"""Rate limit bucket helpers."""

from __future__ import annotations

from app.rate_limit import _EXCLUDE_PREFIXES, _bucket_key


def test_bucket_key_includes_window() -> None:
    k1 = _bucket_key("ip:1.2.3.4", "read")
    assert k1.startswith("tg365:rl:ip:1.2.3.4:read:")


def test_excluded_prefixes_includes_health() -> None:
    assert "/healthz" in _EXCLUDE_PREFIXES
    assert "/readyz" in _EXCLUDE_PREFIXES
    assert "/metrics" in _EXCLUDE_PREFIXES
