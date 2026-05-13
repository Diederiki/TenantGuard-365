"""Verify the wider report catalogue registered."""

from __future__ import annotations

from app.reports import all_reports


def test_more_reports_present() -> None:
    keys = {r.key for r in all_reports()}
    expected = {
        "entra.users.disabled",
        "entra.users.inactive",
        "entra.users.recently_created",
        "entra.groups.empty",
        "sharepoint.sites.owners",
        "sharepoint.sites.inactive",
        "sharepoint.sharing.company_wide_links",
        "entra.users.counts",
    }
    assert expected.issubset(keys), f"missing: {expected - keys}"


def test_total_report_count_grew() -> None:
    assert len(all_reports()) >= 16
