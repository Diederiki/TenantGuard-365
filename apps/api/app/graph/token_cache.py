"""Encrypted token cache for Microsoft Graph credentials.

Each tenant has at most one *current* refresh token + access token pair.
Tokens are sealed with AES-GCM using a key derived from ``TOKEN_CACHE_MASTER_KEY``.

The store is intentionally minimal — Phase 4 wires the per-tenant Graph client
on top of this.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import get_settings


class TokenCacheNotConfigured(RuntimeError):
    """Raised when the master key is missing."""


@dataclass(slots=True)
class GraphTokenEnvelope:
    access_token: str
    refresh_token: str | None
    token_type: str
    expires_at_epoch: int
    scopes: list[str]

    def is_expired(self, leeway_seconds: int = 60) -> bool:
        return time.time() >= self.expires_at_epoch - leeway_seconds


def _derive_key() -> bytes:
    settings = get_settings()
    if not settings.token_cache_master_key:
        # In dev, derive from session secret so devs don't have to set both.
        if settings.environment == "production":
            raise TokenCacheNotConfigured("TOKEN_CACHE_MASTER_KEY must be set in production")
        seed = settings.dev_session_secret
    else:
        seed = settings.token_cache_master_key
    return hashlib.sha256(seed.encode("utf-8")).digest()


def _aead() -> AESGCM:
    return AESGCM(_derive_key())


def encrypt(envelope: GraphTokenEnvelope, associated: bytes) -> bytes:
    """Encrypt a token envelope. Associated data binds the ciphertext to a tenant.

    Returns the concatenation ``nonce || ciphertext`` so we don't need a second
    column for the nonce.
    """
    nonce = os.urandom(12)
    payload = json.dumps(
        {
            "at": envelope.access_token,
            "rt": envelope.refresh_token,
            "tt": envelope.token_type,
            "ex": envelope.expires_at_epoch,
            "sc": envelope.scopes,
        },
        sort_keys=True,
    ).encode("utf-8")
    ct = _aead().encrypt(nonce, payload, associated)
    return nonce + ct


def decrypt(blob: bytes, associated: bytes) -> GraphTokenEnvelope:
    nonce, ct = blob[:12], blob[12:]
    pt = _aead().decrypt(nonce, ct, associated)
    data: dict[str, Any] = json.loads(pt.decode("utf-8"))
    return GraphTokenEnvelope(
        access_token=data["at"],
        refresh_token=data.get("rt"),
        token_type=data["tt"],
        expires_at_epoch=int(data["ex"]),
        scopes=list(data.get("sc", [])),
    )


def associated_data_for_tenant(tenant_id: str) -> bytes:
    """HMAC label so a swapped-tenant ciphertext fails to decrypt."""
    key = _derive_key()
    return base64.b64encode(hmac.new(key, tenant_id.encode("utf-8"), hashlib.sha256).digest())
