from dataclasses import dataclass
import uuid
import time
import asyncio

from easyshell_server.auth import AuthType


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
    timestamp: int
    status: str = STATUS_PENDING


class SessionManager:
    def __init__(self):
        self.sessions: dict[Session] = {}
        self.session_lock = asyncio.Lock()

    async def session_request(
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

        async with self.session_lock:
            self.sessions[session.secret] = session

        return session

    async def cleanup_sessions(self, timeout: int = 60) -> int:
        async with self.session_lock:
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
        
    async def remote_has_pending_session(self, heartbeat_id: uuid.UUID) -> bool:
        async with self.session_lock:
            for session in self.sessions.values():
                if session.remote_id == heartbeat_id and session.status == Session.STATUS_PENDING:
                    return True
            return False
        
    async def get_session_by_remote_id(self, remote_id: uuid.UUID):
        async with self.session_lock:
            for session in self.sessions.values():
                if session.remote_id == remote_id and session.status == Session.STATUS_PENDING:
                    return session
            return None
        
    async def start_session(self, secret: str):
        async with self.session_lock:
            session = self.sessions.get(secret)
            if session:
                session.status = Session.STATUS_CONNECTED
                session.timestamp = int(time.time())
                return session
            return None

    async def close_session(self, secret: str):
        async with self.session_lock:
            session = self.sessions.get(secret)
            if session:
                session.status = Session.STATUS_CLOSED
                session.timestamp = int(time.time())
                return session
            return None
        
    async def get_session(self, secret: str):
        async with self.session_lock:
            return self.sessions.get(secret)