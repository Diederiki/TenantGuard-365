"""Token-bucket rate limiter middleware backed by Redis.

Bucket-per-(actor, route-class). Anonymous requests bucketed by IP.

Limits (defaults — overridable via env in Phase 10):
- write routes (POST/PATCH/DELETE):  60 req / min
- read routes:                       600 req / min

On exceed: 429 + Retry-After header. Logged for visibility.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable

import redis
from fastapi import Request, Response, status

from app.config import get_settings

logger = logging.getLogger("tg365.rate_limit")

_DEFAULT_READ_LIMIT = 600
_DEFAULT_WRITE_LIMIT = 60
_WINDOW_SECONDS = 60

# Routes excluded from rate limiting.
_EXCLUDE_PREFIXES = ("/healthz", "/readyz", "/metrics", "/docs", "/openapi", "/favicon")


def _bucket_key(actor: str, route_class: str) -> str:
    window = int(time.time()) // _WINDOW_SECONDS
    return f"tg365:rl:{actor}:{route_class}:{window}"


def _client_actor(request: Request) -> str:
    """Prefer authed user id; fall back to client IP."""
    cookie = request.cookies.get(get_settings().session_cookie_name)
    if cookie:
        return f"sess:{cookie[:16]}"
    return f"ip:{request.client.host if request.client else 'unknown'}"


def install_rate_limit(app) -> None:  # type: ignore[no-untyped-def]
    """Install the middleware. Safe to call multiple times in tests."""
    settings = get_settings()
    r = redis.from_url(  # type: ignore[no-untyped-call]
        settings.redis_url,
        socket_timeout=1.0,
        socket_connect_timeout=1.0,
    )

    @app.middleware("http")  # type: ignore[misc]
    async def rate_limit_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        path = request.url.path
        if any(path.startswith(p) for p in _EXCLUDE_PREFIXES):
            return await call_next(request)
        route_class = "write" if request.method in {"POST", "PUT", "PATCH", "DELETE"} else "read"
        limit = _DEFAULT_WRITE_LIMIT if route_class == "write" else _DEFAULT_READ_LIMIT
        actor = _client_actor(request)
        key = _bucket_key(actor, route_class)
        try:
            count = int(r.incr(key) or 0)
            if count == 1:
                r.expire(key, _WINDOW_SECONDS)
        except Exception as exc:
            # Redis hiccup: fail-open with a warning. Better to serve than to deny.
            logger.warning("rate_limit.redis_unavailable", extra={"err": str(exc)})
            return await call_next(request)
        if count > limit:
            logger.info(
                "rate_limit.exceeded",
                extra={"actor": actor, "route_class": route_class, "count": count, "limit": limit},
            )
            return Response(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content='{"detail":"rate_limited"}',
                media_type="application/json",
                headers={"Retry-After": str(_WINDOW_SECONDS)},
            )
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - count))
        return response
