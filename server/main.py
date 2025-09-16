import time

from sanic import Sanic
from sanic.response import json
from sanic_ext import validate

from threading import Lock

from server.validation.heartbeat import HeartbeatSchema
from server.helpers import is_device_still_alive

app = Sanic("easyshell_api")

heartbeats = {}
heartbeat_lock = Lock()

@app.post("/heartbeat")
@validate(_, json=HeartbeatSchema)
def heartbeat(body: HeartbeatSchema):
    with heartbeat_lock:
        heartbeats[body.id] = {
            "auth": body.auth,
            "timestamp": time.time(),
        }

    return json({"status": "ok"})

@app.get("/devices")
def get_devices(_):
    with heartbeat_lock:
        devices = []
        for device_id, info in heartbeats.items():
            if is_device_still_alive(info["timestamp"]):
                devices.append({
                    "id": device_id,
                    "auth": info["auth"],
                    "timestamp": info["timestamp"],
                })

    return json({"devices": devices})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)