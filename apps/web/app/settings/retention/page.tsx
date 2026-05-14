import { headers } from "next/headers";
import { redirect } from "next/navigation";

import { AppShell } from "../../../components/layout/AppShell";
import { Badge } from "../../../components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";
import { fetchMe } from "../../../lib/api";

export const dynamic = "force-dynamic";

const POLICIES: { label: string; current: string; default: string }[] = [
  { label: "Audit events", current: "365 days", default: "365 days" },
  { label: "Report exports", current: "90 days", default: "90 days" },
  { label: "Job-run logs", current: "30 days", default: "30 days" },
  { label: "Security alerts", current: "180 days", default: "180 days" },
  { label: "Content-search results", current: "30 days", default: "30 days" },
  { label: "OpenSearch indices", current: "(per ISM policy)", default: "rolling 30-day" },
];

export default async function RetentionSettingsPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  return (
    <AppShell me={me} currentPath="/settings/retention">
      <main className="px-6 py-8">
        <header className="mb-6 flex items-end justify-between">
          <div>
            <p className="mb-1 text-xs font-medium uppercase tracking-widest text-brand-400">
              Settings
            </p>
            <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
              Data retention
            </h1>
            <p className="mt-1 max-w-2xl text-sm text-slate-400">
              How long each data class is kept before scheduled cleanup jobs
              age it out. Real cleanup tasks land alongside the retention
              policy table in Phase 27.
            </p>
          </div>
          <Badge variant="muted">framework</Badge>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Retention policy</CardTitle>
            <CardDescription>
              Defaults are aligned with typical 1-year audit retention.
              Tenants on regulated workloads should review with legal.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <table className="min-w-full text-left text-sm">
              <thead className="text-xs uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="py-2">Data class</th>
                  <th className="py-2">Current</th>
                  <th className="py-2">Default</th>
                </tr>
              </thead>
              <tbody>
                {POLICIES.map((p) => (
                  <tr key={p.label} className="border-t border-slate-800/80">
                    <td className="py-2 text-slate-200">{p.label}</td>
                    <td className="py-2 font-mono text-xs text-slate-300">
                      {p.current}
                    </td>
                    <td className="py-2 font-mono text-xs text-slate-500">
                      {p.default}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </main>
    </AppShell>
  );
}
