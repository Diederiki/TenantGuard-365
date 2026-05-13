"""AuditLogger — the only path through which technician_audit_logs rows are written.

The database also enforces append-only via a trigger (see baseline migration).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import TechnicianAuditLog

logger = logging.getLogger("tg365.audit")


@dataclass(slots=True)
class AuditContext:
    """Context for a single audit record. Most fields come from the request."""

    actor_id: uuid.UUID | None
    actor_display: str
    actor_type: str = "user"
    actor_role_ids: list[uuid.UUID] = field(default_factory=list)
    tenant_id: uuid.UUID | None = None
    ip: str | None = None
    user_agent: str | None = None
    correlation_id: uuid.UUID | None = None
    request_id: uuid.UUID | None = None


def _payload_hash(record: dict[str, Any]) -> bytes:
    settings = get_settings()
    canonical = json.dumps(record, sort_keys=True, default=str).encode("utf-8")
    key = settings.dev_session_secret.encode("utf-8")
    return hmac.new(key, canonical, hashlib.sha256).digest()


class AuditLogger:
    def __init__(self, db: Session) -> None:
        self._db = db

    def log(
        self,
        ctx: AuditContext,
        *,
        action: str,
        target_type: str | None = None,
        target_id: str | None = None,
        target_label: str | None = None,
        old_value: dict[str, Any] | None = None,
        new_value: dict[str, Any] | None = None,
        result: str = "success",
        failure_reason: str | None = None,
    ) -> TechnicianAuditLog:
        record_dict = {
            "action": action,
            "actor_id": ctx.actor_id,
            "actor_display": ctx.actor_display,
            "actor_type": ctx.actor_type,
            "actor_role_ids": ctx.actor_role_ids,
            "tenant_id": ctx.tenant_id,
            "target_type": target_type,
            "target_id": target_id,
            "target_label": target_label,
            "old_value": old_value,
            "new_value": new_value,
            "result": result,
            "failure_reason": failure_reason,
            "ip": ctx.ip,
            "user_agent": ctx.user_agent,
            "correlation_id": str(ctx.correlation_id) if ctx.correlation_id else None,
            "request_id": str(ctx.request_id) if ctx.request_id else None,
            "event_time": datetime.now(UTC).isoformat(),
        }
        row = TechnicianAuditLog(
            tenant_id=ctx.tenant_id,
            actor_id=ctx.actor_id,
            actor_display=ctx.actor_display,
            actor_type=ctx.actor_type,
            actor_role_ids=ctx.actor_role_ids,
            action=action,
            target_type=target_type,
            target_id=target_id,
            target_label=target_label,
            old_value=old_value,
            new_value=new_value,
            result=result,
            failure_reason=failure_reason,
            ip=ctx.ip,
            user_agent=ctx.user_agent,
            correlation_id=ctx.correlation_id,
            request_id=ctx.request_id,
            payload_hash=_payload_hash(record_dict),
            event_time=datetime.now(UTC),
        )
        self._db.add(row)
        self._db.flush()
        logger.info("audit.record.written", extra={"action": action, "actor": ctx.actor_display})
        return row
