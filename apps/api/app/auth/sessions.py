"""Redis-backed session store.

Cookie carries an opaque session ID, signed with `itsdangerous`. The Redis
record holds the actual session payload: who the user is, when the session
started, last activity, IP / UA. Sessions expire by idle timeout AND absolute
timeout.
"""

from __future__ import annotations

import json
import logging
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import redis
from itsdangerous import BadSignature, URLSafeSerializer

from app.config import Settings, get_settings

logger = logging.getLogger("tg365.auth.sessions")

_SESSION_PREFIX = "tg365:session:"


@dataclass(slots=True)
class SessionData:
    user_id: uuid.UUID
    issued_at: datetime
    last_active_at: datetime
    ip: str | None
    user_agent: str | None

    def to_json(self) -> dict[str, Any]:
        return {
            "user_id": str(self.user_id),
            "issued_at": self.issued_at.isoformat(),
            "last_active_at": self.last_active_at.isoformat(),
            "ip": self.ip,
            "user_agent": self.user_agent,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> SessionData:
        return cls(
            user_id=uuid.UUID(data["user_id"]),
            issued_at=datetime.fromisoformat(data["issued_at"]),
            last_active_at=datetime.fromisoformat(data["last_active_at"]),
            ip=data.get("ip"),
            user_agent=data.get("user_agent"),
        )


class SessionStore:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._signer = URLSafeSerializer(self._settings.dev_session_secret, salt="tg365-session")
        self._redis = redis.from_url(self._settings.redis_url)

    # --- cookie helpers ----------------------------------------------------
    def sign_sid(self, sid: str) -> str:
        return self._signer.dumps(sid)  # type: ignore[no-any-return]

    def unsign_sid(self, signed: str) -> str | None:
        try:
            value = self._signer.loads(signed)
        except BadSignature:
            return None
        return value if isinstance(value, str) else None

    # --- lifecycle ---------------------------------------------------------
    def create(
        self,
        *,
        user_id: uuid.UUID,
        ip: str | None,
        user_agent: str | None,
    ) -> tuple[str, SessionData]:
        sid = secrets.token_urlsafe(32)
        now = datetime.now(UTC)
        data = SessionData(
            user_id=user_id,
            issued_at=now,
            last_active_at=now,
            ip=ip,
            user_agent=user_agent,
        )
        self._write(sid, data)
        return sid, data

    def get(self, sid: str) -> SessionData | None:
        raw = self._redis.get(_SESSION_PREFIX + sid)
        if raw is None:
            return None
        if isinstance(raw, bytes):
            raw = raw.decode()
        data = SessionData.from_json(json.loads(raw))
        if self._is_expired(data):
            self.destroy(sid)
            return None
        return data

    def touch(self, sid: str, data: SessionData) -> None:
        data.last_active_at = datetime.now(UTC)
        self._write(sid, data)

    def destroy(self, sid: str) -> None:
        self._redis.delete(_SESSION_PREFIX + sid)

    # --- internals ---------------------------------------------------------
    def _is_expired(self, data: SessionData) -> bool:
        now = datetime.now(UTC)
        idle_limit = timedelta(minutes=self._settings.session_idle_timeout_minutes)
        abs_limit = timedelta(hours=self._settings.session_absolute_timeout_hours)
        if now - data.last_active_at > idle_limit:
            return True
        if now - data.issued_at > abs_limit:
            return True
        return False

    def _write(self, sid: str, data: SessionData) -> None:
        # TTL is the smaller of idle and absolute remaining.
        ttl = max(
            1,
            int(
                min(
                    timedelta(minutes=self._settings.session_idle_timeout_minutes).total_seconds(),
                    (
                        data.issued_at
                        + timedelta(hours=self._settings.session_absolute_timeout_hours)
                        - datetime.now(UTC)
                    ).total_seconds(),
                )
            ),
        )
        self._redis.set(_SESSION_PREFIX + sid, json.dumps(data.to_json()), ex=ttl)


_default: SessionStore | None = None


def get_session_store() -> SessionStore:
    global _default
    if _default is None:
        _default = SessionStore()
    return _default
