"""Periodic security rule evaluation.

Reads tenants from the platform DB and calls ``evaluate_all`` for each.
Imported by app.tasks; the beat scheduler enqueues ``evaluate_security_rules``
on the configured cadence.
"""

from __future__ import annotations

import logging

import dramatiq

from app.broker import broker  # noqa: F401  ensure broker import side-effect

logger = logging.getLogger("tg365.worker.security")


@dramatiq.actor(queue_name="security.eval", max_retries=3)
def evaluate_security_rules() -> None:
    """Evaluate security rules for every tenant.

    The worker container shares the app package with the API in dev. In prod
    the worker image installs the api package separately. To avoid a hard
    dependency at this stage the evaluator function is imported lazily.
    """
    try:
        from sqlalchemy import select

        from app.db.models import Tenant
        from app.db.session import get_session_factory
        from app.security.engine import evaluate_all
    except Exception as exc:
        logger.warning("security.eval.unavailable", extra={"err": str(exc)})
        return

    factory = get_session_factory()
    with factory() as s:
        tenants = list(s.scalars(select(Tenant)))
        for t in tenants:
            counts = evaluate_all(s, t.id)
            logger.info(
                "security.eval.tenant",
                extra={"tenant_id": str(t.id), "counts": counts},
            )
        s.commit()
