"""Double-submit CSRF protection.

On any successful response that creates a session, a CSRF cookie is set with
a random value. State-changing endpoints require the same value in the
`X-CSRF-Token` header.
"""

from __future__ import annotations

import secrets

from fastapi import HTTPException, Request, status


def issue_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def assert_csrf(request: Request, cookie_name: str) -> None:
    """Raise 403 if header does not match cookie for state-changing methods."""
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return
    cookie_val = request.cookies.get(cookie_name)
    header_val = request.headers.get("X-CSRF-Token")
    if not cookie_val or not header_val or not secrets.compare_digest(cookie_val, header_val):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="csrf_token_invalid")
