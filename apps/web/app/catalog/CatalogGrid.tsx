"use client";

import { useMemo, useState } from "react";
import { GridColDef } from "@mui/x-data-grid";
import { TgDataGrid } from "../../components/data-grid/TgDataGrid";
import { Badge, BadgeVariant } from "../../components/ui/badge";
import { Feature, FeatureStatus } from "../../lib/featureCatalog";

const STATUS_VARIANT: Record<FeatureStatus, BadgeVariant> = {
  implemented_real_api: "info",
  implemented_mock_only: "info",
  framework_ready: "muted",
  needs_graph_permission: "attention",
  needs_purview: "attention",
  needs_defender: "critical",
  needs_exchange_powershell: "attention",
  needs_sharepoint_api_validation: "attention",
  blocked_by_microsoft_api: "critical",
  future_module: "muted",
  deprecated_or_unsupported: "critical",
};

const RISK_VARIANT: Record<Feature["risk"], BadgeVariant> = {
  low: "muted",
  medium: "info",
  high: "attention",
  critical: "critical",
};

const columns: GridColDef<Feature>[] = [
  { field: "area", headerName: "Area", flex: 1, minWidth: 180 },
  {
    field: "name",
    headerName: "Feature",
    flex: 1.4,
    minWidth: 260,
    renderCell: (p) => (
      <div style={{ paddingTop: 4 }}>
        <div style={{ color: "#e2e8f0" }}>{p.row.name}</div>
        <div style={{ color: "#64748b", fontSize: 11 }}>{p.row.description}</div>
      </div>
    ),
  },
  {
    field: "status",
    headerName: "Status",
    width: 220,
    renderCell: (p) => (
      <Badge variant={STATUS_VARIANT[p.row.status]}>{p.row.status.replace(/_/g, " ")}</Badge>
    ),
  },
  { field: "priority", headerName: "Priority", width: 100 },
  {
    field: "risk",
    headerName: "Risk",
    width: 100,
    renderCell: (p) => (
      <Badge variant={RISK_VARIANT[p.row.risk]}>{p.row.risk}</Badge>
    ),
  },
  {
    field: "source",
    headerName: "Source",
    flex: 0.7,
    minWidth: 160,
    renderCell: (p) => (
      <span style={{ fontFamily: "ui-monospace, monospace", fontSize: 11, color: "#94a3b8" }}>
        {p.row.source ?? "—"}
      </span>
    ),
  },
  {
    field: "endpoint",
    headerName: "Endpoint",
    flex: 1.2,
    minWidth: 220,
    renderCell: (p) => (
      <span style={{ fontFamily: "ui-monospace, monospace", fontSize: 11, color: "#94a3b8" }}>
        {p.row.endpoint ?? "—"}
      </span>
    ),
  },
  {
    field: "application_scopes",
    headerName: "App scopes",
    flex: 1,
    minWidth: 200,
    valueFormatter: (v: string[] | undefined) => (v ?? []).join(", "),
    renderCell: (p) => (
      <span style={{ fontFamily: "ui-monospace, monospace", fontSize: 11, color: "#94a3b8" }}>
        {(p.row.application_scopes ?? []).join(", ") || "—"}
      </span>
    ),
  },
  {
    field: "ui_page",
    headerName: "UI",
    width: 160,
    renderCell: (p) =>
      p.row.ui_page ? (
        <a
          className="text-brand-400 hover:underline"
          style={{ fontFamily: "ui-monospace, monospace", fontSize: 11 }}
          href={p.row.ui_page}
        >
          {p.row.ui_page}
        </a>
      ) : (
        <span style={{ color: "#475569", fontSize: 11 }}>—</span>
      ),
  },
];

export function CatalogGrid({ features }: { features: Feature[] }) {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<string>("all");
  const [module, setModule] = useState<string>("all");
  const [priority, setPriority] = useState<string>("all");

  const modules = useMemo(
    () => Array.from(new Set(features.map((f) => f.module))).sort(),
    [features],
  );
  const statuses = useMemo(
    () => Array.from(new Set(features.map((f) => f.status))).sort(),
    [features],
  );

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return features.filter((f) => {
      if (status !== "all" && f.status !== status) return false;
      if (module !== "all" && f.module !== module) return false;
      if (priority !== "all" && f.priority !== priority) return false;
      if (!q) return true;
      const blob = [f.name, f.description, f.area, f.source, f.endpoint]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return blob.includes(q);
    });
  }, [features, search, status, module, priority]);

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <input
          type="text"
          placeholder="Search name / description / endpoint…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 min-w-[240px] rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-brand-500"
        />
        <select
          value={module}
          onChange={(e) => setModule(e.target.value)}
          className="rounded-md border border-slate-800 bg-slate-900 px-2 py-2 text-sm text-slate-200"
        >
          <option value="all">All modules</option>
          {modules.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="rounded-md border border-slate-800 bg-slate-900 px-2 py-2 text-sm text-slate-200"
        >
          <option value="all">All statuses</option>
          {statuses.map((s) => (
            <option key={s} value={s}>
              {s.replace(/_/g, " ")}
            </option>
          ))}
        </select>
        <select
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
          className="rounded-md border border-slate-800 bg-slate-900 px-2 py-2 text-sm text-slate-200"
        >
          <option value="all">All priorities</option>
          {["MVP", "Phase 2", "Phase 3", "Future"].map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
        <span className="text-xs text-slate-400">
          {filtered.length} / {features.length}
        </span>
      </div>
      <TgDataGrid
        rows={filtered}
        columns={columns}
        getRowId={(r) => (r as Feature).key}
        getRowHeight={() => 56}
      />
    </div>
  );
}
