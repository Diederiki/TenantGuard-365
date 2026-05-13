"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from starlette.middleware.cors import CORSMiddleware

from app import __version__, rate_limit
from app.api.audit_routes import router as audit_router
from app.api.auth_routes import router as auth_router
from app.api.investigations_routes import router as investigations_router
from app.api.me_routes import router as me_router
from app.api.modules_routes import router as modules_router
from app.api.rbac_routes import router as rbac_router
from app.api.reports_routes import router as reports_router
from app.api.security_alerts_ops import router as security_alerts_ops_router
from app.api.security_routes import router as security_router
from app.api.settings_routes import router as settings_router
from app.api.tenants_routes import router as tenants_router
from app.config import get_settings
from app.health import router as health_router
from app.logging_setup import configure_logging

logger = logging.getLogger("tg365.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    settings.assert_safe_for_environment()
    logger.info(
        "app.startup",
        extra={
            "environment": settings.environment,
            "auth_mode": settings.auth_mode,
            "version": __version__,
        },
    )
    yield
    logger.info("app.shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(level=settings.log_level, fmt=settings.log_format)

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.environment != "production" else None,
        lifespan=lifespan,
    )

    # Rate limiting (Redis token-bucket; fail-open if Redis is down).
    rate_limit.install_rate_limit(app)

    # CORS — locked down to the configured public URL.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.app_public_url],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-CSRF-Token", "X-Request-ID"],
    )

    @app.middleware("http")
    async def request_id_and_security_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = req_id

        response = await call_next(request)

        response.headers["X-Request-ID"] = req_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if settings.environment == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )
        return response

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(me_router)
    app.include_router(audit_router)
    app.include_router(modules_router)
    app.include_router(reports_router)
    app.include_router(security_router)
    app.include_router(tenants_router)
    app.include_router(investigations_router)
    app.include_router(rbac_router)
    app.include_router(security_alerts_ops_router)
    app.include_router(settings_router)

    @app.get("/", tags=["meta"], summary="API root")
    def root() -> dict[str, str]:
        return {
            "name": settings.app_name,
            "version": __version__,
            "docs": "/docs" if settings.environment != "production" else "disabled",
        }

    return app


app = create_app()
