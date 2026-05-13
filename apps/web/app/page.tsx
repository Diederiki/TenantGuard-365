import { headers } from "next/headers";
import { redirect } from "next/navigation";

import { AppShell } from "../components/layout/AppShell";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { apiBaseUrl, fetchMe, type MeResponse } from "../lib/api";
import { DEMO_HEALTH, DEMO_ME, isDemoRequest } from "../lib/demoData";
import { SignOutButton } from "./SignOutButton";

export const dynamic = "force-dynamic";

async function fetchHealth(demo: boolean): Promise<{
  api: { ok: boolean; status: string };
  ready: { ok: boolean; status: string };
}> {
  if (demo) return DEMO_HEALTH;
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
  { n: 0, name: "Project blueprint & feasibility" },
  { n: 1, name: "Repo bootstrap" },
  { n: 2, name: "Authentication & RBAC" },
  { n: 3, name: "Microsoft Graph connection" },
  { n: 4, name: "Core data collectors" },
  { n: 5, name: "Dashboard & report engine" },
  { n: 6, name: "SharePoint deep audit" },
  { n: 7, name: "Unified audit & security ops" },
  { n: 8, name: "Content search & investigations" },
  { n: 9, name: "Remediation framework (off by default)" },
  { n: 10, name: "Enterprise hardening" },
  { n: 11, name: "Reports CRUD + export download" },
  { n: 12, name: "Alerts API + UI" },
  { n: 13, name: "Tenant connect wizard" },
  { n: 14, name: "More collectors / rules / reports" },
  { n: 15, name: "Notifications (email/webhook/Teams)" },
  { n: 16, name: "Investigations API + UI" },
  { n: 17, name: "Scheduled-reports executor" },
  { n: 18, name: "Module pages" },
  { n: 19, name: "RBAC admin API" },
  { n: 20, name: "Alerts → notifications hook" },
  { n: 21, name: "Sign-ins + directory audits collectors" },
  { n: 22, name: "SharePoint drives collector" },
  { n: 23, name: "Prompt audit pass — coverage close-out" },
];

export default async function HomePage({
  searchParams,
}: {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}) {
  const cookieHeader = (await headers()).get("cookie") ?? "";
  const params = searchParams ? await searchParams : {};
  const demo = isDemoRequest(cookieHeader, params);

  let me: MeResponse | null;
  if (demo) {
    me = DEMO_ME;
  } else {
    me = await fetchMe(cookieHeader);
    if (!me) redirect("/sign-in");
  }

  const health = await fetchHealth(demo);

  return (
    <AppShell me={me!} currentPath="/">
      <main className="px-6 py-8">
        <header className="mb-8 flex items-start justify-between gap-6">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
              Overview
              {demo ? (
                <span className="ml-3 align-middle">
                  <Badge variant="attention">DEMO MODE</Badge>
                </span>
              ) : null}
            </h1>
            <p className="mt-1 max-w-2xl text-sm text-slate-400">
              Defensive read-first platform for Microsoft 365 reporting, auditing,
              monitoring, SharePoint visibility, and security operations.
            </p>
          </div>
          <SignOutButton />
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
                Resolved from your role assignments.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="max-h-40 overflow-y-auto">
                <ul className="grid grid-cols-1 gap-1">
                  {me!.permissions.slice(0, 14).map((p) => (
                    <li key={p} className="font-mono text-xs text-slate-400">
                      {p}
                    </li>
                  ))}
                  {me!.permissions.length > 14 ? (
                    <li className="text-xs text-slate-500">
                      … and {me!.permissions.length - 14} more
                    </li>
                  ) : null}
                </ul>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Defaults</CardTitle>
              <CardDescription>What this platform does NOT do.</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1 text-xs text-slate-400">
                <li>• No remediation by default — opt-in per policy.</li>
                <li>• No raw content ingestion — content search metadata only.</li>
                <li>• No password login in production — Entra OIDC.</li>
                <li>• No Graph writes from request-path code.</li>
              </ul>
            </CardContent>
          </Card>
        </section>

        <section className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Quick links</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1.5 text-sm">
                <li><a className="text-brand-400 hover:underline" href={demo ? "/reports?demo=1" : "/reports"}>Reports</a> — 16 built-in</li>
                <li><a className="text-brand-400 hover:underline" href={demo ? "/jobs?demo=1" : "/jobs"}>Sync jobs</a> — 11 collectors</li>
                <li><a className="text-brand-400 hover:underline" href={demo ? "/security/alerts?demo=1" : "/security/alerts"}>Security alerts</a></li>
                <li><a className="text-brand-400 hover:underline" href={demo ? "/security/rules?demo=1" : "/security/rules"}>Security rules</a> — 5 built-in</li>
                <li><a className="text-brand-400 hover:underline" href={demo ? "/security/investigations?demo=1" : "/security/investigations"}>Investigations</a></li>
                <li><a className="text-brand-400 hover:underline" href={demo ? "/remediation?demo=1" : "/remediation"}>Remediation</a> — 5 policies (off)</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Modules</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1.5 text-sm">
                <li><a className="text-brand-400 hover:underline" href={demo ? "/entra?demo=1" : "/entra"}>Entra ID</a></li>
                <li><a className="text-brand-400 hover:underline" href={demo ? "/sharepoint?demo=1" : "/sharepoint"}>SharePoint Online</a></li>
                <li><a className="text-brand-400 hover:underline" href={demo ? "/service-health?demo=1" : "/service-health"}>Service health</a></li>
                <li><a className="text-brand-400 hover:underline" href={demo ? "/audit?demo=1" : "/audit"}>Audit log</a></li>
                <li><a className="text-brand-400 hover:underline" href={demo ? "/delegation?demo=1" : "/delegation"}>Delegation / RBAC</a></li>
                <li><a className="text-brand-400 hover:underline" href={demo ? "/settings/graph?demo=1" : "/settings/graph"}>Graph connection</a></li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Numbers</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1.5 text-sm text-slate-300">
                <li>Phases shipped: <span className="font-mono text-brand-400">24</span></li>
                <li>Collectors: <span className="font-mono text-brand-400">11</span></li>
                <li>Reports: <span className="font-mono text-brand-400">16</span></li>
                <li>Security rules: <span className="font-mono text-brand-400">5</span></li>
                <li>Remediation policies: <span className="font-mono text-brand-400">5</span> (off)</li>
                <li>Sensitive-info patterns: <span className="font-mono text-brand-400">5</span></li>
                <li>Postgres tables: <span className="font-mono text-brand-400">54</span></li>
              </ul>
            </CardContent>
          </Card>
        </section>

        <section className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle>Phase progress</CardTitle>
              <CardDescription>24 phases — all shipped.</CardDescription>
            </CardHeader>
            <CardContent>
              <ol className="grid grid-cols-1 gap-1.5 md:grid-cols-2">
                {phases.map((p) => (
                  <li
                    key={p.n}
                    className="flex items-center justify-between gap-3 rounded px-2 py-1 hover:bg-slate-900/60"
                  >
                    <span className="text-slate-200">
                      <span className="mr-2 inline-block w-10 font-mono text-xs text-slate-500">
                        P{String(p.n).padStart(2, "0")}
                      </span>
                      {p.name}
                    </span>
                    <Badge variant="info">done</Badge>
                  </li>
                ))}
              </ol>
            </CardContent>
          </Card>
        </section>

        <footer className="mt-10 text-xs text-slate-500">
          <span className="font-mono">tg365-web 0.1.0</span>
        </footer>
      </main>
    </AppShell>
  );
}
