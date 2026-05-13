"""Test that _payload_hash is deterministic and key-sensitive."""

from __future__ import annotations

from app.audit.logger import _payload_hash


def test_hash_is_deterministic() -> None:
    record = {"action": "x", "actor": "y"}
    assert _payload_hash(record) == _payload_hash(record)


def test_hash_differs_when_record_changes() -> None:
    r1 = {"action": "a"}
    r2 = {"action": "b"}
    assert _payload_hash(r1) != _payload_hash(r2)


def test_hash_is_32_bytes() -> None:
    assert len(_payload_hash({"action": "z"})) == 32
