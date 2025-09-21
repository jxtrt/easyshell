import time
import os
import asyncio

from dotenv import load_dotenv
from sanic import Sanic, Request
from sanic.response import json
from sanic.log import logger

from sanic_ext import Extend, validate

from threading import Lock

from validation.heartbeat import HeartbeatSchema
from validation.session_request import SessionRequestSchema
from session_manager import SessionManager


app = Sanic("easyshell_api")
app.config.CORS_ORIGINS = "*"
Extend(app)

heartbeats = {}
heartbeat_lock = Lock()

session_manager = SessionManager()


def cleanup_heartbeats(timeout=60):
    """Remove heartbeats older than the timeout."""
    current_time = int(time.time())
    with heartbeat_lock:
        to_delete = [
            device_id
            for device_id, info in heartbeats.items()
            if current_time - info["timestamp"] > timeout
        ]
        for device_id in to_delete:
            del heartbeats[device_id]

    logger.info(f"Cleaned up {len(to_delete)} heartbeats.")
    return len(to_delete)


@app.post("/heartbeat")
@validate(json=HeartbeatSchema)
def heartbeat(_: Request, body: HeartbeatSchema):
    with heartbeat_lock:
        heartbeats[body.id] = {
            "auth": body.auth,
            "timestamp": int(time.time()),
        }

    logger.info(f"Received heartbeat from {body.id}.")

    return json({"status": "ok"})


@app.get("/devices")
def get_devices(_):
    with heartbeat_lock:
        devices = []
        for device_id, info in heartbeats.items():
            devices.append(
                {
                    "id": device_id,
                    "auth": info["auth"],
                    "timestamp": info["timestamp"],
                }
            )

    return json({"devices": devices})


@app.post("/session")
def request_session(_: Request, body: SessionRequestSchema):
    try:
        with heartbeat_lock:
            if body.target_id not in heartbeats:
                return json({"error": "Device offline."}, status=404)

            device_info = heartbeats[body.target_id]

            if device_info["auth"] != body.auth_type:
                return json({"error": "Auth type mismatch."}, status=400)

    except ValueError as e:
        return json({"error": str(e)}, status=400)

    logger.info(
        f"Accepting session request from device {body.client_id} to remote {body.remote_id}."
    )

    session_manager.session_request(
        client_id=body.client_id,
        remote_id=body.remote_id,
        auth_type=body.auth_type,
        auth_value=body.auth_value,
    )

    session_token = "session_token_example"

    return json({"session_token": session_token})


@app.after_server_start
async def setup_cleanup(app, _):
    async def cleanup_task():
        heartbeat_timeout = int(os.getenv("HEARTBEAT_TIMEOUT", 60))
        stale_session_timeout = int(os.getenv("SESSION_TIMEOUT", 300))

        while True:
            logger.info(
                "Cleaned up %s heartbeats.", cleanup_heartbeats(timeout=heartbeat_timeout)
            )

            logger.info(
                "Cleaned up %s stale sessions.",
                session_manager.cleanup_sessions(timeout=stale_session_timeout),
            )

            await asyncio.sleep(60)

    app.add_task(cleanup_task())


if __name__ == "__main__":
    load_dotenv()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 7843)))
