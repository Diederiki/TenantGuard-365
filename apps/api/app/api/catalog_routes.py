"""/api/catalog — read-only registry of features the platform claims.

Powers the in-app feature parity catalog. No tenant data flows through here;
the registry is shipped with the binary, so this endpoint is cheap and
deterministic.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Depends

from app.auth.dependencies import AuthedUser, current_user
from app.registry.features import FEATURES, feature_summary, features_by_module

router = APIRouter(prefix="/api/catalog", tags=["catalog"])


@router.get(
    "/features",
    summary="Return every feature in the registry plus aggregate counts.",
)
def list_features(_: AuthedUser = Depends(current_user)) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for f in FEATURES:
        d = asdict(f)
        # tuples -> lists for stable JSON
        for k in (
            "delegated_scopes",
            "application_scopes",
            "database_tables",
            "export_formats",
            "tags",
        ):
            d[k] = list(d[k])
        rows.append(d)
    return {
        "total": len(FEATURES),
        "by_status": feature_summary(),
        "by_module": {k: len(v) for k, v in features_by_module().items()},
        "items": rows,
    }


@router.get(
    "/features/summary",
    summary="Counts only — cheap dashboard signal.",
)
def features_summary(_: AuthedUser = Depends(current_user)) -> dict[str, Any]:
    return {
        "total": len(FEATURES),
        "by_status": feature_summary(),
        "by_module": {k: len(v) for k, v in features_by_module().items()},
    }
