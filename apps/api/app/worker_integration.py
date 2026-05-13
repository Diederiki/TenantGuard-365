"""Helper: drive collectors from a script or worker task.

This is the seam the Dramatiq worker uses to run a single collector inside a
managed DB session, equivalent to what /api/tenants/{id}/collectors/{key}/run
does for the synchronous HTTP path.
"""

from __future__ import annotations

import asyncio
import logging
import uuid

from app.collectors import run_collector
from app.db.session import get_session_factory

logger = logging.getLogger("tg365.worker.collector")


def run_collector_sync(key: str, *, tenant_id: uuid.UUID) -> dict[str, object]:
    factory = get_session_factory()
    with factory() as s:
        run = asyncio.run(run_collector(key, tenant_id=tenant_id, db=s))
        s.commit()
        return {
            "run_id": str(run.id),
            "status": run.status,
            "rows_in": run.rows_in,
            "rows_out": run.rows_out,
            "error": run.error,
        }
