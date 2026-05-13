"""Per-tenant Graph + auth settings, manageable from the admin UI."""

from __future__ import annotations

import secrets as _secrets
import uuid

from sqlalchemy import Boolean, ForeignKey, LargeBinary, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.graph.token_cache import _aead

_SECRET_AAD = b"tg365-app-secret"


def wrap_app_secret(value: str) -> bytes:
    """AES-GCM seal of an app-registration client secret."""
    nonce = _secrets.token_bytes(12)
    ct = _aead().encrypt(nonce, value.encode("utf-8"), _SECRET_AAD)
    return nonce + ct


def unwrap_app_secret(blob: bytes) -> str:
    nonce, ct = blob[:12], blob[12:]
    return _aead().decrypt(nonce, ct, _SECRET_AAD).decode("utf-8")


class TenantGraphSettings(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "tenant_graph_settings"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    entra_tenant_id: Mapped[str | None] = mapped_column(String(64))
    portal_client_id: Mapped[str | None] = mapped_column(String(64))
    collector_client_id: Mapped[str | None] = mapped_column(String(64))
    portal_client_secret_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary)
    collector_client_secret_encrypted: Mapped[bytes | None] = mapped_column(LargeBinary)
    feature_2fa_required: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    allow_local_password: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
