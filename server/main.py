import os
import asyncio
from typing import Type, Callable
from functools import wraps
from collections import defaultdict

from dotenv import load_dotenv
from sanic import Sanic, Request, response
from sanic.response import json
from sanic.log import logger

from sanic_ext import Extend

from pydantic import BaseModel, ValidationError

from easyshell_server.validation.heartbeat import HeartbeatSchema
from easyshell_server.validation.session_request import SessionRequestSchema
from easyshell_server.session_manager import SessionManager
from easyshell_server.heartbeat_manager import HeartbeatManager

RESPONSE_STATUS_NOP = "nop"
RESPONSE_STATUS_STOP = "stop"
RESPONSE_STATUS_SHELL_REQUEST = "shell_request"

app = Sanic("easyshell_api")
app.config.CORS_ORIGINS = "*"
Extend(app)

session_manager = SessionManager()
heartbeat_manager = HeartbeatManager()

ws_connections = defaultdict(dict)  # session_secret -> {"client": ws, "daemon": ws}
session_url_template = "ws://{host}/ws/{client_or_daemon}/{session_secret}"

def validate_json(model: Type[BaseModel]):
    def decorator(handler: Callable):
        @wraps(handler)
        async def wrapper(request: Request, *args, **kwargs):
            try:
                obj = model.model_validate(request.json)
            except ValidationError as e:
                logger.error(f"Validation error: {e.errors()}")
                return response.json({"error": e.errors()}, status=400)

            return await handler(request, obj, *args, **kwargs)
        return wrapper
    return decorator


@app.post("/heartbeat")
@validate_json(HeartbeatSchema)
async def heartbeat(request: Request, heartbeat: HeartbeatSchema):
    await heartbeat_manager.heartbeat(heartbeat.id, heartbeat.auth_type)
    logger.info(f"Received heartbeat from {heartbeat.id}.")

    is_there_pending_session = await session_manager.remote_has_pending_session(heartbeat.id)
    if is_there_pending_session:
        logger.info(f"Pending session request for {heartbeat.id}.")
        session = await session_manager.get_session_by_remote_id(heartbeat.id)
        return json({
            "status": RESPONSE_STATUS_SHELL_REQUEST,
            "ws_url": session_url_template.format(
                host=request.headers.get("host", "localhost"),
                client_or_daemon="daemon",
                session_secret=session.secret,
            )
        })
    
    return json({"status": RESPONSE_STATUS_NOP})


@app.get("/devices")
async def get_devices(_):
    logger.info("A client requested devices.")
    devices = await heartbeat_manager.get_heartbeats()
    return json({"devices": devices})


@app.post("/session")
@validate_json(SessionRequestSchema)
async def request_session(request: Request, body: SessionRequestSchema):
    try:
        existing_session = await heartbeat_manager.find_by_remote_id(body.remote_id)

        if existing_session.auth_type != body.auth_type:
            return json({"error": "Auth type mismatch."}, status=400)

    except ValueError as e:
        return json({"error": str(e)}, status=400)

    logger.info(
        f"Accepting session request from device {body.client_id} to remote {body.remote_id}."
    )

    session = await session_manager.session_request(
        client_id=body.client_id,
        remote_id=body.remote_id,
        auth_type=body.auth_type,
        auth_value=body.auth_value,
    )

    client_websocket_url = session_url_template.format(
        host=request.headers.get("host", "localhost"),
        client_or_daemon="client",
        session_secret=session.secret,
    )

    return json({
        "session_secret": session.secret, 
        "websocket_url": client_websocket_url
    })


@app.websocket("/ws/client/<session_secret>")
async def client_websocket_handler(request, ws, session_secret):
    """Handle websocket communication for the client."""
    logger.info(f"Websocket connection established with a client, for session {session_secret}.")
    try:
        session = await session_manager.get_session(session_secret)
        if not session:
            logger.error(f"No session found for secret {session_secret}. Closing connection.")
            await ws.close()
            return

        ws_connections[session_secret]["client"] = ws

        while True:
            data = await ws.recv()
            if "daemon" in ws_connections[session_secret]:
                await ws_connections[session_secret]["daemon"].send(data)
            else:
                logger.warning(f"No daemon connected for session {session_secret}.")

    except Exception as e:
        logger.error(f"Error in client websocket: {e}")
    finally:
        logger.info(f"Client disconnected. Closing session {session_secret}.")
        await session_manager.close_session(session_secret)
        ws_connections.get(session_secret, {}).pop("client", None)
        if "daemon" in ws_connections.get(session_secret, {}):
            print("C")
            try:
                await ws_connections[session_secret]["daemon"].close()
                logger.info(f"Closed daemon connection for {session_secret}.")
            except Exception as e:
                logger.error(f"Error closing daemon websocket: {e}")
            ws_connections[session_secret].pop("daemon", None)

@app.websocket("/ws/daemon/<session_secret>")
async def daemon_websocket_handler(request, ws, session_secret):
    """Handle websocket communication for the daemon."""
    logger.info(f"Websocket connection established with a daemon, for session {session_secret}.")

    try:
        session = await session_manager.start_session(session_secret)
        if not session:
            logger.error(f"No session found for secret {session_secret}. Closing connection.")
            await ws.close()
            return

        ws_connections[session_secret]["daemon"] = ws

        while True:
            data = await ws.recv()
            print("AAAAAA")
            print(data)
            if "client" in ws_connections[session_secret]:
                await ws_connections[session_secret]["client"].send(data)
            else:
                logger.warning(f"No client connected for session {session_secret}.")

    except Exception as e:
        logger.error(f"Error in daemon websocket: {e}")
    finally:
        logger.info(f"Daemon disconnected. Closing session {session_secret}.")
        await session_manager.close_session(session_secret)
        ws_connections.get(session_secret, {}).pop("daemon", None)

        if "client" in ws_connections.get(session_secret, {}):
            try:
                await ws_connections[session_secret]["client"].close()
                logger.info(f"Closed client connection for {session_secret}.")
            except Exception as e:
                logger.error(f"Error closing client websocket: {e}")
            ws_connections[session_secret].pop("client", None)


@app.after_server_start
async def setup_cleanup(app, _):
    async def cleanup_task():
        heartbeat_timeout = int(os.getenv("HEARTBEAT_TIMEOUT", 60))
        stale_session_timeout = int(os.getenv("SESSION_TIMEOUT", 300))

        while True:
            n_heartbeats = await heartbeat_manager.cleanup_heartbeats(
                timeout=heartbeat_timeout
            )
            logger.info("Cleaned up %s heartbeats.", n_heartbeats)

            n_sessions = await session_manager.cleanup_sessions(
                timeout=stale_session_timeout
            )
            logger.info(
                "Cleaned up %s stale sessions.",
                n_sessions,
            )

            await asyncio.sleep(60)

    app.add_task(cleanup_task())


if __name__ == "__main__":
    load_dotenv()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 7843)))
