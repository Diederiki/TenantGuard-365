"""Unit tests for the password-policy helper."""

from __future__ import annotations

import asyncio
from collections.abc import Iterator
from unittest.mock import patch

import pytest

from app.auth import password_policy as pp


def _run(coro):  # type: ignore[no-untyped-def]
    return asyncio.run(coro)


@pytest.fixture()
def hibp_clean() -> Iterator[None]:
    with patch.object(pp, "_hibp_breach_count", new=_async_zero()):
        yield


def _async_zero():  # type: ignore[no-untyped-def]
    async def _f(_p: str) -> int:
        return 0

    return _f


def _async_breach(n: int):  # type: ignore[no-untyped-def]
    async def _f(_p: str) -> int:
        return n

    return _f


def test_too_short() -> None:
    r = pp.evaluate_sync_local_only("Short1!")
    assert not r.ok
    assert any(s.startswith("too_short") for s in r.reasons)


def test_too_few_classes() -> None:
    # 12 lowercase letters only — one character class.
    r = pp.evaluate_sync_local_only("aaaaaaaaaaaa")
    assert not r.ok
    assert any(s.startswith("too_few_character_classes") for s in r.reasons)


def test_passes_local_only() -> None:
    r = pp.evaluate_sync_local_only("MyStr0ng-Pass-2026")
    assert r.ok, r.reasons


def test_async_clean(hibp_clean: None) -> None:  # noqa: ARG001 — fixture activates
    r = _run(pp.evaluate("MyStr0ng-Pass-2026"))
    assert r.ok, r.reasons


def test_async_breached() -> None:
    with patch.object(pp, "_hibp_breach_count", new=_async_breach(42)):
        r = _run(pp.evaluate("MyStr0ng-Pass-2026"))
    assert not r.ok
    assert any(s.startswith("breached") for s in r.reasons)
    assert r.breached_count == 42


def test_async_network_error_does_not_block() -> None:
    """If HIBP is unreachable (returns -1), the password is accepted when
    the structural checks pass. Strict mode is a Phase-32 toggle."""

    async def _err(_p: str) -> int:
        return -1

    with patch.object(pp, "_hibp_breach_count", new=_err):
        r = _run(pp.evaluate("MyStr0ng-Pass-2026"))
    assert r.ok, r.reasons
