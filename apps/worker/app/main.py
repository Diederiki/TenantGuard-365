"""Worker entrypoint.

In dev: ``role=all`` runs a worker thread and a beat thread in one process.
In prod: deploy two services with ``role=worker`` and ``role=beat``.
"""

from __future__ import annotations

import logging
import os
import signal
import sys
import threading

from app.broker import broker  # noqa: F401
from app.config import get_settings
from app.logging_setup import configure_logging
from app.tasks import heartbeat  # noqa: F401  register actors

logger = logging.getLogger("tg365.worker")


def _run_worker() -> None:
    """Run Dramatiq worker by invoking the CLI under the hood."""
    from dramatiq.cli import main as dramatiq_main

    # Equivalent to: dramatiq app.tasks --processes 1 --threads 4
    sys.argv = ["dramatiq", "app.tasks", "--processes", "1", "--threads", "4"]
    dramatiq_main()


def _run_beat() -> None:
    from app.beat import run_beat

    run_beat()


def main() -> None:
    settings = get_settings()
    configure_logging(level=settings.log_level, fmt=settings.log_format)
    logger.info("worker.startup", extra={"role": settings.role, "env": settings.environment})

    role = settings.role
    if role == "worker":
        _run_worker()
        return
    if role == "beat":
        _run_beat()
        return

    # "all" — for local dev only. Run beat in a thread; worker on the main thread.
    beat_thread = threading.Thread(target=_run_beat, name="beat", daemon=True)
    beat_thread.start()
    try:
        _run_worker()
    except KeyboardInterrupt:
        logger.info("worker.shutdown.requested")


if __name__ == "__main__":
    # Graceful SIGTERM in containers.
    signal.signal(signal.SIGTERM, lambda *_: os._exit(0))
    main()
