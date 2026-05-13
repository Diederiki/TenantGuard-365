"""Auth routes: /auth/login/mock, /auth/login/entra, /auth/callback, /auth/logout."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from itsdangerous import BadSignature, URLSafeSerializer
from sqlalchemy.orm import Session

from app.audit.logger import AuditContext, AuditLogger
from app.auth import oidc
from app.auth.mock import assert_mock_auth_allowed, resolve_mock_user
from app.auth.sessions import get_session_store
from app.config import get_settings
from app.db.session import db_session

logger = logging.getLogger("tg365.api.auth")
router = APIRouter(prefix="/auth", tags=["auth"])

_PENDING_COOKIE = "tg365_pending_auth"


def _pending_serializer() -> URLSafeSerializer:
    return URLSafeSerializer(get_settings().dev_session_secret, salt="tg365-pending-auth")


def _set_session_cookies(response: Response, sid: str) -> None:
    settings = get_settings()
    store = get_session_store()
    signed = store.sign_sid(sid)
    secure = settings.environment != "development"
    response.set_cookie(
        settings.session_cookie_name,
        signed,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
        max_age=settings.session_idle_timeout_minutes * 60,
    )
    # CSRF cookie is *not* HttpOnly so the SPA can read and mirror it as a header.
    from app.auth.csrf import issue_csrf_token

    response.set_cookie(
        settings.csrf_cookie_name,
        issue_csrf_token(),
        httponly=False,
        secure=secure,
        samesite="lax",
        path="/",
        max_age=settings.session_idle_timeout_minutes * 60,
    )


def _clear_session_cookies(response: Response) -> None:
    settings = get_settings()
    for name in (settings.session_cookie_name, settings.csrf_cookie_name):
        response.delete_cookie(name, path="/")


@router.post("/login/mock")
def login_mock(
    request: Request,
    response: Response,
    email: str = Query(..., description="seeded platform_users.email"),
    db: Session = Depends(db_session),
) -> dict[str, str]:
    """Sign in as a seeded user. Local-dev only."""
    assert_mock_auth_allowed()
    user = resolve_mock_user(db, email)
    sid, _data = get_session_store().create(
        user_id=user.id,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    _set_session_cookies(response, sid)
    AuditLogger(db).log(
        AuditContext(
            actor_id=user.id,
            actor_display=user.display_name,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        ),
        action="auth.signin.success",
        target_type="platform_user",
        target_id=str(user.id),
        target_label=user.email,
        new_value={"provider": "mock"},
    )
    db.commit()
    return {"status": "ok", "user": user.email}


@router.get("/login/entra")
def login_entra(redirect_to: str = "/") -> Response:
    """Redirect to Entra's authorize endpoint with PKCE + state + nonce."""
    url, pending = oidc.start_login(redirect_to=redirect_to)
    cookie_payload = _pending_serializer().dumps(
        {
            "state": pending.state,
            "code_verifier": pending.code_verifier,
            "nonce": pending.nonce,
            "redirect_to": pending.redirect_to,
        }
    )
    settings = get_settings()
    response = Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    response.headers["Location"] = url
    response.set_cookie(
        _PENDING_COOKIE,
        cookie_payload,
        httponly=True,
        secure=settings.environment != "development",
        samesite="lax",
        path="/",
        max_age=600,  # 10 minutes
    )
    return response


@router.get("/callback")
async def callback(
    request: Request,
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(db_session),
) -> Response:
    pending_cookie = request.cookies.get(_PENDING_COOKIE)
    if not pending_cookie:
        raise HTTPException(status_code=400, detail="no_pending_auth")
    try:
        payload = _pending_serializer().loads(pending_cookie)
    except BadSignature as exc:
        raise HTTPException(status_code=400, detail="bad_pending_signature") from exc
    if not isinstance(payload, dict) or payload.get("state") != state:
        raise HTTPException(status_code=400, detail="state_mismatch")

    token_resp = await oidc.exchange_code(code, payload["code_verifier"])
    id_token = token_resp.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="missing_id_token")
    identity = await oidc.verify_id_token(id_token, expected_nonce=payload["nonce"])

    # Look up or stub-provision a platform user.
    from sqlalchemy import select

    from app.db.models import PlatformUser

    user = db.scalar(
        select(PlatformUser).where(PlatformUser.entra_object_id == identity.object_id)
    )
    if user is None and identity.email:
        user = db.scalar(select(PlatformUser).where(PlatformUser.email == identity.email))
        if user is not None:
            user.entra_object_id = identity.object_id
    if user is None:
        raise HTTPException(status_code=403, detail="user_not_provisioned")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="user_inactive")

    sid, _data = get_session_store().create(
        user_id=user.id,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    redirect_to = payload.get("redirect_to") or "/"
    final = Response(status_code=status.HTTP_303_SEE_OTHER)
    final.headers["Location"] = redirect_to
    _set_session_cookies(final, sid)
    final.delete_cookie(_PENDING_COOKIE, path="/")

    AuditLogger(db).log(
        AuditContext(
            actor_id=user.id,
            actor_display=user.display_name,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        ),
        action="auth.signin.success",
        target_type="platform_user",
        target_id=str(user.id),
        target_label=user.email,
        new_value={"provider": "entra", "tid": identity.tenant_id},
    )
    db.commit()
    return final


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(db_session),
) -> dict[str, str]:
    settings = get_settings()
    store = get_session_store()
    signed = request.cookies.get(settings.session_cookie_name)
    actor_id = None
    actor_display = "unknown"
    if signed:
        sid = store.unsign_sid(signed)
        if sid:
            data = store.get(sid)
            if data is not None:
                from app.db.models import PlatformUser

                u = db.get(PlatformUser, data.user_id)
                if u is not None:
                    actor_id = u.id
                    actor_display = u.display_name
            store.destroy(sid)
    _clear_session_cookies(response)
    AuditLogger(db).log(
        AuditContext(
            actor_id=actor_id,
            actor_display=actor_display,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        ),
        action="auth.signout",
    )
    db.commit()
    return {"status": "ok"}
