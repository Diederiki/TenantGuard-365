import { headers } from "next/headers";
import { redirect } from "next/navigation";

import { AppShell } from "../../components/layout/AppShell";
import { Badge } from "../../components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import { apiBaseUrl, fetchMe } from "../../lib/api";
import {
  DEMO_ALERT_SEVERITY,
  DEMO_AUDIT_TREND,
  DEMO_LICENSE_USE,
  DEMO_REPORTING_KPIS,
  DEMO_SHARING_RISK,
  DEMO_SIGNIN_RISK,
  DEMO_TOP_SITES,
  isDemoCookie,
  type ReportingKpis,
} from "../../lib/demoData";
import {
  AlertSeverityChart,
  AuditTrendChart,
  LicenseUseChart,
  SharingRiskChart,
  SigninRiskChart,
} from "./Charts";

export const dynamic = "force-dynamic";

type Dashboard = {
  kpis: ReportingKpis;
  audit_trend: typeof DEMO_AUDIT_TREND;
  signin_risk: typeof DEMO_SIGNIN_RISK;
  license_use: typeof DEMO_LICENSE_USE;
  alert_severity: typeof DEMO_ALERT_SEVERITY;
  sharing_risk: typeof DEMO_SHARING_RISK;
  top_sites: typeof DEMO_TOP_SITES;
  source: "live" | "demo";
};

async function fetchDashboard(cookie: string): Promise<Dashboard> {
  if (isDemoCookie(cookie)) {
    return {
      kpis: DEMO_REPORTING_KPIS,
      audit_trend: DEMO_AUDIT_TREND,
      signin_risk: DEMO_SIGNIN_RISK,
      license_use: DEMO_LICENSE_USE,
      alert_severity: DEMO_ALERT_SEVERITY,
      sharing_risk: DEMO_SHARING_RISK,
      top_sites: DEMO_TOP_SITES,
      source: "demo",
    };
  }
  const base = apiBaseUrl({ serverSide: true });
  try {
    const r = await fetch(`${base}/api/reporting/dashboard`, {
      headers: { cookie },
      cache: "no-store",
    });
    if (r.ok) {
      const body = (await r.json()) as Omit<Dashboard, "source">;
      return { ...body, source: "live" };
    }
  } catch {
    // fall through
  }
  // Fall back to demo so the page is always useful.
  return {
    kpis: DEMO_REPORTING_KPIS,
    audit_trend: DEMO_AUDIT_TREND,
    signin_risk: DEMO_SIGNIN_RISK,
    license_use: DEMO_LICENSE_USE,
    alert_severity: DEMO_ALERT_SEVERITY,
    sharing_risk: DEMO_SHARING_RISK,
    top_sites: DEMO_TOP_SITES,
    source: "demo",
  };
}

function Kpi({
  label,
  value,
  delta,
  tone,
}: {
  label: string;
  value: number | string;
  delta?: string;
  tone?: "info" | "attention" | "critical" | "muted";
}) {
  return (
    <Card>
      <CardHeader>
        <CardDescription>{label}</CardDescription>
        <CardTitle>
          {value}
          {delta ? (
            <span className="ml-2 text-xs text-slate-400">{delta}</span>
          ) : null}
        </CardTitle>
      </CardHeader>
      {tone ? (
        <CardContent>
          <Badge variant={tone}>{tone}</Badge>
        </CardContent>
      ) : null}
    </Card>
  );
}

export default async function ReportingDashboardPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");
  const data = await fetchDashboard(cookie);

  const k = data.kpis;
  const license_pct = Math.round((k.licenses_consumed / k.licenses_purchased) * 100);

  return (
    <AppShell me={me} currentPath="/reporting">
      <main className="px-6 py-8">
        <header className="mb-6 flex items-end justify-between">
          <div>
            <p className="mb-1 text-xs font-medium uppercase tracking-widest text-brand-400">
              Reports
            </p>
            <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
              Reporting overview
            </h1>
            <p className="mt-1 max-w-3xl text-sm text-slate-400">
              Top-line health of the M365 tenant. Click a tile to drill into
              the underlying report.
            </p>
          </div>
          <Badge variant={data.source === "live" ? "info" : "muted"}>
            data: {data.source}
          </Badge>
        </header>

        <div className="mb-4 grid grid-cols-2 gap-2 md:grid-cols-4 xl:grid-cols-7">
          <Kpi label="Total users" value={k.total_users} delta={`${k.active_users_30d} active 30d`} />
          <Kpi label="Guest users" value={k.guest_users} tone={k.guest_users > 50 ? "attention" : "info"} />
          <Kpi label="Privileged admins" value={k.privileged_admins} tone={k.privileged_admins > 5 ? "critical" : "info"} />
          <Kpi label="Licenses" value={`${k.licenses_consumed}/${k.licenses_purchased}`} delta={`${license_pct}%`} tone={license_pct > 95 ? "critical" : license_pct > 85 ? "attention" : "info"} />
          <Kpi label="SharePoint sites" value={k.sites} />
          <Kpi label="Anonymous links" value={k.anonymous_links} tone={k.anonymous_links > 0 ? "critical" : "info"} />
          <Kpi label="Open alerts" value={k.alerts_open} delta={`${k.alerts_critical} critical`} tone={k.alerts_critical > 0 ? "critical" : "info"} />
        </div>

        <div className="mb-4 grid grid-cols-2 gap-2 md:grid-cols-4">
          <Kpi label="External users" value={k.external_users} tone="attention" />
          <Kpi label="External fwd rules" value={k.external_forwarding_rules} tone={k.external_forwarding_rules > 0 ? "critical" : "info"} />
          <Kpi label="MFA registered" value={`${k.mfa_registered_pct}%`} tone={k.mfa_registered_pct < 95 ? "attention" : "info"} />
          <Kpi label="Inactive mailboxes" value={k.inactive_mailboxes} tone="attention" />
        </div>

        <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Audit volume (7d)</CardTitle>
              <CardDescription>
                Total events with failure overlay. Weekend dip is expected.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AuditTrendChart data={data.audit_trend} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Sign-in risk (7d)</CardTitle>
              <CardDescription>
                Stacked by risk class. Anything in red is investigated next.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <SigninRiskChart data={data.signin_risk} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>License utilisation</CardTitle>
              <CardDescription>Used vs free per SKU.</CardDescription>
            </CardHeader>
            <CardContent>
              <LicenseUseChart data={data.license_use} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Sharing-link risk distribution</CardTitle>
              <CardDescription>Across all tenant SharePoint + OneDrive resources.</CardDescription>
            </CardHeader>
            <CardContent>
              <SharingRiskChart data={data.sharing_risk} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Alerts by severity</CardTitle>
              <CardDescription>Open vs closed in the last 30 days.</CardDescription>
            </CardHeader>
            <CardContent>
              <AlertSeverityChart data={data.alert_severity} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Top SharePoint sites</CardTitle>
              <CardDescription>By storage, external users, sharing links.</CardDescription>
            </CardHeader>
            <CardContent>
              <table className="min-w-full text-left text-sm">
                <thead className="text-xs uppercase tracking-wider text-slate-500">
                  <tr>
                    <th className="py-1">Site</th>
                    <th className="py-1">Storage</th>
                    <th className="py-1">External</th>
                    <th className="py-1">Links</th>
                  </tr>
                </thead>
                <tbody>
                  {data.top_sites.map((s) => (
                    <tr key={s.site} className="border-t border-slate-800/80 text-slate-300">
                      <td className="py-1 font-mono text-xs">
                        <a className="text-brand-400 hover:underline" href="/sharepoint/sites">
                          {s.site}
                        </a>
                      </td>
                      <td className="py-1 font-mono text-xs">{s.storage_gb} GB</td>
                      <td className="py-1 font-mono text-xs">{s.ext_users}</td>
                      <td className="py-1 font-mono text-xs">{s.links}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </div>
      </main>
    </AppShell>
  );
}
