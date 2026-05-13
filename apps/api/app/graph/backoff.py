"""Backoff helpers for the Graph client.

Microsoft Graph signals throttling via 429 + ``Retry-After`` (seconds or
HTTP-date). Other transient failures use exponential backoff with jitter.
"""

from __future__ import annotations

import email.utils
import random
import time
from typing import Final

DEFAULT_BACKOFF_BASE: Final = 1.0
DEFAULT_BACKOFF_CAP: Final = 60.0


def parse_retry_after(value: str | None) -> float | None:
    """Return seconds to wait, or ``None`` if the header is absent / unparseable."""
    if not value:
        return None
    value = value.strip()
    if value.isdigit():
        return float(value)
    parsed = email.utils.parsedate_to_datetime(value)
    if parsed is None:
        return None
    delta = parsed.timestamp() - time.time()
    return max(0.0, delta)


def exponential_backoff(
    attempt: int,
    *,
    base: float = DEFAULT_BACKOFF_BASE,
    cap: float = DEFAULT_BACKOFF_CAP,
    jitter: float = 0.25,
) -> float:
    """Compute the next backoff sleep with ±jitter."""
    raw = min(cap, base * (2 ** max(0, attempt)))
    return raw * (1 + random.uniform(-jitter, jitter))  # noqa: S311  not crypto
