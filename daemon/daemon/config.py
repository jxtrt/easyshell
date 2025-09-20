import os
from dataclasses import dataclass


class Config:
    HEARTBEAT_INTERVAL = 30
    HEARTBEAT_ENDPOINT = ""
    HEARTBEAT_PORT = 7843
    FORCED_SHELL = None
    INSTANCE_ID = ""

    @classmethod
    def init(cls):
        cls.HEARTBEAT_INTERVAL = int(
            os.getenv("HEARTBEAT_INTERVAL", cls.HEARTBEAT_INTERVAL)
        )
        cls.HEARTBEAT_ENDPOINT = os.getenv("HEARTBEAT_ENDPOINT", cls.HEARTBEAT_ENDPOINT)
        cls.HEARTBEAT_PORT = int(os.getenv("HEARTBEAT_PORT", cls.HEARTBEAT_PORT))
        cls.FORCED_SHELL = os.getenv("FORCED_SHELL", cls.FORCED_SHELL)
        cls.INSTANCE_ID = UUID = os.getenv("INSTANCE_ID") 