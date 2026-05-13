"""CSRF helper unit tests."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi import HTTPException

from app.auth.csrf import assert_csrf, issue_csrf_token


class _FakeRequest:
    def __init__(self, method: str, cookies: dict[str, str], headers: dict[str, str]) -> None:
        self.method = method
        self.cookies = cookies
        self.headers = headers


def _req(method: str, cookies: dict[str, str], headers: dict[str, str]) -> Any:
    return _FakeRequest(method, cookies, headers)


def test_issue_csrf_token_is_random() -> None:
    a = issue_csrf_token()
    b = issue_csrf_token()
    assert a != b
    assert len(a) >= 32


def test_get_method_skips_check() -> None:
    assert_csrf(_req("GET", {}, {}), "tg365_csrf")


def test_matching_cookie_and_header_passes() -> None:
    token = issue_csrf_token()
    assert_csrf(
        _req("POST", {"tg365_csrf": token}, {"X-CSRF-Token": token}),
        "tg365_csrf",
    )


def test_mismatched_token_raises() -> None:
    with pytest.raises(HTTPException) as exc:
        assert_csrf(
            _req("POST", {"tg365_csrf": "a"}, {"X-CSRF-Token": "b"}),
            "tg365_csrf",
        )
    assert exc.value.status_code == 403


def test_missing_header_raises() -> None:
    with pytest.raises(HTTPException) as exc:
        assert_csrf(_req("POST", {"tg365_csrf": "a"}, {}), "tg365_csrf")
    assert exc.value.status_code == 403
