"""/api/me — return the current user, roles, and resolved permissions."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import AuthedUser, current_user
from app.db.models import PlatformRole
from app.db.session import db_session
from app.schemas.user import UserMe

router = APIRouter(prefix="/api", tags=["me"])


@router.get("/me", response_model=UserMe, summary="Current platform user")
def get_me(
    authed: AuthedUser = Depends(current_user),
    db: Session = Depends(db_session),
) -> UserMe:
    role_keys: list[str] = []
    if authed.role_ids:
        role_keys = list(
            db.scalars(select(PlatformRole.key).where(PlatformRole.id.in_(authed.role_ids)))
        )
    return UserMe(
        id=authed.user.id,
        email=authed.user.email,
        display_name=authed.user.display_name,
        is_active=authed.user.is_active,
        role_keys=sorted(role_keys),
        permissions=sorted(authed.permissions),
    )
