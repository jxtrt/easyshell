import time
import os
import asyncio

from dotenv import load_dotenv
from sanic import Sanic, Request
from sanic.response import json
from sanic.log import logger
from sanic.worker.manager import WorkerManager

from sanic_ext import validate

from threading import Lock

from validation.heartbeat import HeartbeatSchema
from helpers import is_device_still_alive

app = Sanic("easyshell_api")

heartbeats = {}
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
    with heartbeat_lock:
        devices = []
        for device_id, info in heartbeats.items():
            if is_device_still_alive(info["timestamp"]):
                devices.append(
                    {
                        "id": device_id,
                        "auth": info["auth"],
                        "timestamp": info["timestamp"],
                    }
                )

    return json({"devices": devices})


# @app.main_process_ready
# async def ready(app: Sanic, _):
#     app.manager.manage("Cleanup", cleanup_heartbeats, {"timeout": int(os.getenv("HEARTBEAT_TIMEOUT", 60))})


@app.after_server_start
async def setup_cleanup(app, _):
    async def cleanup_task():
        timeout = int(os.getenv("HEARTBEAT_TIMEOUT", 60))
        while True:
            cleanup_heartbeats(timeout=timeout)
            await asyncio.sleep(timeout)  # run every <timeout> seconds

    app.add_task(cleanup_task())


if __name__ == "__main__":
    load_dotenv()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 7843)))
