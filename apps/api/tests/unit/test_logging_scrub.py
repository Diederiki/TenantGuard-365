"""Verify the log scrubber drops well-known secret keys."""

from __future__ import annotations

from app.logging_setup import _scrub


def test_scrubs_authorization_header() -> None:
    record = {"headers": {"Authorization": "Bearer s3cret", "X-Other": "ok"}}
    out = _scrub(record)
    assert out["headers"]["Authorization"] == "[REDACTED]"
    assert out["headers"]["X-Other"] == "ok"


def test_scrubs_nested_token_fields() -> None:
    record = {"oauth": {"access_token": "abc", "refresh_token": "def", "expires_in": 3600}}
    out = _scrub(record)
    assert out["oauth"]["access_token"] == "[REDACTED]"
    assert out["oauth"]["refresh_token"] == "[REDACTED]"
    assert out["oauth"]["expires_in"] == 3600


def test_scrubs_list_of_dicts() -> None:
    record = {"events": [{"password": "x"}, {"ok": 1}]}
    out = _scrub(record)
    assert out["events"][0]["password"] == "[REDACTED]"
    assert out["events"][1]["ok"] == 1


def test_scrub_passes_through_primitives() -> None:
    assert _scrub("hello") == "hello"
    assert _scrub(42) == 42
    assert _scrub(None) is None
