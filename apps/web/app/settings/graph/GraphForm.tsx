"use client";

import { useState } from "react";

type Settings = {
  tenant_id: string;
  entra_tenant_id: string | null;
  portal_client_id: string | null;
  collector_client_id: string | null;
  portal_secret_present: boolean;
  collector_secret_present: boolean;
  feature_2fa_required: boolean;
  allow_local_password: boolean;
};

export function GraphForm({
  tenantId,
  initial,
  demo,
}: {
  tenantId: string;
  initial: Settings;
  demo: boolean;
}) {
  const [entraTenant, setEntraTenant] = useState(initial.entra_tenant_id ?? "");
  const [portalId, setPortalId] = useState(initial.portal_client_id ?? "");
  const [portalSecret, setPortalSecret] = useState("");
  const [collectorId, setCollectorId] = useState(initial.collector_client_id ?? "");
  const [collectorSecret, setCollectorSecret] = useState("");
  const [require2fa, setRequire2fa] = useState(initial.feature_2fa_required);
  const [allowLocal, setAllowLocal] = useState(initial.allow_local_password);
  const [status, setStatus] = useState<"idle" | "saving" | "ok" | "err">("idle");
  const [errMsg, setErrMsg] = useState<string | null>(null);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setStatus("saving");
    setErrMsg(null);

    if (demo) {
      // Demo mode: pretend we saved.
      await new Promise((r) => setTimeout(r, 400));
      setStatus("ok");
      return;
    }

    const base = process.env.NEXT_PUBLIC_API_URL ?? "";
    const csrf = document.cookie.match(/(?:^|; )tg365_csrf=([^;]+)/);
    const csrfHeader: Record<string, string> = csrf
      ? { "X-CSRF-Token": decodeURIComponent(csrf[1]) }
      : {};
    try {
      const r = await fetch(`${base}/api/settings/graph/${tenantId}`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", ...csrfHeader },
        body: JSON.stringify({
          entra_tenant_id: entraTenant || null,
          portal_client_id: portalId || null,
          collector_client_id: collectorId || null,
          portal_client_secret: portalSecret || null,
          collector_client_secret: collectorSecret || null,
          feature_2fa_required: require2fa,
          allow_local_password: allowLocal,
        }),
      });
      if (!r.ok) {
        setStatus("err");
        setErrMsg(`${r.status} — ${await r.text()}`);
        return;
      }
      setStatus("ok");
      setPortalSecret("");
      setCollectorSecret("");
    } catch (err) {
      setStatus("err");
      setErrMsg(String(err));
    }
  }

  return (
    <form onSubmit={save} className="space-y-5">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Field
          label="Entra tenant ID"
          value={entraTenant}
          onChange={setEntraTenant}
          placeholder="00000000-aaaa-bbbb-cccc-000000000000"
        />
        <Field
          label="Portal app — Application (client) ID"
          value={portalId}
          onChange={setPortalId}
          placeholder="tg365-portal app registration"
        />
        <Field
          label={`Portal app — client secret ${initial.portal_secret_present ? "(stored ✓)" : ""}`}
          value={portalSecret}
          onChange={setPortalSecret}
          placeholder="leave blank to keep current"
          type="password"
        />
        <Field
          label="Collector app — Application (client) ID"
          value={collectorId}
          onChange={setCollectorId}
          placeholder="tg365-collector app registration"
        />
        <Field
          label={`Collector app — client secret ${initial.collector_secret_present ? "(stored ✓)" : ""}`}
          value={collectorSecret}
          onChange={setCollectorSecret}
          placeholder="leave blank to keep current"
          type="password"
        />
      </div>

      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm text-slate-300">
          <input
            type="checkbox"
            checked={require2fa}
            onChange={(e) => setRequire2fa(e.target.checked)}
            className="h-4 w-4 rounded border-slate-700 bg-slate-900"
          />
          Require TOTP 2FA for non-Entra (local + mock) users
        </label>
        <label className="flex items-center gap-2 text-sm text-slate-300">
          <input
            type="checkbox"
            checked={allowLocal}
            onChange={(e) => setAllowLocal(e.target.checked)}
            className="h-4 w-4 rounded border-slate-700 bg-slate-900"
          />
          Allow local password sign-in (break-glass only — keep off when Entra SSO is up)
        </label>
      </div>

      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={status === "saving"}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-500 disabled:opacity-50"
        >
          {status === "saving" ? "Saving…" : "Save settings"}
        </button>
        {status === "ok" ? (
          <span className="text-xs text-emerald-300">Saved.</span>
        ) : null}
        {status === "err" && errMsg ? (
          <span className="text-xs text-rose-300">{errMsg}</span>
        ) : null}
      </div>
    </form>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
}) {
  return (
    <label className="block text-sm text-slate-300">
      <span className="mb-1 block text-xs uppercase tracking-wider text-slate-500">
        {label}
      </span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-md border border-slate-800 bg-slate-900 px-3 py-2 font-mono text-xs text-slate-100 outline-none focus:border-brand-500"
      />
    </label>
  );
}
