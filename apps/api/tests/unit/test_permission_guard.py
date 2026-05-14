"""Unit tests for the privilege-escalation guard helper."""

from __future__ import annotations

from app.auth.permissions import (
    PLATFORM_ADMIN,
    PLATFORM_USERS_MANAGE,
    REPORTS_READ,
    REPORTS_RUN,
    caller_can_grant_role,
)


def test_subset_grant_allowed() -> None:
    caller = {REPORTS_READ, REPORTS_RUN, PLATFORM_USERS_MANAGE}
    role = {REPORTS_READ}
    assert caller_can_grant_role(caller, role) is True


def test_superset_grant_denied() -> None:
    caller = {REPORTS_READ}
    role = {REPORTS_READ, REPORTS_RUN}
    assert caller_can_grant_role(caller, role) is False


def test_disjoint_grant_denied() -> None:
    caller = {REPORTS_READ}
    role = {PLATFORM_USERS_MANAGE}
    assert caller_can_grant_role(caller, role) is False


def test_empty_role_always_allowed() -> None:
    """An empty role grants no privileges; anyone can assign it."""
    assert caller_can_grant_role(set(), set()) is True
    assert caller_can_grant_role({REPORTS_READ}, set()) is True


def test_platform_admin_can_grant_anything() -> None:
    caller = {PLATFORM_ADMIN}
    role = {REPORTS_READ, REPORTS_RUN, PLATFORM_USERS_MANAGE, "some.future.perm"}
    assert caller_can_grant_role(caller, role) is True


def test_non_admin_cannot_grant_admin() -> None:
    caller = {PLATFORM_USERS_MANAGE, REPORTS_READ}
    role = {PLATFORM_ADMIN}
    assert caller_can_grant_role(caller, role) is False
