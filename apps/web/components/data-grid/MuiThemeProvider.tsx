"use client";

import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { ReactNode } from "react";

/**
 * Dark theme matched to the Tailwind slate-950 surface used elsewhere in the
 * app. Wrap any MUI-X DataGrid usage in this provider so colors are
 * consistent. Intentionally minimal — we only pull MUI for the data-grid;
 * everything else stays Tailwind.
 */
const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#3b82f6" }, // brand-500 equivalent
    background: {
      default: "#020617", // slate-950
      paper: "#0f172a", // slate-900
    },
    divider: "rgba(148, 163, 184, 0.18)", // slate-400 @ 18%
    text: {
      primary: "#e2e8f0", // slate-200
      secondary: "#94a3b8", // slate-400
    },
  },
  typography: {
    fontFamily: "inherit",
    fontSize: 13,
  },
  shape: { borderRadius: 8 },
});

export function MuiThemeProvider({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline enableColorScheme />
      {children}
    </ThemeProvider>
  );
}
