import {
  AlertTriangle,
  BarChart3,
  Bell,
  Briefcase,
  Building2,
  Gauge,
  Link2,
  Mail,
  Search,
  Shield,
  ShieldCheck,
  Sparkles,
  Users,
  Users2,
} from "lucide-react";
import { headers } from "next/headers";
import { redirect } from "next/navigation";

import { ActivityFeed } from "../components/feed/ActivityFeed";
import { AppShell } from "../components/layout/AppShell";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { KpiTile } from "../components/ui/KpiTile";
import { StatusDot } from "../components/ui/StatusDot";
import { apiBaseUrl, fetchMe, type MeResponse } from "../lib/api";
import {
  DEMO_HEALTH,
  DEMO_ME,
  DEMO_REPORTING_KPIS,
  isDemoCookie,
  isDemoRequest,
  type ReportingKpis,
} from "../lib/demoData";

export const dynamic = "force-dynamic";

type Health = { api: { ok: boolean; status: string }; ready: { ok: boolean; status: string } };

async function fetchHealth(cookie: string, demo: boolean): Promise<Health> {
  if (demo) return DEMO_HEALTH;
  const base = apiBaseUrl({ serverSide: true });
  try {
    const [h, r] = await Promise.all([
      fetch(`${base}/healthz`, { cache: "no-store", headers: { cookie } }),
      fetch(`${base}/readyz`, { cache: "no-store", headers: { cookie } }),
    ]);
    return {
      api: { ok: h.ok, status: h.ok ? "ok" : `${h.status}` },
      ready: { ok: r.ok, status: r.ok ? "ok" : "degraded" },
    };
  } catch {
    return { api: { ok: false, status: "unreachable" }, ready: { ok: false, status: "unreachable" } };
  }
}

async function fetchKpis(cookie: string): Promise<{ kpis: ReportingKpis; source: "live" | "demo" }> {
  if (isDemoCookie(cookie)) return { kpis: DEMO_REPORTING_KPIS, source: "demo" };
  const base = apiBaseUrl({ serverSide: true });
  try {
    const r = await fetch(`${base}/api/reporting/dashboard`, {
      headers: { cookie },
      cache: "no-store",
    });
    if (r.ok) {
      const body = (await r.json()) as { kpis: ReportingKpis };
      return { kpis: body.kpis, source: "live" };
    }
  } catch {
    // fall through
  }
  return { kpis: DEMO_REPORTING_KPIS, source: "demo" };
}

const QUICK_ACTIONS = [
  { href: "/reporting", label: "Reporting overview", desc: "KPIs + charts", icon: BarChart3, accent: "from-sky-500/20" },
  { href: "/audit", label: "Audit log", desc: "Every privileged action", icon: Search, accent: "from-violet-500/20" },
  { href: "/security/alerts", label: "Security alerts", desc: "Open + critical", icon: Shield, accent: "from-rose-500/20" },
  { href: "/settings/graph", label: "Graph connection", desc: "App registration + test", icon: Sparkles, accent: "from-emerald-500/20" },
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

  const health = await fetchHealth(cookieHeader, demo);
  const { kpis: k, source } = await fetchKpis(cookieHeader);

  const license_pct = k.licenses_purchased
    ? Math.round((k.licenses_consumed / k.licenses_purchased) * 100)
    : 0;

  return (
    <AppShell me={me!} currentPath="/">
      <main className="px-6 py-6">
        {/* Hero */}
        <section className="relative mb-6 overflow-hidden rounded-3xl border border-slate-800/60 bg-gradient-to-br from-brand-500/15 via-slate-900/40 to-violet-500/10 p-6 ring-1 ring-white/5 shadow-glass">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(60%_50%_at_20%_0%,rgba(59,130,246,0.18)_0%,transparent_60%),radial-gradient(50%_40%_at_85%_30%,rgba(168,85,247,0.15)_0%,transparent_60%)]" />
          <div className="relative flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="mb-1 inline-flex items-center gap-2 text-xs uppercase tracking-widest text-brand-300">
                <Sparkles className="h-3.5 w-3.5" /> Welcome back, {me!.display_name.split(" ")[0]}
              </p>
              <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
                TenantGuard 365 control center
              </h1>
              <p className="mt-1 max-w-2xl text-sm text-slate-400">
                Live posture of your Microsoft 365 tenant. Audits, sharing risk, sign-ins, and
                license usage in one place.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="flex items-center gap-2 rounded-xl border border-slate-800/60 bg-slate-900/60 px-3 py-1.5 text-xs text-slate-300 ring-1 ring-white/5">
                <StatusDot tone={health.ready.ok ? "ok" : "danger"} />
                {health.ready.ok ? "All systems green" : `Degraded: ${health.ready.status}`}
              </span>
              <span className="rounded-xl border border-slate-800/60 bg-slate-900/60 px-3 py-1.5 text-xs text-slate-300 ring-1 ring-white/5">
                data: <span className={source === "live" ? "text-emerald-300" : "text-slate-400"}>{source}</span>
              </span>
            </div>
          </div>
        </section>

        {/* KPI strip */}
        <section className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
          <KpiTile
            label="Users"
            value={k.total_users}
            delta={`${k.active_users_30d} active 30d`}
            icon={Users}
            tone="info"
            href="/entra/users"
          />
          <KpiTile
            label="Guests"
            value={k.guest_users}
            icon={Users2}
            tone={k.guest_users > 50 ? "warn" : "info"}
            href="/entra/users"
          />
          <KpiTile
            label="Privileged admins"
            value={k.privileged_admins}
            icon={ShieldCheck}
            tone={k.privileged_admins > 5 ? "danger" : "ok"}
            href="/entra/roles"
          />
          <KpiTile
            label="Licenses"
            value={`${k.licenses_consumed}/${k.licenses_purchased}`}
            delta={`${license_pct}% used`}
            icon={Briefcase}
            tone={license_pct > 95 ? "danger" : license_pct > 85 ? "warn" : "info"}
            href="/entra/licenses"
          />
          <KpiTile
            label="SharePoint sites"
            value={k.sites}
            icon={Building2}
            tone="info"
            href="/sharepoint/sites"
          />
          <KpiTile
            label="Open alerts"
            value={k.alerts_open}
            delta={`${k.alerts_critical} critical`}
            icon={AlertTriangle}
            tone={k.alerts_critical > 0 ? "danger" : "ok"}
            href="/security/alerts"
          />
        </section>

        {/* Risk strip */}
        <section className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-4">
          <KpiTile
            label="Anonymous links"
            value={k.anonymous_links}
            icon={Link2}
            tone={k.anonymous_links > 0 ? "danger" : "ok"}
            href="/sharepoint/sharing-links"
          />
          <KpiTile
            label="External forwarding"
            value={k.external_forwarding_rules}
            icon={Mail}
            tone={k.external_forwarding_rules > 0 ? "danger" : "ok"}
            href="/exchange/forwarding-risk"
          />
          <KpiTile
            label="MFA registered"
            value={`${k.mfa_registered_pct}%`}
            icon={ShieldCheck}
            tone={k.mfa_registered_pct < 95 ? "warn" : "ok"}
            href="/entra/users"
          />
          <KpiTile
            label="Inactive mailboxes"
            value={k.inactive_mailboxes}
            icon={Mail}
            tone={k.inactive_mailboxes > 10 ? "warn" : "info"}
            href="/exchange/mailboxes"
          />
        </section>

        {/* Two-column: activity inbox + quick actions */}
        <section className="grid grid-cols-1 gap-4 xl:grid-cols-3">
          <div className="xl:col-span-2">
            <ActivityFeed cookie={cookieHeader} />
          </div>

          <div className="space-y-4">
            <Card variant="glass-1">
              <CardHeader>
                <CardTitle>Quick actions</CardTitle>
                <CardDescription>Jump straight to the most common workflows.</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-1 gap-2">
                {QUICK_ACTIONS.map((q) => {
                  const Icon = q.icon;
                  return (
                    <a
                      key={q.href}
                      href={q.href}
                      className={`group relative overflow-hidden rounded-xl border border-slate-800/60 bg-gradient-to-br ${q.accent} to-transparent p-3 ring-1 ring-white/5 hover:ring-brand-500/40`}
                    >
                      <div className="flex items-center gap-3">
                        <div className="grid h-9 w-9 place-items-center rounded-lg bg-slate-900/60 text-slate-200 ring-1 ring-white/10">
                          <Icon className="h-4 w-4" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="text-sm font-medium text-slate-100">{q.label}</div>
                          <div className="text-xs text-slate-400">{q.desc}</div>
                        </div>
                        <span className="text-slate-500 group-hover:text-slate-300">→</span>
                      </div>
                    </a>
                  );
                })}
              </CardContent>
            </Card>

            <Card variant="glass">
              <CardHeader>
                <CardTitle>Infrastructure</CardTitle>
                <CardDescription>Live platform dependency status.</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center justify-between rounded-lg border border-slate-800/60 bg-slate-900/40 px-3 py-2">
                    <span className="flex items-center gap-2 text-slate-200">
                      <Gauge className="h-3.5 w-3.5 text-slate-500" /> API health
                    </span>
                    <span className="flex items-center gap-2 text-xs text-slate-400">
                      <StatusDot tone={health.api.ok ? "ok" : "danger"} />
                      {health.api.status}
                    </span>
                  </li>
                  <li className="flex items-center justify-between rounded-lg border border-slate-800/60 bg-slate-900/40 px-3 py-2">
                    <span className="flex items-center gap-2 text-slate-200">
                      <Bell className="h-3.5 w-3.5 text-slate-500" /> Readiness
                    </span>
                    <span className="flex items-center gap-2 text-xs text-slate-400">
                      <StatusDot tone={health.ready.ok ? "ok" : "warn"} />
                      {health.ready.status}
                    </span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </section>
      </main>
    </AppShell>
  );
}
