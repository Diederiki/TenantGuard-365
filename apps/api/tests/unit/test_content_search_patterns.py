"""Pattern library + matcher unit tests."""

from __future__ import annotations

from app.content_search import compile_patterns, match_against_text


def test_email_pattern_matches() -> None:
    compiled = compile_patterns(["email_address"])
    hits = match_against_text("contact me at a.b@example.com or b@x.y", compiled)
    matched = [m for _, m in hits]
    assert "a.b@example.com" in matched
    assert "b@x.y" in matched


def test_aws_key_pattern_matches() -> None:
    compiled = compile_patterns(["aws_access_key"])
    hits = match_against_text("AKIAABCDEFGHIJKLMNOP rest", compiled)
    assert hits and hits[0][1] == "AKIAABCDEFGHIJKLMNOP"


def test_unknown_pattern_silently_skipped() -> None:
    compiled = compile_patterns(["does_not_exist"])
    assert compiled == []


def test_long_snippet_truncated() -> None:
    compiled = compile_patterns(["email_address"])
    long_local = "a" * 90 + "@example.com"
    hits = match_against_text(long_local, compiled)
    assert hits
    assert hits[0][1].endswith("…")
