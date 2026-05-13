"""Verify extra report definitions registered."""

from __future__ import annotations

from app.reports import all_reports


def test_extra_reports_present() -> None:
    keys = {r.key for r in all_reports()}
    for k in (
        "entra.groups.inventory",
        "entra.licenses.usage",
        "serviceHealth.overviews",
        "security.alerts.open",
    ):
        assert k in keys


def test_each_report_has_columns() -> None:
    for r in all_reports():
        assert len(r.columns) >= 1
