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

export const dynamic = "force-dynamic";

type Collector = {
  key: string;
  module: string;
  display_name: string;
  required_scopes: string[];
  schedule_cron: string | null;
  description: string;
};

export default async function JobsPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  const base = apiBaseUrl({ serverSide: true });
  let collectors: Collector[] | { error: string };
  try {
    const r = await fetch(`${base}/api/collectors`, {
      headers: { cookie },
      cache: "no-store",
    });
    collectors = r.ok ? ((await r.json()) as Collector[]) : { error: `${r.status}` };
  } catch (e) {
    collectors = { error: String(e) };
  }

  return (
    <AppShell me={me} currentPath="/jobs">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Sync jobs
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Registered collectors. Each runs on its schedule and can be triggered
            manually once the tenant Graph connection is configured.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Registered collectors</CardTitle>
            <CardDescription>
              Listed scopes are required for the collector to succeed.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {"error" in collectors ? (
              <p className="text-sm text-rose-300">Failed to load: {collectors.error}</p>
            ) : (
              <div className="overflow-x-auto rounded-lg border border-slate-800/80">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-slate-900/60 text-xs uppercase tracking-wider text-slate-500">
                    <tr>
                      <th className="px-3 py-2">Module</th>
                      <th className="px-3 py-2">Collector</th>
                      <th className="px-3 py-2">Schedule</th>
                      <th className="px-3 py-2">Required scopes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {collectors.map((c) => (
                      <tr key={c.key} className="border-t border-slate-800/80 text-slate-300">
                        <td className="px-3 py-2">
                          <Badge variant="info">{c.module}</Badge>
                        </td>
                        <td className="px-3 py-2 font-medium text-slate-100">
                          {c.display_name}
                          <div className="font-mono text-xs text-slate-500">{c.key}</div>
                          <div className="text-xs text-slate-500">{c.description}</div>
                        </td>
                        <td className="px-3 py-2 font-mono text-xs text-slate-400">
                          {c.schedule_cron ?? "—"}
                        </td>
                        <td className="px-3 py-2">
                          <div className="flex flex-wrap gap-1">
                            {c.required_scopes.map((s) => (
                              <span
                                key={s}
                                className="rounded border border-slate-800 px-1.5 py-0.5 font-mono text-xs text-slate-400"
                              >
                                {s}
                              </span>
                            ))}
                          </div>
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
