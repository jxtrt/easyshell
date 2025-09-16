import os
from dataclasses import dataclass


class Config:
    HEARTBEAT_INTERVAL = 1
    HEARTBEAT_ENDPOINT = ""
    HEARTBEAT_PORT = 7843

    @classmethod
    def init(cls):
        cls.HEARTBEAT_INTERVAL = int(
            os.getenv("HEARTBEAT_INTERVAL", cls.HEARTBEAT_INTERVAL)
        )
        cls.HEARTBEAT_ENDPOINT = os.getenv("HEARTBEAT_ENDPOINT", cls.HEARTBEAT_ENDPOINT)
        cls.HEARTBEAT_PORT = int(os.getenv("HEARTBEAT_PORT", cls.HEARTBEAT_PORT))
