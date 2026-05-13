"use client";

import { useState } from "react";

import { csrfHeader } from "../lib/api";

export function SignOutButton() {
  const [busy, setBusy] = useState(false);
  return (
    <button
      type="button"
      disabled={busy}
      onClick={async () => {
        setBusy(true);
        document.cookie = "tg365_demo=; path=/; max-age=0; samesite=lax";
        try {
          const base = process.env.NEXT_PUBLIC_API_URL ?? "";
          await fetch(`${base}/auth/logout`, {
            method: "POST",
            credentials: "include",
            headers: csrfHeader(),
          });
        } catch {
          /* ignore — demo mode has no real session to drop */
        }
        window.location.href = "/sign-in";
      }}
      className="rounded-md border border-slate-700 px-3 py-1 text-xs text-slate-300 hover:bg-slate-800 disabled:opacity-50"
    >
      {busy ? "Signing out…" : "Sign out"}
    </button>
  );
}
