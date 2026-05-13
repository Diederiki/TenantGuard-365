"""Scheduler next-run-at bump logic."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.reports.scheduler import _bump_next_run


def test_hourly() -> None:
    base = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    assert _bump_next_run("@hourly", after=base) == base + timedelta(hours=1)


def test_daily() -> None:
    base = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    assert _bump_next_run("@daily", after=base) == base + timedelta(days=1)


def test_weekly() -> None:
    base = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    assert _bump_next_run("@weekly", after=base) == base + timedelta(days=7)


def test_integer_minutes() -> None:
    base = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    assert _bump_next_run("15", after=base) == base + timedelta(minutes=15)


def test_unknown_falls_back_to_hourly() -> None:
    base = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    # No spaces and not a recognised shorthand → +1h fallback.
    assert _bump_next_run("nonsense", after=base) == base + timedelta(hours=1)


def test_full_cron_with_croniter() -> None:
    """Full 5-field cron uses croniter when installed."""
    base = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    result = _bump_next_run("0 9 * * MON", after=base)
    assert result > base
    assert result.hour == 9
    assert result.minute == 0


def test_monthly() -> None:
    base = datetime(2026, 1, 15, 0, 0, tzinfo=UTC)
    assert _bump_next_run("@monthly", after=base) == base + timedelta(days=31)
