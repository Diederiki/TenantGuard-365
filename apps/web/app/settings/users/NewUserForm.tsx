"use client";

import { useState } from "react";

const ROLES = [
  { key: "platform_admin", label: "Platform Admin" },
  { key: "security_analyst", label: "Security Analyst" },
  { key: "sharepoint_auditor", label: "SharePoint Auditor" },
  { key: "helpdesk", label: "Helpdesk" },
  { key: "readonly_auditor", label: "Read-only Auditor" },
  { key: "report_only", label: "Report-only" },
];

export function NewUserForm({ demo }: { demo: boolean }) {
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [authMethod, setAuthMethod] = useState<"entra" | "local" | "mock">("entra");
  const [requireTotp, setRequireTotp] = useState(true);
  const [selectedRoles, setSelectedRoles] = useState<string[]>(["readonly_auditor"]);
  const [status, setStatus] = useState<"idle" | "saving" | "ok" | "err">("idle");
  const [errMsg, setErrMsg] = useState<string | null>(null);
  const [createdId, setCreatedId] = useState<string | null>(null);

  function toggleRole(k: string) {
    setSelectedRoles((rs) =>
      rs.includes(k) ? rs.filter((r) => r !== k) : [...rs, k],
    );
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("saving");
    setErrMsg(null);
    if (demo) {
      await new Promise((r) => setTimeout(r, 400));
      setCreatedId("u-demo-" + Math.random().toString(36).slice(2, 8));
      setStatus("ok");
      return;
    }
    const base = process.env.NEXT_PUBLIC_API_URL ?? "";
    const csrf = document.cookie.match(/(?:^|; )tg365_csrf=([^;]+)/);
    const csrfHeader: Record<string, string> = csrf
      ? { "X-CSRF-Token": decodeURIComponent(csrf[1]) }
      : {};
    try {
      const r = await fetch(`${base}/api/settings/users`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", ...csrfHeader },
        body: JSON.stringify({
          email,
          display_name: displayName,
          auth_method: authMethod,
          require_totp: requireTotp,
          role_keys: selectedRoles,
        }),
      });
      if (!r.ok) {
        setStatus("err");
        setErrMsg(`${r.status} — ${await r.text()}`);
        return;
      }
      const body = await r.json();
      setCreatedId(body.id);
      setStatus("ok");
    } catch (err) {
      setStatus("err");
      setErrMsg(String(err));
    }
  }

  if (status === "ok" && createdId) {
    const totpHref = `/settings/users/${createdId}/totp${demo ? "?demo=1" : ""}`;
    return (
      <div className="space-y-3">
        <div className="rounded-md border border-emerald-800 bg-emerald-950/50 p-3 text-sm text-emerald-200">
          User <code className="font-mono">{email || "(new user)"}</code> created.
          {authMethod === "entra" ? (
            <p className="mt-1 text-xs text-emerald-300/80">
              They sign in via Microsoft Entra ID. Microsoft enforces MFA per
              your Conditional Access policy.
            </p>
          ) : (
            <p className="mt-1 text-xs text-emerald-300/80">
              Set up their TOTP authenticator next to enable 2FA sign-in.
            </p>
          )}
        </div>
        {authMethod !== "entra" ? (
          <a
            href={totpHref}
            className="inline-block rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-500"
          >
            Set up TOTP →
          </a>
        ) : null}
        <a
          href={`/settings/users${demo ? "?demo=1" : ""}`}
          className="ml-2 inline-block text-sm text-brand-400 hover:underline"
        >
          ← Back to users
        </a>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="space-y-5">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <label className="block text-sm text-slate-300">
          <span className="mb-1 block text-xs uppercase tracking-wider text-slate-500">
            Email
          </span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="admin2@yourcorp.com"
            required
            className="w-full rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-brand-500"
          />
        </label>
        <label className="block text-sm text-slate-300">
          <span className="mb-1 block text-xs uppercase tracking-wider text-slate-500">
            Display name
          </span>
          <input
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="Anna Admin"
            required
            className="w-full rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none focus:border-brand-500"
          />
        </label>
      </div>

      <fieldset className="space-y-2">
        <legend className="text-xs uppercase tracking-wider text-slate-500">
          Sign-in method
        </legend>
        <label className="flex items-start gap-2 text-sm text-slate-300">
          <input
            type="radio"
            name="auth"
            value="entra"
            checked={authMethod === "entra"}
            onChange={() => setAuthMethod("entra")}
            className="mt-1"
          />
          <span>
            <strong>Microsoft Entra SSO (recommended)</strong>
            <span className="block text-xs text-slate-500">
              MFA handled by your Conditional Access policy.
            </span>
          </span>
        </label>
        <label className="flex items-start gap-2 text-sm text-slate-300">
          <input
            type="radio"
            name="auth"
            value="local"
            checked={authMethod === "local"}
            onChange={() => setAuthMethod("local")}
            className="mt-1"
          />
          <span>
            <strong>Local password + TOTP (break-glass)</strong>
            <span className="block text-xs text-slate-500">
              Only enable when explicitly allowed in Settings → Graph.
            </span>
          </span>
        </label>
        <label className="flex items-start gap-2 text-sm text-slate-300">
          <input
            type="radio"
            name="auth"
            value="mock"
            checked={authMethod === "mock"}
            onChange={() => setAuthMethod("mock")}
            className="mt-1"
          />
          <span>
            <strong>Mock (development only)</strong>
            <span className="block text-xs text-slate-500">
              Forbidden in <code className="font-mono">ENVIRONMENT=production</code>.
            </span>
          </span>
        </label>
      </fieldset>

      <label className="flex items-center gap-2 text-sm text-slate-300">
        <input
          type="checkbox"
          checked={requireTotp}
          onChange={(e) => setRequireTotp(e.target.checked)}
          className="h-4 w-4 rounded border-slate-700 bg-slate-900"
          disabled={authMethod === "entra"}
        />
        Require TOTP enrollment on first sign-in
        {authMethod === "entra" ? (
          <span className="text-xs text-slate-500">
            (Entra users get MFA from your CA policy)
          </span>
        ) : null}
      </label>

      <fieldset>
        <legend className="text-xs uppercase tracking-wider text-slate-500">
          Roles
        </legend>
        <div className="mt-2 grid grid-cols-1 gap-1.5 md:grid-cols-2">
          {ROLES.map((r) => (
            <label
              key={r.key}
              className="flex items-center gap-2 rounded-md border border-slate-800 bg-slate-900/40 px-3 py-1.5 text-sm text-slate-300"
            >
              <input
                type="checkbox"
                checked={selectedRoles.includes(r.key)}
                onChange={() => toggleRole(r.key)}
                className="h-4 w-4 rounded border-slate-700 bg-slate-900"
              />
              {r.label}
              <span className="ml-auto font-mono text-xs text-slate-500">
                {r.key}
              </span>
            </label>
          ))}
        </div>
      </fieldset>

      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={status === "saving"}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-500 disabled:opacity-50"
        >
          {status === "saving" ? "Creating…" : "Create user"}
        </button>
        {status === "err" && errMsg ? (
          <span className="text-xs text-rose-300">{errMsg}</span>
        ) : null}
      </div>
    </form>
  );
}
