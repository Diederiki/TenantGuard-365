"""Security posture self-tests.

These assert the platform's defensive defaults stay defensive even as we add
features. Failures here = a regression in the security model.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.remediation import all_handlers
from app.security.rules import all_rules


def test_remediation_policies_ship_disabled() -> None:
    for h in all_handlers():
        assert h.policy.enabled_by_default is False
        assert h.policy.approval_required is True
        assert h.policy.dry_run_default is True


def test_remediation_policy_apply_handlers_are_not_implemented() -> None:
    """Apply handlers must remain stubbed until operator review."""
    import asyncio

    from app.db.models import RemediationAction

    for h in all_handlers():
        action = RemediationAction(  # type: ignore[call-arg]
            tenant_id=None,  # type: ignore[arg-type]
            policy_key=h.policy.key,
            submitter_id=None,  # type: ignore[arg-type]
            target_id="x",
        )
        with pytest.raises(NotImplementedError):
            asyncio.run(h.apply(None, action))  # type: ignore[arg-type]


def test_security_rules_have_recognised_severity() -> None:
    palette = {"info", "attention", "trouble", "critical"}
    for rule in all_rules():
        assert rule.severity in palette


def test_production_refuses_mock_auth() -> None:
    s = Settings(
        environment="production",
        auth_mode="mock",
        dev_session_secret="this-is-a-long-enough-strong-key-1234",
        token_cache_master_key="x" * 32,
    )
    with pytest.raises(RuntimeError):
        s.assert_safe_for_environment()


def test_production_refuses_default_session_secret() -> None:
    s = Settings(
        environment="production",
        auth_mode="entra",
        token_cache_master_key="x" * 32,
    )
    with pytest.raises(RuntimeError):
        s.assert_safe_for_environment()


def test_production_requires_token_cache_master_key() -> None:
    s = Settings(
        environment="production",
        auth_mode="entra",
        dev_session_secret="this-is-a-long-enough-strong-key-1234",
        token_cache_master_key=None,
    )
    with pytest.raises(RuntimeError):
        s.assert_safe_for_environment()


def test_audit_endpoint_requires_auth(client: TestClient) -> None:
    """A request without a session cookie must be 401."""
    r = client.get("/api/audit")
    assert r.status_code == 401


def test_me_endpoint_requires_auth(client: TestClient) -> None:
    r = client.get("/api/me")
    assert r.status_code == 401
