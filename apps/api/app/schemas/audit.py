"""Audit log DTOs."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: uuid.UUID | None
    actor_id: uuid.UUID | None
    actor_display: str
    actor_type: str
    action: str
    target_type: str | None
    target_id: str | None
    target_label: str | None
    result: str
    event_time: datetime


class AuditPage(BaseModel):
    items: list[AuditEntry]
    next_cursor: int | None
