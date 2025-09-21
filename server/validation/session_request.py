import uuid
from dataclasses import dataclass
from auth import AuthType

@dataclass
class SessionRequestSchema:
    client_id: uuid.UUID
    target_id: uuid.UUID
    auth_type: AuthType
    auth_value: str

    def __post_init__(self):
        try:
            self.target_id = uuid.UUID(self.target_id)
        except ValueError:
            raise ValueError(f"Invalid UUID: {self.target_id}")
        
        try:
            self.client_id = uuid.UUID(self.client_id)
        except ValueError:
            raise ValueError(f"Invalid UUID: {self.client_id}")

        try:
            if not isinstance(self.auth_type, str) or not self.auth_type:
                raise ValueError("Auth type must be a non-empty string")
            self.auth_type = AuthType(self.auth_type)
        except ValueError:
            raise ValueError(f"Unsupported auth type: {self.auth_type}")
        
        if not isinstance(self.auth_value, str) or not self.auth_value:
            raise ValueError("Auth value must be a non-empty string")