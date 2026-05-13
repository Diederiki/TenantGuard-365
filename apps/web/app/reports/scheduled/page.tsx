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
import { DEMO_SCHEDULED_REPORTS, isDemoRequest } from "../../../lib/demoData";

export const dynamic = "force-dynamic";

export default async function ScheduledReportsPage({
  searchParams,
}: {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}) {
  const cookie = (await headers()).get("cookie") ?? "";
  const params = searchParams ? await searchParams : {};
  const demo = isDemoRequest(cookie, params);
  const me = demo
    ? { display_name: "Local Admin (Demo)", email: "admin@dev.local", role_keys: ["platform_admin"] }
    : await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  const rows = demo ? DEMO_SCHEDULED_REPORTS : ([] as typeof DEMO_SCHEDULED_REPORTS);

  return (
    <AppShell me={me} currentPath="/reports/scheduled">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Scheduled reports
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Cron-driven runs. Supports <code className="font-mono">@hourly</code>,{" "}
            <code className="font-mono">@daily</code>, <code className="font-mono">@weekly</code>,{" "}
            <code className="font-mono">@monthly</code>, integer minutes, or any 5-field cron via
            croniter.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Schedules</CardTitle>
            <CardDescription>{rows.length} active</CardDescription>
          </CardHeader>
          <CardContent>
            {rows.length === 0 ? (
              <p className="text-sm text-slate-500">
                No schedules yet. Save a report and schedule it from the report
                detail page.
              </p>
            ) : (
              <div className="overflow-x-auto rounded-lg border border-slate-800/80">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-slate-900/60 text-xs uppercase tracking-wider text-slate-500">
                    <tr>
                      <th className="px-3 py-2">Report</th>
                      <th className="px-3 py-2">Cron</th>
                      <th className="px-3 py-2">Formats</th>
                      <th className="px-3 py-2">Email</th>
                      <th className="px-3 py-2">Next run (UTC)</th>
                      <th className="px-3 py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((s) => (
                      <tr key={s.id} className="border-t border-slate-800/80 text-slate-300">
                        <td className="px-3 py-2 text-slate-100">{s.report}</td>
                        <td className="px-3 py-2 font-mono text-xs">{s.cron}</td>
                        <td className="px-3 py-2 text-xs">
                          {s.formats.join(", ")}
                        </td>
                        <td className="px-3 py-2 font-mono text-xs">
                          {s.email_to.join(", ")}
                        </td>
                        <td className="px-3 py-2 font-mono text-xs">
                          {new Date(s.next_run_at)
                            .toISOString()
                            .replace("T", " ")
                            .slice(0, 16)}
                        </td>
                        <td className="px-3 py-2">
                          <Badge variant={s.enabled ? "info" : "muted"}>
                            {s.enabled ? "active" : "paused"}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </AppShell>
  );
}
