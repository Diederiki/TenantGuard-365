"""Backoff helper unit tests."""

from __future__ import annotations

import datetime as dt

from app.graph.backoff import exponential_backoff, parse_retry_after


def test_parse_retry_after_seconds() -> None:
    assert parse_retry_after("3") == 3.0
    assert parse_retry_after("0") == 0.0


def test_parse_retry_after_none_when_missing() -> None:
    assert parse_retry_after(None) is None
    assert parse_retry_after("") is None


def test_parse_retry_after_http_date_in_future() -> None:
    future = dt.datetime.now(dt.UTC) + dt.timedelta(seconds=60)
    rfc = future.strftime("%a, %d %b %Y %H:%M:%S GMT")
    val = parse_retry_after(rfc)
    assert val is not None
    assert 50.0 < val < 70.0


def test_exponential_backoff_grows_and_caps() -> None:
    a0 = exponential_backoff(0, base=1.0, cap=10.0, jitter=0.0)
    a2 = exponential_backoff(2, base=1.0, cap=10.0, jitter=0.0)
    a10 = exponential_backoff(10, base=1.0, cap=10.0, jitter=0.0)
    assert a0 == 1.0
    assert a2 == 4.0
    assert a10 == 10.0  # capped


def test_exponential_backoff_jitter_within_bounds() -> None:
    for _ in range(50):
        v = exponential_backoff(3, base=1.0, cap=100.0, jitter=0.5)
        assert 4.0 <= v <= 12.0
