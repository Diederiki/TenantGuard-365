"""OpenTelemetry initialisation.

Activated only when ``OTEL_EXPORTER_OTLP_ENDPOINT`` is set. When unset, the
module is a complete no-op so local dev and tests aren't slowed by the
SDK. Resource attributes include service name + environment so traces
land in the right bucket.

Instruments:
- FastAPI request spans.
- SQLAlchemy queries.
- httpx outbound calls (Microsoft Graph, OIDC discovery).
- redis commands.

Each instrumentation is guarded so a missing optional dependency does not
prevent the others from starting.
"""

from __future__ import annotations

import logging

from app.config import get_settings

logger = logging.getLogger("tg365.otel")

_initialised = False


def init_otel(app: object | None = None) -> bool:
    """Initialise OTel tracing. Idempotent.

    Returns True if the SDK was initialised, False if it was skipped
    (no endpoint configured) or already initialised.
    """
    global _initialised
    if _initialised:
        return False

    s = get_settings()
    endpoint = s.otel_exporter_otlp_endpoint
    if not endpoint:
        logger.debug("otel.disabled: no OTEL_EXPORTER_OTLP_ENDPOINT")
        return False

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except Exception as exc:
        logger.warning("otel.sdk_import_failed", extra={"err": str(exc)})
        return False

    resource = Resource.create(
        {
            "service.name": s.otel_service_name,
            "deployment.environment": s.environment,
        }
    )
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    trace.set_tracer_provider(provider)

    # FastAPI
    if app is not None:
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

            FastAPIInstrumentor.instrument_app(app)
        except Exception as exc:
            logger.warning("otel.fastapi_instrument_failed", extra={"err": str(exc)})

    # SQLAlchemy — instrument the global engine if available.
    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        from app.db.session import get_engine

        SQLAlchemyInstrumentor().instrument(engine=get_engine())
    except Exception as exc:
        logger.warning("otel.sqlalchemy_instrument_failed", extra={"err": str(exc)})

    # httpx
    try:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

        HTTPXClientInstrumentor().instrument()
    except Exception as exc:
        logger.warning("otel.httpx_instrument_failed", extra={"err": str(exc)})

    # redis
    try:
        from opentelemetry.instrumentation.redis import RedisInstrumentor

        RedisInstrumentor().instrument()
    except Exception as exc:
        logger.warning("otel.redis_instrument_failed", extra={"err": str(exc)})

    _initialised = True
    logger.info("otel.initialised", extra={"endpoint": endpoint})
    return True
