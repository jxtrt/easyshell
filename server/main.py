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
from auth import AuthType

app = Sanic("easyshell_api")
app.config.CORS_ORIGINS = "*"
Extend(app)

heartbeats = {}
session_requests = {}

heartbeat_lock = Lock()

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


@app.post("/heartbeat")
@validate(json=HeartbeatSchema)
def heartbeat(_: Request, body: HeartbeatSchema):
    with heartbeat_lock:
        heartbeats[body.id] = {
            "auth": body.auth,
            "timestamp": int(time.time()),
        }

    logger.info(f"Received heartbeat from {body.id}")

    return json({"status": "ok"})


@app.get("/devices")
def get_devices(_):
    logger.info("Fetching devices.")
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
    device_id = body.id
    otp_code = body.auth_value
    requested_auth_type = body.auth_type

    try:
        with heartbeat_lock:
            if device_id not in heartbeats:
                return json({"error": "Device not found or offline."}, status=404)

            device_info = heartbeats[device_id]
            
            if device_info["auth"] != requested_auth_type:
                return json({"error": "Auth type mismatch."}, status=400)
        
    except ValueError as e:
        return json({"error": str(e)}, status=400)

    # Here you would implement the logic to request a session from the device.
    # This is a placeholder implementation.
    logger.info(f"Requesting session from device {device_id} with OTP code {otp_code}")

    # Simulate session creation
    session_token = "session_token_example"

    return json({"session_token": session_token})
    

@app.after_server_start
async def setup_cleanup(app, _):
    async def cleanup_task():
        timeout = int(os.getenv("HEARTBEAT_TIMEOUT", 60))
        while True:
            how_many = cleanup_heartbeats(timeout=timeout)

            logger.info("Cleaned up %s heartbeats.", how_many)

            await asyncio.sleep(timeout)  # run every <timeout> seconds

    app.add_task(cleanup_task())


if __name__ == "__main__":
    load_dotenv()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 7843)))
