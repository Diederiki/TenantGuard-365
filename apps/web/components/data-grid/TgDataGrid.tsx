"use client";

import { DataGrid, DataGridProps } from "@mui/x-data-grid";
import { MuiThemeProvider } from "./MuiThemeProvider";

/**
 * Dark, Tailwind-friendly wrapper around MUI-X DataGrid (Community / MIT).
 *
 * We pin density to "compact" and disable selection by default; pages opt in
 * via spread props. Pagination is server-driven by passing `paginationMode`
 * and `rowCount` from the parent — by default it's client-side.
 */
const gridSx = {
  border: "1px solid rgba(148, 163, 184, 0.18)",
  backgroundColor: "rgba(15, 23, 42, 0.6)",
  borderRadius: 2,
  "& .MuiDataGrid-columnHeaders": {
    backgroundColor: "rgba(2, 6, 23, 0.8)",
  },
  "& .MuiDataGrid-columnHeader": {
    fontSize: 11,
    textTransform: "uppercase",
    letterSpacing: "0.06em",
    color: "#94a3b8",
  },
  "& .MuiDataGrid-cell": {
    borderBottomColor: "rgba(148, 163, 184, 0.12)",
    fontSize: 13,
  },
  "& .MuiDataGrid-footerContainer": {
    backgroundColor: "rgba(2, 6, 23, 0.6)",
    borderTop: "1px solid rgba(148, 163, 184, 0.18)",
  },
  "& .MuiDataGrid-overlay": {
    backgroundColor: "rgba(2, 6, 23, 0.4)",
  },
  "& .MuiTablePagination-root, & .MuiTablePagination-selectLabel, & .MuiTablePagination-displayedRows":
    {
      color: "#94a3b8",
      fontSize: 12,
    },
} as const;

export function TgDataGrid(props: DataGridProps) {
  return (
    <MuiThemeProvider>
      <div style={{ width: "100%" }}>
        <DataGrid
          density="compact"
          disableRowSelectionOnClick
          autoHeight
          pageSizeOptions={[10, 25, 50, 100]}
          initialState={{
            pagination: { paginationModel: { pageSize: 25, page: 0 } },
          }}
          {...props}
          sx={{ ...gridSx, ...(props.sx ?? {}) }}
        />
      </div>
    </MuiThemeProvider>
  );
}
