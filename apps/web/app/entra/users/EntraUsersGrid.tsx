"use client";

import { GridColDef } from "@mui/x-data-grid";
import { TgDataGrid } from "../../../components/data-grid/TgDataGrid";
import { Badge } from "../../../components/ui/badge";
import type { DemoEntraUser } from "../../../lib/demoData";

const columns: GridColDef<DemoEntraUser>[] = [
  { field: "display_name", headerName: "Display name", flex: 1, minWidth: 180 },
  {
    field: "user_principal_name",
    headerName: "UPN",
    flex: 1.4,
    minWidth: 240,
    renderCell: (p) => (
      <span style={{ fontFamily: "ui-monospace, monospace", fontSize: 12 }}>
        {p.value as string}
      </span>
    ),
  },
  {
    field: "user_type",
    headerName: "Type",
    width: 100,
    renderCell: (p) => (
      <Badge variant={p.value === "Guest" ? "attention" : "info"}>
        {String(p.value)}
      </Badge>
    ),
  },
  {
    field: "account_enabled",
    headerName: "Account",
    width: 110,
    renderCell: (p) =>
      p.value ? (
        <Badge variant="info">enabled</Badge>
      ) : (
        <Badge variant="critical">disabled</Badge>
      ),
  },
  { field: "department", headerName: "Dept", width: 140 },
  { field: "job_title", headerName: "Title", flex: 1, minWidth: 140 },
  { field: "office_location", headerName: "Office", width: 120 },
  {
    field: "last_signin_at",
    headerName: "Last sign-in (UTC)",
    width: 170,
    valueFormatter: (v: string | null | undefined) =>
      v ? new Date(v).toISOString().replace("T", " ").slice(0, 16) : "—",
    renderCell: (p) => (
      <span style={{ fontFamily: "ui-monospace, monospace", fontSize: 12 }}>
        {p.formattedValue as string}
      </span>
    ),
  },
];

export function EntraUsersGrid({ rows }: { rows: DemoEntraUser[] }) {
  return <TgDataGrid rows={rows} columns={columns} getRowId={(r) => r.id} />;
}
