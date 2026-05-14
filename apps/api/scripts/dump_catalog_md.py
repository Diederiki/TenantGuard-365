"""Generate docs/product/manageengine-feature-parity-matrix.md from the
feature registry.

Run from repo root:
    python apps/api/scripts/dump_catalog_md.py
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from textwrap import dedent

from app.registry.features import FEATURES, feature_summary, features_by_module


def main() -> None:
    summary = feature_summary()
    by_module = features_by_module()
    total = len(FEATURES)

    out: list[str] = []
    out.append(
        dedent(
            f"""
            # ManageEngine feature-parity matrix

            > Inspired by the public capability sets of M365 Manager Plus,
            > M365 Security Plus, and SharePoint Manager Plus. **No
            > ManageEngine source code, branding, or copyrighted text is
            > used.** The goal is parity of enterprise capability, not
            > replication of UI or copy.

            **Total features:** {total}.

            **Source of truth:** `apps/api/app/registry/features.py`.
            **Live mirror:** `GET /api/catalog/features` and the
            `/catalog` page in the web app.

            ## Status overview

            | Status | Count |
            |---|---|
            """
        ).strip()
    )
    for k, v in sorted(summary.items(), key=lambda kv: -kv[1]):
        out.append(f"| `{k}` | {v} |")
    out.append("")

    out.append("## By module\n\n| Module | Count |\n|---|---|")
    for k, v in sorted(by_module.items(), key=lambda kv: -len(kv[1])):
        out.append(f"| `{k}` | {len(v)} |")
    out.append("")

    # MVP / Phase 2 / Phase 3 / Future
    bucket: dict[str, list[str]] = defaultdict(list)
    for f in FEATURES:
        bucket[f.priority].append(f"- **{f.area} — {f.name}** (`{f.key}`) · status `{f.status}`")
    for k in ("MVP", "Phase 2", "Phase 3", "Future"):
        out.append(f"\n## {k} priority\n")
        out.extend(bucket.get(k, ["_(none)_"]))

    # Full matrix
    out.append("\n## Full matrix\n")
    out.append(
        "| Key | Area / Feature | Status | Priority | Source | Endpoint "
        "| App scopes | License | Risk | UI | Approval | Dry-run |"
    )
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for f in FEATURES:
        scopes = "`" + ", ".join(f.application_scopes) + "`" if f.application_scopes else "—"
        ep = f"`{f.endpoint}`" if f.endpoint else "—"
        ui = f"[{f.ui_page}]({f.ui_page})" if f.ui_page else "—"
        out.append(
            f"| `{f.key}` | **{f.area}** — {f.name} | `{f.status}` | {f.priority} | "
            f"{f.source or '—'} | {ep} | {scopes} | {f.license_dep or '—'} | "
            f"{f.risk} | {ui} | {'yes' if f.requires_approval else 'no'} | "
            f"{'yes' if f.requires_dry_run else 'no'} |"
        )

    out.append(
        dedent(
            """
            ## Next implementation steps

            1. Light up the **needs_graph_permission** entries by configuring
               an app registration with the listed `App scopes`. Most are
               read-only (`User.Read.All`, `Group.Read.All`,
               `MailboxSettings.Read`, `Files.Read.All`, etc.).
            2. Validate the **needs_sharepoint_api_validation** entries
               against a dev tenant. Microsoft has changed sharing-link
               surface area twice in 2024–2025.
            3. Schedule a Purview eDiscovery validation pass before
               promoting `security.content_search.*` past framework.
            4. Wire `app.management.*` actions to the real Graph + Exchange
               PowerShell paths. They are framework-ready with audit +
               approval + dry-run gates already in place.
            5. Implement the four "framework" settings pages (general,
               security, retention, notifications) with their backing
               tables in Phase 29.
            """
        ).strip()
    )

    out.append("")
    target = Path("docs/product/manageengine-feature-parity-matrix.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
