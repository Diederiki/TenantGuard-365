"""Verify built-in security rules register with the expected shape."""

from __future__ import annotations

from app.security.rules import all_rules, get_rule


def test_rules_registered() -> None:
    keys = {r.key for r in all_rules()}
    assert "sharepoint.anonymous_link_present" in keys
    assert "entra.guest_user_active" in keys


def test_severity_values_within_palette() -> None:
    for rule in all_rules():
        assert rule.severity in {"info", "attention", "trouble", "critical"}


def test_get_rule_returns_none_for_unknown() -> None:
    assert get_rule("does.not.exist") is None
