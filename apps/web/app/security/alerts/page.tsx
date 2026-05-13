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
import { apiBaseUrl, fetchMe } from "../../../lib/api";

export const dynamic = "force-dynamic";

type Alert = {
  id: string;
  rule_key: string;
  severity: "info" | "attention" | "trouble" | "critical";
  status: "new" | "investigating" | "resolved" | "false_positive";
  title: string;
  entity_kind: string | null;
  entity_id: string | null;
  occurrences: number;
  first_seen_at: string;
  last_seen_at: string;
};

function sev(s: Alert["severity"]) {
  return s;
}

function statusVariant(s: Alert["status"]) {
  if (s === "new") return "trouble" as const;
  if (s === "investigating") return "attention" as const;
  if (s === "resolved") return "info" as const;
  return "muted" as const;
}

export default async function AlertsPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  const base = apiBaseUrl({ serverSide: true });
  let alerts: Alert[] | { error: string };
  try {
    const r = await fetch(`${base}/api/security/alerts?limit=100`, {
      headers: { cookie },
      cache: "no-store",
    });
    alerts = r.ok ? ((await r.json()) as Alert[]) : { error: `${r.status}` };
  } catch (e) {
    alerts = { error: String(e) };
  }

  return (
    <AppShell me={me} currentPath="/security/alerts">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Security alerts
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Deduplicated alerts produced by the rule engine. Newest activity first.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Open and recent alerts</CardTitle>
            <CardDescription>
              Severity → info / attention / trouble / critical.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {"error" in alerts ? (
              <p className="text-sm text-rose-300">Failed to load: {alerts.error}</p>
            ) : alerts.length === 0 ? (
              <p className="text-sm text-slate-500">
                No alerts. Run the rule engine via{" "}
                <code className="font-mono">POST /api/security/rules/evaluate-now</code>{" "}
                after collectors have populated data.
              </p>
            ) : (
              <div className="overflow-x-auto rounded-lg border border-slate-800/80">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-slate-900/60 text-xs uppercase tracking-wider text-slate-500">
                    <tr>
                      <th className="px-3 py-2">Severity</th>
                      <th className="px-3 py-2">Status</th>
                      <th className="px-3 py-2">Title</th>
                      <th className="px-3 py-2">Rule</th>
                      <th className="px-3 py-2">Occurs</th>
                      <th className="px-3 py-2">Last seen</th>
                    </tr>
                  </thead>
                  <tbody>
                    {alerts.map((a) => (
                      <tr key={a.id} className="border-t border-slate-800/80 text-slate-300">
                        <td className="px-3 py-2">
                          <Badge variant={sev(a.severity)}>{a.severity}</Badge>
                        </td>
                        <td className="px-3 py-2">
                          <Badge variant={statusVariant(a.status)}>{a.status}</Badge>
                        </td>
                        <td className="px-3 py-2 text-slate-100">{a.title}</td>
                        <td className="px-3 py-2 font-mono text-xs text-slate-500">
                          {a.rule_key}
                        </td>
                        <td className="px-3 py-2 text-xs">{a.occurrences}</td>
                        <td className="px-3 py-2 font-mono text-xs">
                          {new Date(a.last_seen_at)
                            .toISOString()
                            .replace("T", " ")
                            .slice(0, 19)}
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
