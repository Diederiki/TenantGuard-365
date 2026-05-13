"""/api/audit — paginated technician audit log viewer."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import permissions as P
from app.auth.dependencies import AuthedUser, require
from app.db.models import TechnicianAuditLog
from app.db.session import db_session
from app.schemas.audit import AuditEntry, AuditPage

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=AuditPage, summary="List audit entries (newest first)")
def list_audit(
    authed: AuthedUser = Depends(require(P.AUDIT_READ)),
    db: Session = Depends(db_session),
    limit: int = Query(default=50, ge=1, le=500),
    before_id: int | None = Query(default=None, description="opaque cursor; pass prior page's next_cursor"),
    action: str | None = Query(default=None),
) -> AuditPage:
    del authed  # used by the dependency only; reference to silence unused-arg lint
    stmt = select(TechnicianAuditLog).order_by(TechnicianAuditLog.id.desc()).limit(limit + 1)
    if before_id is not None:
        stmt = stmt.where(TechnicianAuditLog.id < before_id)
    if action:
        stmt = stmt.where(TechnicianAuditLog.action == action)
    rows = list(db.scalars(stmt))
    next_cursor = rows[-1].id if len(rows) > limit else None
    items = [AuditEntry.model_validate(r) for r in rows[:limit]]
    return AuditPage(items=items, next_cursor=next_cursor)
