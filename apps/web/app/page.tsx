import { headers } from "next/headers";
import { redirect } from "next/navigation";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { apiBaseUrl, fetchMe, type MeResponse } from "../lib/api";
import { SignOutButton } from "./SignOutButton";

export const dynamic = "force-dynamic";

async function fetchHealth(): Promise<{
  api: { ok: boolean; status: string };
  ready: { ok: boolean; status: string };
}> {
  const base = apiBaseUrl({ serverSide: true });
  try {
    const [h, r] = await Promise.all([
      fetch(`${base}/healthz`, { cache: "no-store" }),
      fetch(`${base}/readyz`, { cache: "no-store" }),
    ]);
    return {
      api: { ok: h.ok, status: h.ok ? "ok" : `${h.status}` },
      ready: { ok: r.ok, status: r.ok ? "ok" : "degraded" },
    };
  } catch {
    return {
      api: { ok: false, status: "unreachable" },
      ready: { ok: false, status: "unreachable" },
    };
  }
}

const phases = [
  { n: 0, name: "Project blueprint & feasibility", state: "done" },
  { n: 1, name: "Repo bootstrap", state: "done" },
  { n: 2, name: "Authentication & RBAC", state: "done" },
  { n: 3, name: "Microsoft Graph connection center", state: "active" },
  { n: 4, name: "Core data collectors", state: "todo" },
  { n: 5, name: "Dashboard & report engine", state: "todo" },
  { n: 6, name: "SharePoint deep audit", state: "todo" },
  { n: 7, name: "Unified audit & security ops", state: "todo" },
  { n: 8, name: "Content search & investigations", state: "todo" },
  { n: 9, name: "Remediation framework (off by default)", state: "todo" },
  { n: 10, name: "Enterprise hardening", state: "todo" },
];

export default async function HomePage() {
  const cookieHeader = (await headers()).get("cookie") ?? "";
  const me: MeResponse | null = await fetchMe(cookieHeader);
  if (!me) redirect("/sign-in");

  const health = await fetchHealth();

  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <header className="mb-10 flex items-start justify-between gap-6">
        <div>
          <p className="mb-2 text-sm font-medium uppercase tracking-widest text-brand-400">
            TenantGuard / Internal
          </p>
          <h1 className="text-4xl font-semibold tracking-tight text-slate-50">
            M365 Enterprise Control Center
          </h1>
          <p className="mt-3 max-w-2xl text-slate-400">
            Defensive read-first platform for Microsoft 365 reporting, auditing,
            and security operations.
          </p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <div className="text-right">
            <div className="text-sm font-medium text-slate-100">{me.display_name}</div>
            <div className="text-xs text-slate-500">{me.email}</div>
          </div>
          <div className="flex gap-2">
            {me.role_keys.map((r) => (
              <Badge key={r} variant="info">
                {r}
              </Badge>
            ))}
          </div>
          <SignOutButton />
        </div>
      </header>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Stack health</CardTitle>
            <CardDescription>API + dependency reachability.</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1">
              <li className="flex items-center justify-between">
                <span>API</span>
                <Badge variant={health.api.ok ? "info" : "critical"}>
                  {health.api.status}
                </Badge>
              </li>
              <li className="flex items-center justify-between">
                <span>Dependencies</span>
                <Badge variant={health.ready.ok ? "info" : "attention"}>
                  {health.ready.status}
                </Badge>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Your access</CardTitle>
            <CardDescription>
              Resolved from your role assignments. Backend enforces, the UI only
              reflects.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="max-h-40 overflow-y-auto">
              <ul className="grid grid-cols-1 gap-1">
                {me.permissions.map((p) => (
                  <li key={p} className="font-mono text-xs text-slate-400">
                    {p}
                  </li>
                ))}
                {me.permissions.length === 0 ? (
                  <li className="text-xs text-slate-500">no permissions</li>
                ) : null}
              </ul>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Audit</CardTitle>
            <CardDescription>
              Every privileged action is recorded with an append-only trigger at
              the database layer.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {me.permissions.includes("audit.read") || me.permissions.includes("platform.admin") ? (
              <a className="text-sm text-brand-400 hover:underline" href="/audit">
                Open audit viewer →
              </a>
            ) : (
              <span className="text-xs text-slate-500">
                Requires <code className="font-mono">audit.read</code>.
              </span>
            )}
          </CardContent>
        </Card>
      </section>

      <section className="mt-10">
        <Card>
          <CardHeader>
            <CardTitle>Phase progress</CardTitle>
            <CardDescription>Phased delivery plan; one slice at a time.</CardDescription>
          </CardHeader>
          <CardContent>
            <ol className="space-y-1.5">
              {phases.map((p) => (
                <li key={p.n} className="flex items-center justify-between gap-3">
                  <span className="text-slate-200">
                    <span className="mr-2 inline-block w-10 font-mono text-xs text-slate-500">
                      P{String(p.n).padStart(2, "0")}
                    </span>
                    {p.name}
                  </span>
                  <Badge
                    variant={
                      p.state === "done"
                        ? "info"
                        : p.state === "active"
                          ? "attention"
                          : "muted"
                    }
                  >
                    {p.state}
                  </Badge>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>
      </section>

      <footer className="mt-12 text-xs text-slate-500">
        <span className="font-mono">tg365-web 0.1.0</span>
      </footer>
    </main>
  );
}
