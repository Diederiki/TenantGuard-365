"use client";

import { useEffect, useState } from "react";

type EnrollResponse = { secret: string; otpauth_uri: string; qr_svg_base64?: string };

export function TotpEnroll({ userId, demo }: { userId: string; demo: boolean }) {
  const [secret, setSecret] = useState<string | null>(null);
  const [uri, setUri] = useState<string | null>(null);
  const [qr, setQr] = useState<string | null>(null);
  const [code, setCode] = useState("");
  const [status, setStatus] = useState<"idle" | "enrolling" | "ready" | "verifying" | "ok" | "err">("idle");
  const [errMsg, setErrMsg] = useState<string | null>(null);

  useEffect(() => {
    enroll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function enroll() {
    setStatus("enrolling");
    setErrMsg(null);
    if (demo) {
      // Demo: stable example. Real authenticator apps reject this code.
      const fake: EnrollResponse = {
        secret: "JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP",
        otpauth_uri:
          "otpauth://totp/TenantGuard%20365:" + userId + "?secret=JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP&issuer=TenantGuard%20365",
      };
      setSecret(fake.secret);
      setUri(fake.otpauth_uri);
      setQr(null);
      setStatus("ready");
      return;
    }
    const base = process.env.NEXT_PUBLIC_API_URL ?? "";
    const csrf = document.cookie.match(/(?:^|; )tg365_csrf=([^;]+)/);
    const csrfHeader: Record<string, string> = csrf
      ? { "X-CSRF-Token": decodeURIComponent(csrf[1]) }
      : {};
    try {
      const r = await fetch(`${base}/api/settings/users/${userId}/totp/enroll`, {
        method: "POST",
        credentials: "include",
        headers: csrfHeader,
      });
      if (!r.ok) {
        setStatus("err");
        setErrMsg(`${r.status} — ${await r.text()}`);
        return;
      }
      const body: EnrollResponse = await r.json();
      setSecret(body.secret);
      setUri(body.otpauth_uri);
      setQr(body.qr_svg_base64 ?? null);
      setStatus("ready");
    } catch (err) {
      setStatus("err");
      setErrMsg(String(err));
    }
  }

  async function verify(e: React.FormEvent) {
    e.preventDefault();
    setStatus("verifying");
    setErrMsg(null);
    if (demo) {
      await new Promise((r) => setTimeout(r, 400));
      if (code === "000000") {
        setStatus("err");
        setErrMsg("Demo mode rejects code 000000 — try any other 6-digit code.");
        return;
      }
      setStatus("ok");
      return;
    }
    const base = process.env.NEXT_PUBLIC_API_URL ?? "";
    const csrf = document.cookie.match(/(?:^|; )tg365_csrf=([^;]+)/);
    const csrfHeader: Record<string, string> = csrf
      ? { "X-CSRF-Token": decodeURIComponent(csrf[1]) }
      : {};
    try {
      const r = await fetch(`${base}/api/settings/users/${userId}/totp/verify`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", ...csrfHeader },
        body: JSON.stringify({ code }),
      });
      if (!r.ok) {
        setStatus("err");
        setErrMsg(`Invalid code (${r.status})`);
        return;
      }
      setStatus("ok");
    } catch (err) {
      setStatus("err");
      setErrMsg(String(err));
    }
  }

  if (status === "enrolling") {
    return <p className="text-sm text-slate-400">Generating secret…</p>;
  }
  if (status === "ok") {
    return (
      <div className="rounded-md border border-emerald-800 bg-emerald-950/50 p-3 text-sm text-emerald-200">
        ✓ TOTP confirmed. The user can now sign in with email + password + 6-digit code.
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div>
        <div className="text-sm font-medium text-slate-200">
          1. Add to your authenticator app
        </div>
        <p className="mt-1 text-xs text-slate-400">
          Scan this URI in Microsoft Authenticator, Google Authenticator, 1Password,
          Bitwarden, Authy, or any RFC 6238 TOTP app. Or paste the secret manually.
        </p>
        {qr ? (
          <div className="mt-3 inline-block rounded-md border border-slate-800 bg-white p-3">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={`data:image/svg+xml;base64,${qr}`}
              alt="TOTP QR code"
              className="h-44 w-44"
            />
          </div>
        ) : null}
        {uri ? (
          <pre className="mt-2 overflow-x-auto rounded-md bg-slate-950 p-3 font-mono text-[10px] text-slate-300">
            {uri}
          </pre>
        ) : null}
        {secret ? (
          <p className="mt-2 text-xs">
            <span className="text-slate-500">Secret:</span>{" "}
            <code className="rounded bg-slate-950 px-1.5 py-0.5 font-mono text-slate-200">
              {secret}
            </code>
          </p>
        ) : null}
      </div>

      <form onSubmit={verify} className="space-y-2">
        <div className="text-sm font-medium text-slate-200">
          2. Confirm with the current code
        </div>
        <input
          type="text"
          inputMode="numeric"
          autoComplete="one-time-code"
          maxLength={6}
          pattern="\d{6}"
          value={code}
          onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
          placeholder="123456"
          className="w-full max-w-xs rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-center font-mono text-lg tracking-widest text-slate-100 outline-none focus:border-brand-500"
          required
        />
        <div>
          <button
            type="submit"
            disabled={status === "verifying" || code.length !== 6}
            className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-500 disabled:opacity-50"
          >
            {status === "verifying" ? "Verifying…" : "Verify + activate"}
          </button>
        </div>
        {errMsg ? (
          <p className="text-xs text-rose-300">{errMsg}</p>
        ) : null}
      </form>
    </div>
  );
}
