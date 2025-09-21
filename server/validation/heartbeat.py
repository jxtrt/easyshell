import uuid
from dataclasses import dataclass
from auth import AuthType


@dataclass
class HeartbeatSchema:
    id: uuid.UUID
    auth_type: AuthType

    def __post_init__(self):
        try:
            self.id = uuid.UUID(self.id)
        except ValueError:
            raise ValueError(f"Invalid UUID: {self.id}")

        try:
            if not isinstance(self.auth_type, str) or not self.auth_type:
                raise ValueError("auth_type must be a non-empty string")
            self.auth_type = AuthType(self.auth_type)
        except ValueError:
            raise ValueError(f"Unsupported auth type: {self.auth_type}")
