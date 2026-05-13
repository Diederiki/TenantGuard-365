"""Collector registry smoke."""

from __future__ import annotations

from app.collectors import all_collectors, get_collector


def test_registry_has_expected_collectors() -> None:
    keys = {c.manifest.key for c in all_collectors()}
    assert {"entra.users", "sharepoint.sites", "serviceHealth.snapshot"}.issubset(keys)


def test_each_collector_declares_required_scopes() -> None:
    for c in all_collectors():
        assert isinstance(c.manifest.required_scopes, list)
        assert len(c.manifest.required_scopes) >= 1


def test_unknown_collector_returns_none() -> None:
    assert get_collector("nope") is None
