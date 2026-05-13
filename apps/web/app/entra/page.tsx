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
import { fetchMe } from "../../lib/api";

export const dynamic = "force-dynamic";

const collectorKeys = ["entra.users", "entra.groups", "entra.licenses"];
const reportKeys = [
  "entra.users.all",
  "entra.users.guests",
  "entra.groups.inventory",
  "entra.licenses.usage",
];
const ruleKeys = [
  "entra.guest_user_active",
  "entra.disabled_user_present",
  "entra.guest_count_high",
];

export default async function EntraPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  return (
    <AppShell me={me} currentPath="/entra">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Entra ID
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Users, groups, licenses, role assignments. Read-only mirror of the
            tenant's Entra ID directory via Microsoft Graph.
          </p>
        </header>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Collectors</CardTitle>
              <CardDescription>
                Schedule + manual trigger from <a className="text-brand-400 hover:underline" href="/jobs">Jobs</a>.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1">
                {collectorKeys.map((k) => (
                  <li key={k} className="flex items-center justify-between">
                    <span className="font-mono text-xs text-slate-400">{k}</span>
                    <Badge variant="info">read-only</Badge>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Reports</CardTitle>
              <CardDescription>
                Run from <a className="text-brand-400 hover:underline" href="/reports">Reports</a>.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1">
                {reportKeys.map((k) => (
                  <li key={k} className="font-mono text-xs text-slate-400">
                    {k}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Security rules</CardTitle>
              <CardDescription>
                See <a className="text-brand-400 hover:underline" href="/security/rules">Security → Rules</a>.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1">
                {ruleKeys.map((k) => (
                  <li key={k} className="font-mono text-xs text-slate-400">
                    {k}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      </main>
    </AppShell>
  );
}
