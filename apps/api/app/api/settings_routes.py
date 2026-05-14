"""/api/settings — admin-managed config: Graph connection, auth policy, users."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.logger import AuditContext, AuditLogger
from app.auth import permissions as P
from app.auth import totp as totp_auth
from app.auth.dependencies import AuthedUser, require
from app.auth.password_policy import evaluate as evaluate_password
from app.auth.passwords import hash_password
from app.db.models import (
    PlatformPermission,
    PlatformRole,
    PlatformRoleAssignment,
    PlatformRolePermission,
    PlatformUser,
    Tenant,
    TenantGraphSettings,
)
from app.db.models.tenant_settings import wrap_app_secret
from app.db.session import db_session


def _role_permission_keys(db: Session, role_id: uuid.UUID) -> set[str]:
    rows = db.execute(
        select(PlatformPermission.key)
        .join(
            PlatformRolePermission,
            PlatformRolePermission.permission_id == PlatformPermission.id,
        )
        .where(PlatformRolePermission.role_id == role_id)
    ).all()
    return {r[0] for r in rows}

router = APIRouter(prefix="/api/settings", tags=["settings"])


# ---------------------------------------------------------------- Graph settings


class GraphSettingsIn(BaseModel):
    entra_tenant_id: str | None = None
    portal_client_id: str | None = None
    collector_client_id: str | None = None
    portal_client_secret: str | None = None
    collector_client_secret: str | None = None
    feature_2fa_required: bool = False
    allow_local_password: bool = False


class GraphSettingsOut(BaseModel):
    tenant_id: uuid.UUID
    entra_tenant_id: str | None
    portal_client_id: str | None
    collector_client_id: str | None
    portal_secret_present: bool
    collector_secret_present: bool
    feature_2fa_required: bool
    allow_local_password: bool


def _settings_to_out(row: TenantGraphSettings) -> GraphSettingsOut:
    return GraphSettingsOut(
        tenant_id=row.tenant_id,
        entra_tenant_id=row.entra_tenant_id,
        portal_client_id=row.portal_client_id,
        collector_client_id=row.collector_client_id,
        portal_secret_present=row.portal_client_secret_encrypted is not None,
        collector_secret_present=row.collector_client_secret_encrypted is not None,
        feature_2fa_required=row.feature_2fa_required,
        allow_local_password=row.allow_local_password,
    )


@router.get(
    "/graph/{tenant_id}",
    response_model=GraphSettingsOut,
    summary="Get current Graph connection settings for a tenant",
)
def get_graph_settings(
    tenant_id: uuid.UUID,
    _: AuthedUser = Depends(require(P.PLATFORM_ADMIN)),
    db: Session = Depends(db_session),
) -> GraphSettingsOut:
    row = db.scalar(
        select(TenantGraphSettings).where(TenantGraphSettings.tenant_id == tenant_id)
    )
    if row is None:
        # Return an empty placeholder so the UI can render a form.
        row = TenantGraphSettings(tenant_id=tenant_id)
        db.add(row)
        db.flush()
        db.commit()
    return _settings_to_out(row)


@router.post(
    "/graph/{tenant_id}",
    response_model=GraphSettingsOut,
    summary="Upsert Graph connection settings",
)
def upsert_graph_settings(
    tenant_id: uuid.UUID,
    body: GraphSettingsIn,
    authed: AuthedUser = Depends(require(P.PLATFORM_ADMIN)),
    db: Session = Depends(db_session),
) -> GraphSettingsOut:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="tenant_not_found")
    row = db.scalar(
        select(TenantGraphSettings).where(TenantGraphSettings.tenant_id == tenant_id)
    )
    if row is None:
        row = TenantGraphSettings(tenant_id=tenant_id)
        db.add(row)

    old = _settings_to_out(row).model_dump()

    if body.entra_tenant_id is not None:
        row.entra_tenant_id = body.entra_tenant_id or None
    if body.portal_client_id is not None:
        row.portal_client_id = body.portal_client_id or None
    if body.collector_client_id is not None:
        row.collector_client_id = body.collector_client_id or None
    if body.portal_client_secret:
        row.portal_client_secret_encrypted = wrap_app_secret(body.portal_client_secret)
    if body.collector_client_secret:
        row.collector_client_secret_encrypted = wrap_app_secret(body.collector_client_secret)
    row.feature_2fa_required = body.feature_2fa_required
    row.allow_local_password = body.allow_local_password

    db.flush()
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="settings.graph.updated",
        target_type="tenant",
        target_id=str(tenant_id),
        target_label=tenant.display_name,
        old_value=old,
        new_value=_settings_to_out(row).model_dump(),
    )
    db.commit()
    return _settings_to_out(row)


# ---------------------------------------------------------------- Users


class NewUserIn(BaseModel):
    email: str
    display_name: str
    role_keys: list[str] = ["readonly_auditor"]
    auth_method: str = "entra"  # entra | mock | local
    require_totp: bool = False


class NewUserOut(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str
    auth_method: str
    must_complete_totp: bool


@router.post(
    "/users",
    response_model=NewUserOut,
    summary="Provision a new platform user + role assignments",
)
def create_user(
    body: NewUserIn,
    authed: AuthedUser = Depends(require(P.PLATFORM_USERS_MANAGE)),
    db: Session = Depends(db_session),
) -> NewUserOut:
    if body.auth_method not in ("entra", "mock", "local"):
        raise HTTPException(status_code=400, detail="invalid_auth_method")

    existing = db.scalar(select(PlatformUser).where(PlatformUser.email == body.email))
    if existing is not None:
        raise HTTPException(status_code=409, detail="user_email_exists")

    # Privilege-escalation guard: caller cannot grant a role whose permission
    # set is not a subset of their own. The helper bypasses for
    # platform.admin holders (intentional super-admin escape hatch).
    caller_perms = set(authed.permissions)
    requested_roles: list[PlatformRole] = []
    for role_key in body.role_keys:
        role = db.scalar(select(PlatformRole).where(PlatformRole.key == role_key))
        if role is None:
            continue
        role_perms = _role_permission_keys(db, role.id)
        if not P.caller_can_grant_role(caller_perms, role_perms):
            raise HTTPException(
                status_code=403,
                detail=f"cannot_grant_higher_role:{role_key}",
            )
        requested_roles.append(role)

    user = PlatformUser(
        email=body.email.lower(),
        display_name=body.display_name,
        is_active=True,
        is_system=False,
        auth_method=body.auth_method,
        must_complete_totp=body.require_totp,
    )
    db.add(user)
    db.flush()

    granted_roles: list[str] = []
    for role in requested_roles:
        db.add(PlatformRoleAssignment(user_id=user.id, role_id=role.id, scope=""))
        granted_roles.append(role.key)

    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="settings.user.created",
        target_type="platform_user",
        target_id=str(user.id),
        target_label=user.email,
        new_value={
            "auth_method": body.auth_method,
            "roles": granted_roles,
            "require_totp": body.require_totp,
        },
    )
    db.commit()
    return NewUserOut(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        auth_method=user.auth_method,
        must_complete_totp=user.must_complete_totp,
    )


# ---------------------------------------------------------------- Password


class SetPasswordIn(BaseModel):
    password: str


@router.post(
    "/users/{user_id}/password",
    summary="Set or reset a local password for a user (auth_method must be 'local').",
)
async def set_user_password(
    user_id: uuid.UUID,
    body: SetPasswordIn,
    authed: AuthedUser = Depends(require(P.PLATFORM_USERS_MANAGE)),
    db: Session = Depends(db_session),
) -> dict[str, Any]:
    user = db.get(PlatformUser, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    if user.auth_method != "local":
        raise HTTPException(status_code=400, detail="user_not_local_auth")
    # Full policy check: length + character classes + HIBP k-anonymity.
    result = await evaluate_password(body.password)
    if not result.ok:
        raise HTTPException(
            status_code=400,
            detail={"error": "password_policy", "reasons": list(result.reasons)},
        )
    user.password_hash = hash_password(body.password)
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="settings.user.password.set",
        target_type="platform_user",
        target_id=str(user.id),
        target_label=user.email,
    )
    db.commit()
    return {"ok": True}


# ---------------------------------------------------------------- TOTP


class TotpEnrollOut(BaseModel):
    secret: str
    otpauth_uri: str
    qr_svg_base64: str


class TotpVerifyIn(BaseModel):
    code: str


@router.post(
    "/users/{user_id}/totp/enroll",
    response_model=TotpEnrollOut,
    summary="Generate (or rotate) a TOTP secret for a user. Returns the otpauth URI.",
)
def enroll_totp(
    user_id: uuid.UUID,
    authed: AuthedUser = Depends(require(P.PLATFORM_USERS_MANAGE)),
    db: Session = Depends(db_session),
) -> TotpEnrollOut:
    user = db.get(PlatformUser, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    secret, uri = totp_auth.enroll(db, user)
    qr_b64 = totp_auth.qr_svg_base64(uri)
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="settings.user.totp.enrolled",
        target_type="platform_user",
        target_id=str(user.id),
        target_label=user.email,
    )
    db.commit()
    return TotpEnrollOut(secret=secret, otpauth_uri=uri, qr_svg_base64=qr_b64)


@router.post(
    "/users/{user_id}/totp/verify",
    summary="Confirm enrollment by submitting a current code.",
)
def verify_totp(
    user_id: uuid.UUID,
    body: TotpVerifyIn,
    authed: AuthedUser = Depends(require(P.PLATFORM_USERS_MANAGE)),
    db: Session = Depends(db_session),
) -> dict[str, Any]:
    user = db.get(PlatformUser, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    ok = totp_auth.verify(db, user, body.code)
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="settings.user.totp.verified",
        target_type="platform_user",
        target_id=str(user.id),
        target_label=user.email,
        new_value={"ok": ok},
    )
    db.commit()
    if not ok:
        raise HTTPException(status_code=400, detail="invalid_code")
    return {"ok": True, "confirmed": True}
