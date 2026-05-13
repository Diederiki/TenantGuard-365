"""/api/investigations — case CRUD, timeline events, link alerts."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.logger import AuditContext, AuditLogger
from app.auth import permissions as P
from app.auth.dependencies import AuthedUser, require
from app.db.models import InvestigationCase, InvestigationCaseEvent
from app.db.session import db_session

router = APIRouter(prefix="/api/investigations", tags=["investigations"])

CaseStatus = Literal["open", "in_progress", "closed"]
Priority = Literal["low", "medium", "high", "critical"]


class CaseIn(BaseModel):
    tenant_id: uuid.UUID
    title: str
    priority: Priority = "medium"
    summary: str | None = None


class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    title: str
    status: str
    priority: str
    owner_id: uuid.UUID | None
    summary: str | None
    created_at: datetime
    updated_at: datetime


class CasePatch(BaseModel):
    status: CaseStatus | None = None
    priority: Priority | None = None
    summary: str | None = None
    owner_id: uuid.UUID | None = None


class EventIn(BaseModel):
    kind: Literal["note", "evidence", "alert_link", "status_change"]
    payload: dict[str, Any] = {}


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    case_id: uuid.UUID
    kind: str
    actor_id: uuid.UUID | None
    payload: dict[str, Any]
    created_at: datetime


@router.get("", response_model=list[CaseOut], summary="List investigation cases")
def list_cases(
    _: AuthedUser = Depends(require("audit.read")),
    db: Session = Depends(db_session),
    status: CaseStatus | None = None,
) -> list[InvestigationCase]:
    stmt = select(InvestigationCase).order_by(InvestigationCase.updated_at.desc())
    if status is not None:
        stmt = stmt.where(InvestigationCase.status == status)
    return list(db.scalars(stmt))


@router.post("", response_model=CaseOut, summary="Create a case")
def create_case(
    body: CaseIn,
    authed: AuthedUser = Depends(require("audit.read")),
    db: Session = Depends(db_session),
) -> InvestigationCase:
    case = InvestigationCase(
        tenant_id=body.tenant_id,
        title=body.title,
        priority=body.priority,
        owner_id=authed.user.id,
        summary=body.summary,
    )
    db.add(case)
    db.flush()
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="investigation.case.created",
        target_type="investigation_case",
        target_id=str(case.id),
        target_label=case.title,
        new_value={"priority": case.priority},
    )
    db.commit()
    return case


@router.patch("/{case_id}", response_model=CaseOut)
def patch_case(
    case_id: uuid.UUID,
    body: CasePatch,
    authed: AuthedUser = Depends(require("audit.read")),
    db: Session = Depends(db_session),
) -> InvestigationCase:
    case = db.get(InvestigationCase, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="case_not_found")
    old = {
        "status": case.status,
        "priority": case.priority,
        "owner_id": str(case.owner_id) if case.owner_id else None,
    }
    if body.status is not None:
        case.status = body.status
    if body.priority is not None:
        case.priority = body.priority
    if body.summary is not None:
        case.summary = body.summary
    if body.owner_id is not None:
        case.owner_id = body.owner_id
    db.flush()
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="investigation.case.updated",
        target_type="investigation_case",
        target_id=str(case.id),
        target_label=case.title,
        old_value=old,
        new_value={
            "status": case.status,
            "priority": case.priority,
            "owner_id": str(case.owner_id) if case.owner_id else None,
        },
    )
    db.commit()
    return case


@router.get(
    "/{case_id}/events",
    response_model=list[EventOut],
    summary="Timeline events for a case",
)
def list_events(
    case_id: uuid.UUID,
    _: AuthedUser = Depends(require("audit.read")),
    db: Session = Depends(db_session),
) -> list[InvestigationCaseEvent]:
    return list(
        db.scalars(
            select(InvestigationCaseEvent)
            .where(InvestigationCaseEvent.case_id == case_id)
            .order_by(InvestigationCaseEvent.created_at.asc())
        )
    )


@router.post("/{case_id}/events", response_model=EventOut)
def add_event(
    case_id: uuid.UUID,
    body: EventIn,
    authed: AuthedUser = Depends(require("audit.read")),
    db: Session = Depends(db_session),
) -> InvestigationCaseEvent:
    case = db.get(InvestigationCase, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="case_not_found")
    event = InvestigationCaseEvent(
        case_id=case_id,
        kind=body.kind,
        actor_id=authed.user.id,
        payload=body.payload,
    )
    db.add(event)
    db.flush()
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="investigation.case.event.added",
        target_type="investigation_case",
        target_id=str(case.id),
        target_label=case.title,
        new_value={"kind": body.kind},
    )
    db.commit()
    return event
