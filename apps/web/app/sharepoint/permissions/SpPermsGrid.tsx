"use client";

import { GridColDef } from "@mui/x-data-grid";
import { TgDataGrid } from "../../../components/data-grid/TgDataGrid";
import { Badge } from "../../../components/ui/badge";
import type { DemoSpPermission } from "../../../lib/demoData";

function principalVariant(t: DemoSpPermission["principal_type"]) {
  if (t === "Anonymous") return "critical" as const;
  if (t === "External") return "attention" as const;
  return "info" as const;
}

const columns: GridColDef<DemoSpPermission>[] = [
  { field: "site_url", headerName: "Site", flex: 0.8, minWidth: 180 },
  {
    field: "resource",
    headerName: "Resource",
    flex: 1.5,
    minWidth: 280,
    renderCell: (p) => (
      <span
        title={p.value as string}
        style={{
          fontFamily: "ui-monospace, monospace",
          fontSize: 12,
          overflow: "hidden",
          textOverflow: "ellipsis",
        }}
      >
        {p.value as string}
      </span>
    ),
  },
  { field: "principal_display", headerName: "Principal", flex: 1, minWidth: 200 },
  {
    field: "principal_type",
    headerName: "Type",
    width: 120,
    renderCell: (p) => (
      <Badge variant={principalVariant(p.value as DemoSpPermission["principal_type"])}>
        {String(p.value)}
      </Badge>
    ),
  },
  { field: "role", headerName: "Role", width: 110 },
  {
    field: "inheritance",
    headerName: "Inheritance",
    width: 140,
    renderCell: (p) => (
      <Badge variant={p.value === "unique" ? "attention" : "info"}>
        {String(p.value)}
      </Badge>
    ),
  },
  {
    field: "granted_at",
    headerName: "Granted",
    width: 130,
    valueFormatter: (v: string | undefined) =>
      v ? new Date(v).toISOString().slice(0, 10) : "—",
  },
];

export function SpPermsGrid({ rows }: { rows: DemoSpPermission[] }) {
  return <TgDataGrid rows={rows} columns={columns} getRowId={(r) => r.id} />;
}
