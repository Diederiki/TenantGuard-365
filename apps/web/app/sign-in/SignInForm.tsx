"use client";

import { useState } from "react";

export function SignInForm() {
  const [email, setEmail] = useState("admin@dev.local");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function signInMock(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const base = process.env.NEXT_PUBLIC_API_URL ?? "";
      const r = await fetch(
        `${base}/auth/login/mock?email=${encodeURIComponent(email)}`,
        { method: "POST", credentials: "include" },
      );
      if (!r.ok) {
        const body = await r.text();
        setError(body || `${r.status}`);
        setBusy(false);
        return;
      }
      window.location.href = "/";
    } catch (e) {
      setError(String(e));
      setBusy(false);
    }
  }

  function signInEntra() {
    const base = process.env.NEXT_PUBLIC_API_URL ?? "";
    window.location.href = `${base}/auth/login/entra?redirect_to=/`;
  }

  return (
    <div className="space-y-6">
      <form onSubmit={signInMock} className="space-y-3">
        <label className="block text-sm text-slate-300">
          Mock user email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-brand-500"
            disabled={busy}
            required
          />
        </label>
        <button
          type="submit"
          disabled={busy}
          className="w-full rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-500 disabled:opacity-50"
        >
          {busy ? "Signing in…" : "Sign in (mock)"}
        </button>
      </form>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-slate-800" />
        </div>
        <div className="relative flex justify-center text-xs">
          <span className="bg-slate-900/60 px-2 text-slate-500">or</span>
        </div>
      </div>

      <button
        type="button"
        onClick={signInEntra}
        className="w-full rounded-md border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800"
      >
        Sign in with Microsoft Entra ID
      </button>

      {error ? (
        <p className="rounded-md border border-rose-800 bg-rose-950/60 p-2 text-xs text-rose-200">
          {error}
        </p>
      ) : null}
    </div>
  );
}
