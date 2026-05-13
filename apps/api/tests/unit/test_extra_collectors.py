"""Verify additional collectors registered."""

from __future__ import annotations

from app.collectors import all_collectors


def test_extra_collectors_present() -> None:
    keys = {c.manifest.key for c in all_collectors()}
    assert "entra.groups" in keys
    assert "entra.licenses" in keys
