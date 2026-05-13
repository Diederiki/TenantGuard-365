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
import { DEMO_REPORT_DEFS, isDemoCookie } from "../../lib/demoData";

export const dynamic = "force-dynamic";

type ReportDef = {
  key: string;
  module: string;
  display_name: string;
  description: string;
  columns: { key: string; label: string; width: number }[];
};

async function fetchReports(cookie: string): Promise<ReportDef[] | { error: string }> {
  if (isDemoCookie(cookie)) return DEMO_REPORT_DEFS;
  const base = apiBaseUrl({ serverSide: true });
  try {
    const r = await fetch(`${base}/api/reports/definitions`, {
      headers: { cookie },
      cache: "no-store",
    });
    if (!r.ok) return { error: `${r.status}` };
    return (await r.json()) as ReportDef[];
  } catch (e) {
    return { error: String(e) };
  }
}

export default async function ReportsPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  const reports = await fetchReports(cookie);

  return (
    <AppShell me={me} currentPath="/reports">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Reports
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Built-in report definitions. Run, schedule, and export to CSV / XLSX /
            HTML / PDF.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Built-in reports</CardTitle>
            <CardDescription>
              Module-grouped. Each report has fixed columns and accepts filters.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {"error" in reports ? (
              <p className="text-sm text-rose-300">Failed to load: {reports.error}</p>
            ) : (
              <div className="overflow-x-auto rounded-lg border border-slate-800/80">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-slate-900/60 text-xs uppercase tracking-wider text-slate-500">
                    <tr>
                      <th className="px-3 py-2">Module</th>
                      <th className="px-3 py-2">Report</th>
                      <th className="px-3 py-2">Description</th>
                      <th className="px-3 py-2">Columns</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reports.map((r) => (
                      <tr key={r.key} className="border-t border-slate-800/80 text-slate-300">
                        <td className="px-3 py-2">
                          <Badge variant="info">{r.module}</Badge>
                        </td>
                        <td className="px-3 py-2 font-medium text-slate-100">
                          {r.display_name}
                          <div className="font-mono text-xs text-slate-500">{r.key}</div>
                        </td>
                        <td className="px-3 py-2 text-xs text-slate-400">
                          {r.description}
                        </td>
                        <td className="px-3 py-2 text-xs text-slate-500">
                          {r.columns.length} cols
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
