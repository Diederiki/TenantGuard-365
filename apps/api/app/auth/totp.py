"""TOTP enrollment + verification.

Uses ``pyotp`` for the canonical TOTP algorithm. Secrets are stored encrypted
via the platform's existing AES-GCM helpers (see app.graph.token_cache).
"""

from __future__ import annotations

import base64
import io
import secrets
import uuid
from datetime import UTC, datetime

import pyotp
import qrcode
import qrcode.image.svg
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PlatformUser, PlatformUserTotp
from app.graph.token_cache import _aead


def _wrap(secret_b32: str) -> bytes:
    nonce = secrets.token_bytes(12)
    ct = _aead().encrypt(nonce, secret_b32.encode("ascii"), b"tg365-totp")
    return nonce + ct


def _unwrap(blob: bytes) -> str:
    nonce, ct = blob[:12], blob[12:]
    return _aead().decrypt(nonce, ct, b"tg365-totp").decode("ascii")


def enroll(db: Session, user: PlatformUser, issuer: str = "TenantGuard 365") -> tuple[str, str]:
    """Create or replace the TOTP secret for the user. Returns ``(secret, otpauth_uri)``.

    The secret is base32; the otpauth URI is what an authenticator app expects
    in its QR code.
    """
    secret = pyotp.random_base32()
    existing = db.scalar(
        select(PlatformUserTotp).where(PlatformUserTotp.user_id == user.id)
    )
    blob = _wrap(secret)
    if existing is None:
        db.add(PlatformUserTotp(user_id=user.id, secret_encrypted=blob))
    else:
        existing.secret_encrypted = blob
        existing.confirmed_at = None
        existing.last_used_at = None
    user.must_complete_totp = True
    db.flush()
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user.email, issuer_name=issuer)
    return secret, uri


def verify(db: Session, user: PlatformUser, code: str) -> bool:
    row = db.scalar(
        select(PlatformUserTotp).where(PlatformUserTotp.user_id == user.id)
    )
    if row is None:
        return False
    secret = _unwrap(row.secret_encrypted)
    totp = pyotp.TOTP(secret)
    # 30-second step; allow one step skew either side.
    if not totp.verify(code, valid_window=1):
        return False
    row.last_used_at = datetime.now(UTC)
    if row.confirmed_at is None:
        row.confirmed_at = datetime.now(UTC)
        user.must_complete_totp = False
    db.flush()
    return True


def qr_svg_base64(otpauth_uri: str) -> str:
    """Render an otpauth URI to a base64-encoded SVG QR code."""
    buf = io.BytesIO()
    img = qrcode.make(
        otpauth_uri,
        image_factory=qrcode.image.svg.SvgImage,
        box_size=10,
        border=2,
    )
    img.save(buf)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def is_enrolled(db: Session, user_id: uuid.UUID) -> bool:
    row = db.scalar(
        select(PlatformUserTotp).where(PlatformUserTotp.user_id == user_id)
    )
    return row is not None and row.confirmed_at is not None


