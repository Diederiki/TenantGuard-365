import { headers } from "next/headers";
import { redirect } from "next/navigation";

import { AppShell } from "../../../components/layout/AppShell";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";
import { apiBaseUrl, fetchMe } from "../../../lib/api";
import { DEMO_GRAPH_SETTINGS, DEMO_TENANT_ID, isDemoCookie } from "../../../lib/demoData";
import { GraphForm } from "./GraphForm";

export const dynamic = "force-dynamic";

const MIN_SCOPES = [
  "User.Read.All",
  "Group.Read.All",
  "GroupMember.Read.All",
  "RoleManagement.Read.Directory",
  "Organization.Read.All",
  "Sites.Read.All",
  "Files.Read.All",
  "MailboxSettings.Read",
  "Reports.Read.All",
  "ServiceHealth.Read.All",
  "ServiceMessage.Read.All",
  "Team.ReadBasic.All",
  "Channel.ReadBasic.All",
  "TeamMember.Read.All",
  "Application.Read.All",
  "AuditLog.Read.All",
];

export default async function GraphConnectionPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");
  const demo = isDemoCookie(cookie);

  let tenantId = DEMO_TENANT_ID;
  let initial = DEMO_GRAPH_SETTINGS;
  if (!demo) {
    try {
      const base = apiBaseUrl({ serverSide: true });
      const r = await fetch(`${base}/api/tenants`, {
        headers: { cookie },
        cache: "no-store",
      });
      if (r.ok) {
        const list = (await r.json()) as Array<{ id: string }>;
        if (list.length > 0) {
          tenantId = list[0].id;
          const sr = await fetch(`${base}/api/settings/graph/${tenantId}`, {
            headers: { cookie },
            cache: "no-store",
          });
          if (sr.ok) {
            initial = (await sr.json()) as typeof DEMO_GRAPH_SETTINGS;
          }
        }
      }
    } catch {
      // Fall back to demo fixture so the form still renders.
    }
  }

  return (
    <AppShell me={me} currentPath="/settings/graph">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Graph connection
          </h1>
          <p className="mt-1 max-w-3xl text-sm text-slate-400">
            Two app registrations: <code className="font-mono">tg365-portal</code>{" "}
            (sign-in) and <code className="font-mono">tg365-collector</code>{" "}
            (read-only data collection).
          </p>
        </header>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Step 1 — Create collector app</CardTitle>
              <CardDescription>
                Single-tenant app registration. Application permissions only.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ol className="space-y-1 text-sm text-slate-300">
                <li>1. Entra portal → App registrations → New registration.</li>
                <li>
                  2. Name: <code className="font-mono">tg365-collector</code> —
                  Single tenant — no redirect URI.
                </li>
                <li>
                  3. Add Application permissions on Microsoft Graph (full list →).
                </li>
                <li>4. Grant admin consent.</li>
                <li>
                  5. Add a certificate (preferred) or 6-month client secret.
                </li>
              </ol>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Step 2 — Required scopes (read-only)</CardTitle>
              <CardDescription>
                Phase 4 minimum viable set. Optional features add to this list.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-1.5">
                {MIN_SCOPES.map((s) => (
                  <span
                    key={s}
                    className="rounded border border-slate-800 bg-slate-900/60 px-2 py-0.5 font-mono text-xs text-slate-300"
                  >
                    {s}
                  </span>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Step 3 — Set env vars</CardTitle>
              <CardDescription>
                In production, mount these from your secret store. Never commit.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <pre className="overflow-x-auto rounded-md bg-slate-950 p-3 font-mono text-xs text-slate-300">
                {`ENTRA_TENANT_ID=<tenant-id>
ENTRA_CLIENT_ID=<collector-app-client-id>
ENTRA_CLIENT_SECRET=<collector-secret>   # or cert path
TOKEN_CACHE_MASTER_KEY=<32+ byte random>`}
              </pre>
            </CardContent>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Step 4 — Save tenant Graph settings</CardTitle>
              <CardDescription>
                Persists app-registration IDs + secrets per tenant. Secrets are
                AES-GCM-sealed before write. Use Test connection to verify.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <GraphForm tenantId={tenantId} initial={initial} demo={demo} />
            </CardContent>
          </Card>
        </div>
      </main>
    </AppShell>
  );
}
