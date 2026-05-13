"""OIDC PKCE primitive tests."""

from __future__ import annotations

import base64
import hashlib

from app.auth.oidc import _pkce_pair


def test_pkce_pair_produces_matching_challenge() -> None:
    verifier, challenge = _pkce_pair()
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    expected = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    assert challenge == expected
    assert len(verifier) >= 43  # RFC 7636 minimum entropy


def test_pkce_pair_is_unique() -> None:
    a = _pkce_pair()
    b = _pkce_pair()
    assert a != b
