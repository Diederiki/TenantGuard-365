"""Structured JSON logging with a secret scrubber.

Logging is configured once at startup. The scrubber drops well-known secret keys
from records before serialisation so tokens never reach disk.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from pythonjsonlogger.json import JsonFormatter

SENSITIVE_KEYS = {
    "authorization",
    "proxy-authorization",
    "cookie",
    "set-cookie",
    "x-csrf-token",
    "client_secret",
    "code",
    "access_token",
    "refresh_token",
    "id_token",
    "token",
    "password",
    "secret",
    "api_key",
}


def _scrub(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            k: ("[REDACTED]" if k.lower() in SENSITIVE_KEYS else _scrub(v))
            for k, v in value.items()
        }
    if isinstance(value, list | tuple):
        return type(value)(_scrub(v) for v in value)
    return value


class ScrubbingJsonFormatter(JsonFormatter):
    def add_fields(  # type: ignore[override]
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        for k in list(log_record.keys()):
            log_record[k] = _scrub(log_record[k])
        log_record.setdefault("level", record.levelname.lower())
        log_record.setdefault("logger", record.name)


def configure_logging(level: str, fmt: str) -> None:
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler(stream=sys.stdout)

    if fmt == "json":
        formatter: logging.Formatter = ScrubbingJsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={"asctime": "ts", "levelname": "level", "name": "logger"},
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)-7s %(name)s :: %(message)s"
        )

    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(level.upper())

    # Tame the chatty third-party loggers.
    for noisy in ("uvicorn.access", "botocore", "boto3", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
