"""Mock authentication for local development.

Refuses to operate when ``ENVIRONMENT=production``. Lets the operator
sign in as any seeded ``platform_users`` row by email.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import PlatformUser


def assert_mock_auth_allowed() -> None:
    settings = get_settings()
    if settings.environment == "production":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="mock_auth_disabled_in_production",
        )
    if settings.auth_mode != "mock":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="mock_auth_not_enabled",
        )


def resolve_mock_user(session: Session, email: str) -> PlatformUser:
    user = session.scalar(select(PlatformUser).where(PlatformUser.email == email))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user_not_found")
    return user
