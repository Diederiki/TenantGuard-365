"""Token cache encrypt/decrypt round-trip with tenant binding."""

from __future__ import annotations

import time

import pytest

from app.graph.token_cache import (
    GraphTokenEnvelope,
    associated_data_for_tenant,
    decrypt,
    encrypt,
)


def _env() -> GraphTokenEnvelope:
    return GraphTokenEnvelope(
        access_token="at-test",
        refresh_token="rt-test",
        token_type="Bearer",
        expires_at_epoch=int(time.time()) + 3600,
        scopes=["User.Read.All", "Group.Read.All"],
    )


def test_round_trip() -> None:
    aad = associated_data_for_tenant("tenant-a")
    blob = encrypt(_env(), aad)
    out = decrypt(blob, aad)
    assert out.access_token == "at-test"
    assert out.refresh_token == "rt-test"
    assert out.scopes == ["User.Read.All", "Group.Read.All"]


def test_swapped_tenant_fails() -> None:
    blob = encrypt(_env(), associated_data_for_tenant("tenant-a"))
    with pytest.raises(Exception):
        decrypt(blob, associated_data_for_tenant("tenant-b"))


def test_envelope_expiry() -> None:
    e = GraphTokenEnvelope(
        access_token="x", refresh_token=None, token_type="Bearer",
        expires_at_epoch=int(time.time()) - 5, scopes=[],
    )
    assert e.is_expired(leeway_seconds=0)
    fresh = GraphTokenEnvelope(
        access_token="x", refresh_token=None, token_type="Bearer",
        expires_at_epoch=int(time.time()) + 600, scopes=[],
    )
    assert not fresh.is_expired()
