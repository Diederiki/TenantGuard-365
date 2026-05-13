"""Verify the Phase 21/22 collectors registered."""

from __future__ import annotations

from app.collectors import all_collectors


def test_more_collectors_present() -> None:
    keys = {c.manifest.key for c in all_collectors()}
    for k in ("entra.signins", "entra.directoryAudits", "sharepoint.drives"):
        assert k in keys


def test_each_collector_has_required_scopes() -> None:
    for c in all_collectors():
        assert isinstance(c.manifest.required_scopes, list)
        assert all(isinstance(s, str) and s for s in c.manifest.required_scopes)
