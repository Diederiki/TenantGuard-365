"""Alert ops: suppression rules, comments, link-to-case."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.logger import AuditContext, AuditLogger
from app.auth import permissions as P
from app.auth.dependencies import AuthedUser, require
from app.db.models import (
    InvestigationCase,
    InvestigationCaseEvent,
    SecurityAlert,
)
from app.db.session import db_session

router = APIRouter(prefix="/api/security/alerts", tags=["security-ops"])


class CommentIn(BaseModel):
    body: str


class LinkCaseIn(BaseModel):
    case_id: uuid.UUID


class SuppressIn(BaseModel):
    until: datetime | None = None
    reason: str


@router.post("/{alert_id}/comment", summary="Add a comment to an alert")
def add_comment(
    alert_id: uuid.UUID,
    body: CommentIn,
    authed: AuthedUser = Depends(require(P.SECURITY_ALERTS_READ)),
    db: Session = Depends(db_session),
) -> dict[str, Any]:
    alert = db.get(SecurityAlert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="alert_not_found")
    raw_comments = alert.payload.get("comments") or []
    comments: list[dict[str, Any]] = (
        list(raw_comments) if isinstance(raw_comments, list) else []
    )
    comments.append(
        {
            "by": str(authed.user.id),
            "by_display": authed.user.display_name,
            "at": datetime.now(UTC).isoformat(),
            "body": body.body[:5000],
        }
    )
    alert.payload = {**alert.payload, "comments": comments}
    db.flush()
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="alert.comment.added",
        target_type="security_alert",
        target_id=str(alert.id),
        target_label=alert.title,
        new_value={"comment_index": len(comments) - 1},
    )
    db.commit()
    return {"comments": comments}


@router.post(
    "/{alert_id}/link-case", summary="Link an alert to an investigation case"
)
def link_to_case(
    alert_id: uuid.UUID,
    body: LinkCaseIn,
    authed: AuthedUser = Depends(require(P.SECURITY_ALERTS_READ)),
    db: Session = Depends(db_session),
) -> dict[str, Any]:
    alert = db.get(SecurityAlert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="alert_not_found")
    case = db.get(InvestigationCase, body.case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="case_not_found")
    event = InvestigationCaseEvent(
        case_id=case.id,
        kind="alert_link",
        actor_id=authed.user.id,
        payload={"alert_id": str(alert.id), "title": alert.title, "severity": alert.severity},
    )
    db.add(event)
    db.flush()
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="alert.linked_to_case",
        target_type="security_alert",
        target_id=str(alert.id),
        target_label=alert.title,
        new_value={"case_id": str(case.id)},
    )
    db.commit()
    return {"ok": True, "event_id": str(event.id)}


@router.post("/{alert_id}/suppress", summary="Suppress an alert (until / forever)")
def suppress_alert(
    alert_id: uuid.UUID,
    body: SuppressIn,
    authed: AuthedUser = Depends(require(P.SECURITY_ALERTS_READ)),
    db: Session = Depends(db_session),
) -> dict[str, Any]:
    alert = db.get(SecurityAlert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="alert_not_found")
    suppression = {
        "until": body.until.isoformat() if body.until else None,
        "reason": body.reason[:1000],
        "by": str(authed.user.id),
        "at": datetime.now(UTC).isoformat(),
    }
    alert.payload = {**alert.payload, "suppression": suppression}
    alert.status = "false_positive" if body.until is None else alert.status
    db.flush()
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="alert.suppressed",
        target_type="security_alert",
        target_id=str(alert.id),
        target_label=alert.title,
        new_value=suppression,
    )
    db.commit()
    return {"ok": True, "suppression": suppression}


@router.get("/{alert_id}/comments", summary="List comments on an alert")
def list_comments(
    alert_id: uuid.UUID,
    _: AuthedUser = Depends(require(P.SECURITY_ALERTS_READ)),
    db: Session = Depends(db_session),
) -> list[dict[str, Any]]:
    alert = db.get(SecurityAlert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="alert_not_found")
    raw = alert.payload.get("comments") or []
    if not isinstance(raw, list):
        return []
    return [r for r in raw if isinstance(r, dict)]


_ = select  # silence unused
