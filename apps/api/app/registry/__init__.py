"""Feature registry — the canonical source of truth for what TenantGuard 365
intends to deliver vs. what is shipping vs. what is blocked by Microsoft.

Everything in here is plain Python data so it serialises cheaply to JSON for
the /api/catalog/* endpoints, can be diffed in PRs, and powers the docs
generated under docs/product/.
"""

from app.registry.features import FEATURES, FeatureEntry, FeatureStatus

__all__ = ["FEATURES", "FeatureEntry", "FeatureStatus"]
