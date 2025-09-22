import time
import uuid
import asyncio
from dataclasses import dataclass, field

from easyshell_server.auth import AuthType


@dataclass
class Heartbeat:
    client_id: uuid.UUID
    auth_type: AuthType
    timestamp: int = field(default_factory=lambda: int(time.time()))


class HeartbeatManager:
    def __init__(self):
        self.heartbeats: dict[uuid.UUID, Heartbeat] = {}
        self.heartbeat_lock: asyncio.Lock = asyncio.Lock()

    async def heartbeat(self, client_id: str, auth_type: AuthType):
        hb = Heartbeat(client_id=client_id, auth_type=auth_type)
        async with self.heartbeat_lock:
            self.heartbeats[client_id] = hb

    async def cleanup_heartbeats(self, timeout: int = 60):
        """Remove heartbeats older than the timeout."""
        current_time = int(time.time())
        async with self.heartbeat_lock:
            to_delete = [
                device_id
                for device_id, obj in self.heartbeats.items()
                if current_time - obj.timestamp > timeout
            ]
            for device_id in to_delete:
                del self.heartbeats[device_id]

        return len(to_delete)

    async def get_heartbeats(self):
        async with self.heartbeat_lock:
            devices = []
            for device_id, obj in self.heartbeats.items():
                devices.append(
                    {
                        "id": str(device_id),
                        "auth_type": obj.auth_type.value,
                        "timestamp": obj.timestamp,
                    }
                )
            return devices

    async def find_by_remote_id(self, remote_id: uuid.UUID):
        async with self.heartbeat_lock:
            if remote_id not in self.heartbeats:
                raise ValueError("Device not found.")
            return self.heartbeats[remote_id]
