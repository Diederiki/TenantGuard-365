import { FrameworkPage } from "../../../components/layout/FrameworkPage";
import { Badge } from "../../../components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";

export const dynamic = "force-dynamic";

const ROWS: { label: string; value: string; status?: "info" | "muted" | "attention" }[] = [
  { label: "Tenant ID", value: "00000000-aaaa-bbbb-cccc-000000000000", status: "info" },
  { label: "Display name", value: "AmSpec Group", status: "info" },
  { label: "Primary domain", value: "amspec.group", status: "info" },
  { label: "Connection status", value: "configured", status: "info" },
  { label: "Graph permission status", value: "consented (16/16)", status: "info" },
  { label: "Last successful sync", value: "2026-05-13T18:55:00Z", status: "info" },
  { label: "Last failed sync", value: "—", status: "muted" },
  { label: "Sync frequency", value: "per-collector cron schedules", status: "info" },
  { label: "Throttling / concurrency", value: "4 concurrent Graph calls per tenant", status: "info" },
  { label: "Enabled modules", value: "Entra · SharePoint · Service Health · Reports · Audit", status: "info" },
  { label: "Disabled modules", value: "Content search · Remediation (off by default)", status: "attention" },
];

export default async function TenantSettingsPage() {
  return (
    <FrameworkPage
      module="Settings"
      title="Tenant settings"
      subtitle="Per-tenant configuration: identity, sync cadence, module toggles."
      currentPath="/settings/tenant"
      status="framework"
      notes="Read-only summary. Per-tenant edits land alongside the multi-tenant onboarding flow in Phase 29."
    >
      <Card>
        <CardHeader>
          <CardTitle>Current state</CardTitle>
          <CardDescription>
            Sourced from <code className="font-mono">tenants</code> +{" "}
            <code className="font-mono">tenant_graph_settings</code>.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {ROWS.map((r) => (
              <div
                key={r.label}
                className="rounded-md border border-slate-800/80 bg-slate-900/40 px-3 py-2"
              >
                <dt className="flex items-center justify-between text-xs uppercase tracking-wider text-slate-500">
                  {r.label}
                  {r.status ? <Badge variant={r.status}>{r.status}</Badge> : null}
                </dt>
                <dd className="mt-1 text-sm text-slate-100">{r.value}</dd>
              </div>
            ))}
          </dl>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
