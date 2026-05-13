"""/api/security/alerts — list, assign, change status, evaluate-now."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.logger import AuditContext, AuditLogger
from app.auth import permissions as P
from app.auth.dependencies import AuthedUser, require
from app.db.models import SecurityAlert
from app.db.session import db_session
from app.security.engine import evaluate_all

router = APIRouter(prefix="/api/security", tags=["security"])

AlertStatus = Literal["new", "investigating", "resolved", "false_positive"]


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    rule_key: str
    severity: str
    status: str
    title: str
    entity_kind: str | None
    entity_id: str | None
    occurrences: int
    first_seen_at: datetime
    last_seen_at: datetime
    assigned_to: uuid.UUID | None


class AlertPatch(BaseModel):
    status: AlertStatus | None = None
    assigned_to: uuid.UUID | None = None


@router.get("/alerts", response_model=list[AlertOut], summary="List security alerts")
def list_alerts(
    authed: AuthedUser = Depends(require(P.SECURITY_ALERTS_READ)),
    db: Session = Depends(db_session),
    status: AlertStatus | None = Query(default=None),
    severity: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[SecurityAlert]:
    del authed
    stmt = select(SecurityAlert).order_by(SecurityAlert.last_seen_at.desc()).limit(limit)
    if status is not None:
        stmt = stmt.where(SecurityAlert.status == status)
    if severity is not None:
        stmt = stmt.where(SecurityAlert.severity == severity)
    return list(db.scalars(stmt))


@router.patch("/alerts/{alert_id}", response_model=AlertOut)
def patch_alert(
    alert_id: uuid.UUID,
    body: AlertPatch,
    authed: AuthedUser = Depends(require(P.SECURITY_ALERTS_READ)),
    db: Session = Depends(db_session),
) -> SecurityAlert:
    alert = db.get(SecurityAlert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="alert_not_found")
    old = {
        "status": alert.status,
        "assigned_to": str(alert.assigned_to) if alert.assigned_to else None,
    }
    if body.status is not None:
        alert.status = body.status
    if body.assigned_to is not None:
        alert.assigned_to = body.assigned_to
    db.flush()
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="alert.updated",
        target_type="security_alert",
        target_id=str(alert.id),
        target_label=alert.title,
        old_value=old,
        new_value={
            "status": alert.status,
            "assigned_to": str(alert.assigned_to) if alert.assigned_to else None,
        },
    )
    db.commit()
    return alert


@router.post(
    "/rules/evaluate-now",
    summary="Evaluate all enabled rules against the current data snapshot.",
)
def evaluate_now(
    authed: AuthedUser = Depends(require(P.SECURITY_RULES_READ)),
    db: Session = Depends(db_session),
    tenant_id: uuid.UUID = Query(...),
) -> dict[str, Any]:
    counts = evaluate_all(db, tenant_id)
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="security.rules.evaluated",
        new_value={"counts": counts, "tenant_id": str(tenant_id)},
    )
    db.commit()
    return {"counts": counts}
