import uuid
from pydantic import BaseModel, field_validator
from easyshell_server.auth import AuthType


class SessionRequestSchema(BaseModel):
    client_id: uuid.UUID
    remote_id: uuid.UUID
    auth_type: AuthType
    auth_value: str

    @field_validator("auth_value")
    @classmethod
    def validate_auth_value(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("auth_value must be a non-empty string")
        return v
