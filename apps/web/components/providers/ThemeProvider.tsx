"use client";

import { useEffect } from "react";

/**
 * Minimal theme provider — reads `tg365_theme` cookie and applies the
 * `dark` / `light` class on <html>. Defaults to dark.
 */
export function ThemeProvider() {
  useEffect(() => {
    const m = document.cookie.match(/(?:^|; )tg365_theme=([^;]+)/);
    const theme = m ? decodeURIComponent(m[1]) : "dark";
    document.documentElement.classList.remove("light", "dark");
    document.documentElement.classList.add(theme === "light" ? "light" : "dark");
  }, []);
  return null;
}

export function setTheme(theme: "light" | "dark") {
  document.cookie = `tg365_theme=${theme}; path=/; max-age=31536000; samesite=lax`;
  document.documentElement.classList.remove("light", "dark");
  document.documentElement.classList.add(theme);
}
