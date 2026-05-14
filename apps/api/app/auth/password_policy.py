"""Password policy + Have I Been Pwned k-anonymity check.

We rate passwords on three axes:

1. **Length**: at least 12 characters.
2. **Character classes**: at least 3 of {lower, upper, digit, symbol}.
3. **Breach prevalence**: query the Pwned Passwords range API with the
   first 5 chars of the SHA-1 hex digest; reject if the full digest
   appears in the response (the full hash never leaves this process).

The HIBP check is **best-effort**: a network failure does not block the
password change, but it is logged. Strict enforcement (fail-on-network-
error) is a Phase-32 toggle.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass

import httpx

logger = logging.getLogger("tg365.auth.password_policy")

MIN_LENGTH = 12
MIN_CHARACTER_CLASSES = 3
HIBP_URL = "https://api.pwnedpasswords.com/range/{prefix}"
HIBP_TIMEOUT = 3.0


@dataclass(frozen=True, slots=True)
class PolicyResult:
    ok: bool
    reasons: tuple[str, ...]
    breached_count: int = 0


def _count_classes(p: str) -> int:
    cls = 0
    if re.search(r"[a-z]", p):
        cls += 1
    if re.search(r"[A-Z]", p):
        cls += 1
    if re.search(r"[0-9]", p):
        cls += 1
    if re.search(r"[^A-Za-z0-9]", p):
        cls += 1
    return cls


async def _hibp_breach_count(plaintext: str) -> int:
    """Return how many times the password appears in the Pwned Passwords
    corpus. 0 = clean. Raises only on programming errors; network errors
    return -1 so callers can treat it as "unknown" rather than blocking.
    """
    digest = hashlib.sha1(plaintext.encode("utf-8")).hexdigest().upper()
    prefix, suffix = digest[:5], digest[5:]
    try:
        async with httpx.AsyncClient(timeout=HIBP_TIMEOUT) as client:
            r = await client.get(
                HIBP_URL.format(prefix=prefix),
                headers={"Add-Padding": "true"},
            )
            r.raise_for_status()
    except Exception as exc:
        logger.warning("hibp.network_error", extra={"err": str(exc)})
        return -1
    for line in r.text.splitlines():
        try:
            suf, count_str = line.split(":", 1)
        except ValueError:
            continue
        if suf.strip().upper() == suffix:
            try:
                return int(count_str.strip())
            except ValueError:
                return 1
    return 0


async def evaluate(plaintext: str) -> PolicyResult:
    """Run the full policy + HIBP check. Used by the API endpoint."""
    reasons: list[str] = []
    if len(plaintext) < MIN_LENGTH:
        reasons.append(f"too_short:min_{MIN_LENGTH}")
    classes = _count_classes(plaintext)
    if classes < MIN_CHARACTER_CLASSES:
        reasons.append(f"too_few_character_classes:min_{MIN_CHARACTER_CLASSES}")
    breach = await _hibp_breach_count(plaintext)
    if breach > 0:
        reasons.append(f"breached:{breach}")
    return PolicyResult(ok=not reasons, reasons=tuple(reasons), breached_count=max(0, breach))


def evaluate_sync_local_only(plaintext: str) -> PolicyResult:
    """Synchronous variant that skips the HIBP check. Used when the caller
    cannot await (e.g. seed scripts, migrations).
    """
    reasons: list[str] = []
    if len(plaintext) < MIN_LENGTH:
        reasons.append(f"too_short:min_{MIN_LENGTH}")
    if _count_classes(plaintext) < MIN_CHARACTER_CLASSES:
        reasons.append(f"too_few_character_classes:min_{MIN_CHARACTER_CLASSES}")
    return PolicyResult(ok=not reasons, reasons=tuple(reasons))
