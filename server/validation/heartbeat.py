import uuid
from dataclasses import dataclass

@dataclass
class HeartbeatSchema:
    id: str
    auth: str

    def __post_init__(self):
        try:
            uuid.UUID(self.id)
        except ValueError:
            raise ValueError(f"Invalid UUID: {self.id}")
        
        if not isinstance(self.auth, str) or not self.auth:
            raise ValueError("Auth must be a non-empty string")