"""/api/rbac — platform users, roles, permissions admin API."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.logger import AuditContext, AuditLogger
from app.auth import permissions as P
from app.auth.dependencies import AuthedUser, require
from app.db.models import (
    PlatformPermission,
    PlatformRole,
    PlatformRoleAssignment,
    PlatformRolePermission,
    PlatformUser,
)
from app.db.session import db_session

router = APIRouter(prefix="/api/rbac", tags=["rbac"])


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    display_name: str
    is_active: bool
    is_system: bool
    created_at: datetime


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    key: str
    display_name: str
    description: str
    is_builtin: bool


class PermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    key: str
    description: str
    category: str


class AssignmentIn(BaseModel):
    user_id: uuid.UUID
    role_key: str
    scope: str = ""


class AssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    role_id: uuid.UUID
    scope: str


@router.get("/users", response_model=list[UserOut])
def list_users(
    _: AuthedUser = Depends(require(P.PLATFORM_USERS_READ)),
    db: Session = Depends(db_session),
) -> list[PlatformUser]:
    return list(db.scalars(select(PlatformUser).order_by(PlatformUser.email)))


@router.get("/roles", response_model=list[RoleOut])
def list_roles(
    _: AuthedUser = Depends(require(P.PLATFORM_ROLES_READ)),
    db: Session = Depends(db_session),
) -> list[PlatformRole]:
    return list(db.scalars(select(PlatformRole).order_by(PlatformRole.key)))


@router.get("/roles/{role_key}/permissions", response_model=list[PermissionOut])
def role_permissions(
    role_key: str,
    _: AuthedUser = Depends(require(P.PLATFORM_ROLES_READ)),
    db: Session = Depends(db_session),
) -> list[PlatformPermission]:
    role = db.scalar(select(PlatformRole).where(PlatformRole.key == role_key))
    if role is None:
        raise HTTPException(status_code=404, detail="role_not_found")
    rows = db.execute(
        select(PlatformPermission)
        .join(
            PlatformRolePermission,
            PlatformRolePermission.permission_id == PlatformPermission.id,
        )
        .where(PlatformRolePermission.role_id == role.id)
        .order_by(PlatformPermission.key)
    ).scalars()
    return list(rows)


@router.get("/permissions", response_model=list[PermissionOut])
def list_permissions(
    _: AuthedUser = Depends(require(P.PLATFORM_ROLES_READ)),
    db: Session = Depends(db_session),
) -> list[PlatformPermission]:
    return list(
        db.scalars(
            select(PlatformPermission).order_by(
                PlatformPermission.category, PlatformPermission.key
            )
        )
    )


@router.post("/assignments", response_model=AssignmentOut)
def add_assignment(
    body: AssignmentIn,
    authed: AuthedUser = Depends(require(P.PLATFORM_USERS_MANAGE)),
    db: Session = Depends(db_session),
) -> PlatformRoleAssignment:
    user = db.get(PlatformUser, body.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    role = db.scalar(select(PlatformRole).where(PlatformRole.key == body.role_key))
    if role is None:
        raise HTTPException(status_code=404, detail="role_not_found")
    existing = db.scalar(
        select(PlatformRoleAssignment).where(
            PlatformRoleAssignment.user_id == user.id,
            PlatformRoleAssignment.role_id == role.id,
            PlatformRoleAssignment.scope == body.scope,
        )
    )
    if existing is not None:
        return existing
    a = PlatformRoleAssignment(user_id=user.id, role_id=role.id, scope=body.scope)
    db.add(a)
    db.flush()
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="rbac.assignment.added",
        target_type="platform_user",
        target_id=str(user.id),
        target_label=user.email,
        new_value={"role": role.key, "scope": body.scope},
    )
    db.commit()
    return a


@router.delete("/assignments/{assignment_id}")
def remove_assignment(
    assignment_id: uuid.UUID,
    authed: AuthedUser = Depends(require(P.PLATFORM_USERS_MANAGE)),
    db: Session = Depends(db_session),
) -> dict[str, Any]:
    a = db.get(PlatformRoleAssignment, assignment_id)
    if a is None:
        raise HTTPException(status_code=404, detail="assignment_not_found")
    record = {"user_id": str(a.user_id), "role_id": str(a.role_id), "scope": a.scope}
    db.delete(a)
    db.flush()
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="rbac.assignment.removed",
        target_type="platform_role_assignment",
        target_id=str(assignment_id),
        old_value=record,
    )
    db.commit()
    return {"ok": True}
