"""Verify additional rules registered."""

from __future__ import annotations

from app.security.rules import all_rules


def test_extra_rules_present() -> None:
    keys = {r.key for r in all_rules()}
    for k in (
        "sharepoint.org_wide_link_present",
        "entra.disabled_user_present",
        "entra.guest_count_high",
    ):
        assert k in keys
