import os
import asyncio
from typing import Type, Callable
from functools import wraps

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


app = Sanic("easyshell_api")
app.config.CORS_ORIGINS = "*"
Extend(app)

session_manager = SessionManager()
heartbeat_manager = HeartbeatManager()


def validate_json(model: Type[BaseModel]):
    def decorator(handler: Callable):
        @wraps(handler)
        async def wrapper(request: Request, *args, **kwargs):
            try:
                obj = model.model_validate(request.json)
            except ValidationError as e:
                logger.error(f"Validation error: {e.errors()}")
                return response.json({"error": e.errors()}, status=400)

            # Check if the handler is asynchronous
            return await handler(request, obj, *args, **kwargs)

        return wrapper

    return decorator


@app.post("/heartbeat")
@validate_json(HeartbeatSchema)
async def heartbeat(_: Request, heartbeat: HeartbeatSchema):
    await heartbeat_manager.heartbeat(heartbeat.id, heartbeat.auth_type)
    logger.info(f"Received heartbeat from {heartbeat.id}.")
    return json({"status": "ok"})


@app.get("/devices")
async def get_devices(_):
    logger.info("A client requested devices.")
    devices = await heartbeat_manager.get_heartbeats()
    return json({"devices": devices})


@app.post("/session")
@validate_json(SessionRequestSchema)
async def request_session(request: Request, body: SessionRequestSchema):
    try:
        device_info = await heartbeat_manager.find_by_remote_id(body.remote_id)

        if device_info["auth_type"] != body.auth_type:
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

    websocket_url = f"ws://{request.host}/ws/{session.secret}"

    return json({"session_secret": session.secret, "websocket_url": websocket_url})


@app.websocket("/ws/<session_secret>")
async def websocket_handler(request, ws, session_secret):
    """Handle WebSocket communication."""
    logger.info(f"WebSocket connection established for session {session_secret}.")

    try:
        while True:
            message = await ws.recv()
            logger.info(f"Received message: {message}")
            await ws.send(f"Echo: {message}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info(f"WebSocket connection closed for session {session_secret}.")


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
