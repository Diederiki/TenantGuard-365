"""Tests for the RBAC `require()` dependency factory.

We exercise it directly with synthetic AuthedUser values so we don't need a DB.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import pytest
from fastapi import HTTPException

from app.auth.dependencies import AuthedUser, require
from app.auth.sessions import SessionData


@dataclass
class _StubUser:
    id: uuid.UUID
    email: str = "stub@example.com"
    display_name: str = "Stub"
    is_active: bool = True


def _authed(*perms: str) -> AuthedUser:
    user = _StubUser(id=uuid.uuid4())
    from datetime import UTC, datetime

    return AuthedUser(
        user=user,  # type: ignore[arg-type]
        role_ids=[],
        permissions=frozenset(perms),
        session=SessionData(
            user_id=user.id,
            issued_at=datetime.now(UTC),
            last_active_at=datetime.now(UTC),
            ip=None,
            user_agent=None,
        ),
    )


def test_require_allows_when_permission_granted() -> None:
    dep = require("audit.read")
    result = dep(authed=_authed("audit.read"))
    assert result.permissions == frozenset({"audit.read"})


def test_require_admin_wildcard_allows_anything() -> None:
    dep = require("audit.read", "remediation.execute")
    result = dep(authed=_authed("platform.admin"))
    assert result is not None


def test_require_rejects_when_missing() -> None:
    dep = require("audit.read")
    with pytest.raises(HTTPException) as exc:
        dep(authed=_authed("reports.read"))
    assert exc.value.status_code == 403
    assert "audit.read" in exc.value.detail["missing_permissions"]


def test_require_rejects_partial_match() -> None:
    dep = require("audit.read", "audit.read.raw")
    with pytest.raises(HTTPException) as exc:
        dep(authed=_authed("audit.read"))
    assert "audit.read.raw" in exc.value.detail["missing_permissions"]
