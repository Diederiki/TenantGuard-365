"use client";

import { useState, useEffect } from "react";
import { setTheme } from "../providers/ThemeProvider";

export function ThemeToggle() {
  const [current, setCurrent] = useState<"light" | "dark">("dark");
  useEffect(() => {
    const m = document.cookie.match(/(?:^|; )tg365_theme=([^;]+)/);
    if (m) setCurrent(decodeURIComponent(m[1]) === "light" ? "light" : "dark");
  }, []);
  return (
    <button
      type="button"
      onClick={() => {
        const next = current === "dark" ? "light" : "dark";
        setCurrent(next);
        setTheme(next);
      }}
      className="rounded-md border border-slate-700 px-2 py-1 text-xs text-slate-300 hover:bg-slate-800"
      aria-label="Toggle theme"
    >
      {current === "dark" ? "☾ Dark" : "☀ Light"}
    </button>
  );
}
