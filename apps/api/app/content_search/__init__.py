"""Content search framework.

Feature-flagged off by default. When ``FEATURE_CONTENT_SEARCH_ENABLED=true``
the search profiles can be created, but executing them still requires
``content_search.run`` permission AND acknowledgement of the legal warning
on the first run per user (Phase 10 wires that flow).

The framework provides:
- A registry of sensitive-information pattern templates.
- A profile model the operator can name and save.
- A worker-runnable executor that scans cached SharePoint/OneDrive items
  by metadata only (no raw content download by default).
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True)
class PatternTemplate:
    key: str
    display_name: str
    description: str
    regex: str
    severity: str = "attention"


PATTERN_LIBRARY: list[PatternTemplate] = [
    PatternTemplate(
        key="email_address",
        display_name="Email address",
        description="Generic email address pattern.",
        regex=r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b",
        severity="info",
    ),
    PatternTemplate(
        key="iban_eu",
        display_name="EU IBAN",
        description="European bank account identifier.",
        regex=r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b",
        severity="trouble",
    ),
    PatternTemplate(
        key="visa_card",
        display_name="Visa card number",
        description=(
            "Visa PAN (13 or 16 digits). False positives possible; "
            "combine with a Luhn check."
        ),
        regex=r"\b4\d{12}(?:\d{3})?\b",
        severity="critical",
    ),
    PatternTemplate(
        key="us_ssn",
        display_name="US Social Security Number",
        description="US SSN pattern.",
        regex=r"\b\d{3}-\d{2}-\d{4}\b",
        severity="critical",
    ),
    PatternTemplate(
        key="aws_access_key",
        display_name="AWS access key",
        description="AKIA-prefixed access key.",
        regex=r"\bAKIA[0-9A-Z]{16}\b",
        severity="critical",
    ),
]


_BY_KEY = {p.key: p for p in PATTERN_LIBRARY}


def get_pattern(key: str) -> PatternTemplate | None:
    return _BY_KEY.get(key)


def compile_patterns(keys: list[str]) -> list[tuple[PatternTemplate, re.Pattern[str]]]:
    out: list[tuple[PatternTemplate, re.Pattern[str]]] = []
    for k in keys:
        p = _BY_KEY.get(k)
        if p is None:
            continue
        out.append((p, re.compile(p.regex)))
    return out


def match_against_text(
    text: str, compiled: list[tuple[PatternTemplate, re.Pattern[str]]]
) -> list[tuple[PatternTemplate, str]]:
    """Return ``(pattern, matched_snippet)`` for each hit. Snippet is truncated."""
    hits: list[tuple[PatternTemplate, str]] = []
    for pattern, regex in compiled:
        for m in regex.finditer(text):
            snippet = m.group(0)
            if len(snippet) > 64:
                snippet = snippet[:64] + "…"
            hits.append((pattern, snippet))
    return hits
