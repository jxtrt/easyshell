from dataclasses import dataclass
import uuid
import time
import asyncio

from auth import AuthType


@dataclass
class Session:
    STATUS_PENDING = "PENDING"
    STATUS_CONNECTED = "CONNECTED"
    STATUS_CLOSED = "CLOSED"

    secret: str
    client_id: uuid.UUID
    remote_id: uuid.UUID
    auth_type: AuthType
    auth_value: str
    status: str = STATUS_PENDING
    timestamp: int


class SessionManager:
    def __init__(self):
        self.sessions: list[Session] = {}
        self.session_lock = asyncio.Lock()

    def session_request(
        self,
        client_id: uuid.UUID,
        remote_id: uuid.UUID,
        auth_type: AuthType,
        auth_value: str,
    ):
        session = Session(
            secret=str(uuid.uuid4()),
            client_id=client_id,
            remote_id=remote_id,
            auth_type=auth_type,
            auth_value=auth_value,
            timestamp=int(time.time()),
        )

        with self.session_lock:
            self.sessions[session.secret] = session

        return session

    def cleanup_sessions(self, timeout: int) -> int:
        with self.session_lock:
            now = int(time.time())
            to_delete = [
                s.secret
                for s in self.sessions.values()
                if (now - s.timestamp > timeout)
                and s.status in {Session.STATUS_PENDING, Session.STATUS_CLOSED}
            ]

            for secret in to_delete:
                del self.sessions[secret]

            return len(to_delete)
