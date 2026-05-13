"""FastAPI dependencies for authn + authz."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.sessions import SessionData, SessionStore, get_session_store
from app.config import get_settings
from app.db.models import (
    PlatformPermission,
    PlatformRoleAssignment,
    PlatformRolePermission,
    PlatformUser,
)
from app.db.session import db_session


@dataclass(slots=True)
class AuthedUser:
    user: PlatformUser
    role_ids: list[uuid.UUID]
    permissions: frozenset[str]
    session: SessionData


def _resolve_permissions(session: Session, user_id: uuid.UUID) -> tuple[list[uuid.UUID], frozenset[str]]:
    role_ids = list(
        session.scalars(
            select(PlatformRoleAssignment.role_id).where(
                PlatformRoleAssignment.user_id == user_id
            )
        )
    )
    if not role_ids:
        return [], frozenset()
    perm_rows = session.execute(
        select(PlatformPermission.key)
        .join(PlatformRolePermission, PlatformRolePermission.permission_id == PlatformPermission.id)
        .where(PlatformRolePermission.role_id.in_(role_ids))
    ).all()
    return role_ids, frozenset(r[0] for r in perm_rows)


def current_user(
    request: Request,
    db: Session = Depends(db_session),
) -> AuthedUser:
    settings = get_settings()
    store: SessionStore = get_session_store()
    signed = request.cookies.get(settings.session_cookie_name)
    if not signed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="no_session")
    sid = store.unsign_sid(signed)
    if sid is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="bad_session_signature")
    data = store.get(sid)
    if data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="session_expired")
    user = db.get(PlatformUser, data.user_id)
    if user is None or not user.is_active:
        store.destroy(sid)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user_inactive")
    store.touch(sid, data)
    role_ids, perms = _resolve_permissions(db, user.id)
    # Stash for audit logger to read from request state.
    request.state.authed_user_id = user.id
    request.state.authed_user_display = user.display_name
    request.state.authed_role_ids = role_ids
    return AuthedUser(user=user, role_ids=role_ids, permissions=perms, session=data)


def require(*needed: str):  # type: ignore[no-untyped-def]
    """Create a dependency that asserts the current user holds every given permission.

    The platform-wide ``platform.admin`` permission is treated as a wildcard.
    """

    def dep(authed: AuthedUser = Depends(current_user)) -> AuthedUser:
        granted = authed.permissions
        if "platform.admin" in granted:
            return authed
        missing = [p for p in needed if p not in granted]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"missing_permissions": missing},
            )
        return authed

    return dep
