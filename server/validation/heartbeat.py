import uuid
from auth import AuthType
from pydantic import BaseModel, field_validator


class HeartbeatSchema(BaseModel):
    id: uuid.UUID
    auth_type: AuthType

    @field_validator("auth_type", mode="before")
    @classmethod
    def validate_auth_type(cls, v):
        if not v:
            raise ValueError("auth_type must be a non-empty string")
        return v
