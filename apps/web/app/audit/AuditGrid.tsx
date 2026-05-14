"use client";

import { GridColDef } from "@mui/x-data-grid";
import { TgDataGrid } from "../../components/data-grid/TgDataGrid";
import { Badge } from "../../components/ui/badge";

export type AuditRow = {
  id: number;
  event_time: string;
  actor_display: string;
  actor_type: string;
  action: string;
  target_label?: string | null;
  target_id?: string | null;
  target_type?: string | null;
  result: string;
};

const columns: GridColDef<AuditRow>[] = [
  {
    field: "event_time",
    headerName: "When (UTC)",
    width: 170,
    valueFormatter: (v: string | undefined) =>
      v ? new Date(v).toISOString().replace("T", " ").slice(0, 19) : "",
    renderCell: (p) => (
      <span style={{ fontFamily: "ui-monospace, monospace", fontSize: 12 }}>
        {p.formattedValue as string}
      </span>
    ),
  },
  {
    field: "actor_display",
    headerName: "Actor",
    flex: 1,
    minWidth: 180,
    renderCell: (p) => (
      <span>
        {p.row.actor_display}{" "}
        <span style={{ color: "#64748b", fontSize: 11 }}>
          ({p.row.actor_type})
        </span>
      </span>
    ),
  },
  {
    field: "action",
    headerName: "Action",
    flex: 1,
    minWidth: 200,
    renderCell: (p) => (
      <span style={{ fontFamily: "ui-monospace, monospace", fontSize: 12 }}>
        {p.value as string}
      </span>
    ),
  },
  {
    field: "target_label",
    headerName: "Target",
    flex: 1,
    minWidth: 200,
    renderCell: (p) => (
      <span style={{ fontSize: 12, color: "#94a3b8" }}>
        {p.row.target_label ?? p.row.target_id ?? "—"}
        {p.row.target_type ? (
          <span style={{ color: "#475569", marginLeft: 4 }}>
            [{p.row.target_type}]
          </span>
        ) : null}
      </span>
    ),
  },
  {
    field: "result",
    headerName: "Result",
    width: 110,
    renderCell: (p) => (
      <Badge variant={p.value === "success" ? "info" : "critical"}>
        {String(p.value)}
      </Badge>
    ),
  },
];

export function AuditGrid({
  rows,
  nextCursor,
}: {
  rows: AuditRow[];
  nextCursor: number | null;
}) {
  return (
    <>
      <TgDataGrid rows={rows} columns={columns} getRowId={(r) => r.id} />
      {nextCursor != null ? (
        <div className="mt-4 text-right">
          <a
            className="text-sm text-brand-400 hover:underline"
            href={`/audit?before_id=${nextCursor}`}
          >
            Older →
          </a>
        </div>
      ) : null}
    </>
  );
}
