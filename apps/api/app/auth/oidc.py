"""Microsoft Entra OIDC handler — auth-code + PKCE.

The handler covers:
- building the authorize URL
- validating state and PKCE
- exchanging code for tokens
- validating the id_token against JWKS

Phase 3 hooks the user's ``oid`` to ``platform_users``.
"""

from __future__ import annotations

import base64
import hashlib
import logging
import secrets
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import HTTPException, status

from app.config import get_settings

logger = logging.getLogger("tg365.auth.oidc")

_JWKS_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
_JWKS_TTL_SECONDS = 60 * 60


@dataclass(slots=True)
class PendingAuth:
    state: str
    code_verifier: str
    nonce: str
    redirect_to: str


@dataclass(slots=True)
class OidcIdentity:
    object_id: str
    tenant_id: str
    email: str | None
    display_name: str | None
    upn: str | None


def _pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def start_login(redirect_to: str = "/") -> tuple[str, PendingAuth]:
    settings = get_settings()
    if not (settings.entra_client_id and settings.entra_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="entra_not_configured",
        )

    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    verifier, challenge = _pkce_pair()

    params = {
        "client_id": settings.entra_client_id,
        "response_type": "code",
        "redirect_uri": settings.entra_redirect_uri,
        "response_mode": "query",
        "scope": "openid profile email offline_access",
        "state": state,
        "nonce": nonce,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    url = (
        f"{settings.entra_authority}/{settings.entra_tenant_id}"
        f"/oauth2/v2.0/authorize?{urlencode(params)}"
    )
    return url, PendingAuth(
        state=state, code_verifier=verifier, nonce=nonce, redirect_to=redirect_to
    )


async def exchange_code(code: str, code_verifier: str) -> dict[str, Any]:
    settings = get_settings()
    if not (settings.entra_client_id and settings.entra_tenant_id and settings.entra_client_secret):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="entra_not_configured",
        )

    token_url = (
        f"{settings.entra_authority}/{settings.entra_tenant_id}/oauth2/v2.0/token"
    )
    payload = {
        "client_id": settings.entra_client_id,
        "client_secret": settings.entra_client_secret,
        "redirect_uri": settings.entra_redirect_uri,
        "grant_type": "authorization_code",
        "code": code,
        "code_verifier": code_verifier,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(token_url, data=payload)
    if r.status_code != 200:
        logger.warning("oidc.token_exchange_failed", extra={"status": r.status_code})
        raise HTTPException(status_code=400, detail="token_exchange_failed")
    return r.json()  # type: ignore[no-any-return]


async def _get_jwks(tenant_id: str) -> dict[str, Any]:
    now = time.time()
    cached = _JWKS_CACHE.get(tenant_id)
    if cached is not None and now - cached[0] < _JWKS_TTL_SECONDS:
        return cached[1]
    settings = get_settings()
    url = (
        f"{settings.entra_authority}/{tenant_id}/v2.0/.well-known/openid-configuration"
    )
    async with httpx.AsyncClient(timeout=10.0) as client:
        cfg = (await client.get(url)).raise_for_status().json()
        jwks = (await client.get(cfg["jwks_uri"])).raise_for_status().json()
    _JWKS_CACHE[tenant_id] = (now, jwks)
    return jwks  # type: ignore[no-any-return]


async def verify_id_token(id_token: str, expected_nonce: str) -> OidcIdentity:
    settings = get_settings()
    assert settings.entra_tenant_id and settings.entra_client_id
    jwks = await _get_jwks(settings.entra_tenant_id)
    unverified = jwt.get_unverified_header(id_token)
    kid = unverified.get("kid")
    key_jwk = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if key_jwk is None:
        raise HTTPException(status_code=401, detail="id_token_kid_unknown")
    key = jwt.PyJWK(key_jwk).key
    claims = jwt.decode(
        id_token,
        key=key,
        algorithms=[unverified.get("alg", "RS256")],
        audience=settings.entra_client_id,
        issuer=(
            f"{settings.entra_authority}/{settings.entra_tenant_id}/v2.0"
        ),
        options={"require": ["exp", "iat", "iss", "sub", "aud"]},
    )
    if claims.get("nonce") != expected_nonce:
        raise HTTPException(status_code=401, detail="id_token_nonce_mismatch")
    if claims.get("tid") != settings.entra_tenant_id:
        raise HTTPException(status_code=401, detail="id_token_tid_mismatch")
    return OidcIdentity(
        object_id=str(claims["oid"]),
        tenant_id=str(claims["tid"]),
        email=claims.get("email") or claims.get("preferred_username"),
        display_name=claims.get("name"),
        upn=claims.get("preferred_username"),
    )
