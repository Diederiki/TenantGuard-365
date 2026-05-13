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

type Case = {
  id: string;
  tenant_id: string;
  title: string;
  status: "open" | "in_progress" | "closed";
  priority: "low" | "medium" | "high" | "critical";
  owner_id: string | null;
  summary: string | null;
  created_at: string;
  updated_at: string;
};

function priorityVariant(p: Case["priority"]) {
  if (p === "low") return "muted" as const;
  if (p === "medium") return "info" as const;
  if (p === "high") return "attention" as const;
  return "critical" as const;
}

function statusVariant(s: Case["status"]) {
  if (s === "open") return "trouble" as const;
  if (s === "in_progress") return "attention" as const;
  return "muted" as const;
}

export default async function InvestigationsPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  const base = apiBaseUrl({ serverSide: true });
  let cases: Case[] | { error: string };
  try {
    const r = await fetch(`${base}/api/investigations`, {
      headers: { cookie },
      cache: "no-store",
    });
    cases = r.ok ? ((await r.json()) as Case[]) : { error: `${r.status}` };
  } catch (e) {
    cases = { error: String(e) };
  }

  return (
    <AppShell me={me} currentPath="/security/investigations">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Investigations
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Cases group related alerts, evidence notes, and status changes.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Open cases</CardTitle>
            <CardDescription>
              Most-recent activity first.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {"error" in cases ? (
              <p className="text-sm text-rose-300">Failed to load: {cases.error}</p>
            ) : cases.length === 0 ? (
              <p className="text-sm text-slate-500">No cases yet.</p>
            ) : (
              <div className="overflow-x-auto rounded-lg border border-slate-800/80">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-slate-900/60 text-xs uppercase tracking-wider text-slate-500">
                    <tr>
                      <th className="px-3 py-2">Priority</th>
                      <th className="px-3 py-2">Status</th>
                      <th className="px-3 py-2">Title</th>
                      <th className="px-3 py-2">Updated</th>
                    </tr>
                  </thead>
                  <tbody>
                    {cases.map((c) => (
                      <tr key={c.id} className="border-t border-slate-800/80 text-slate-300">
                        <td className="px-3 py-2">
                          <Badge variant={priorityVariant(c.priority)}>{c.priority}</Badge>
                        </td>
                        <td className="px-3 py-2">
                          <Badge variant={statusVariant(c.status)}>{c.status}</Badge>
                        </td>
                        <td className="px-3 py-2 text-slate-100">{c.title}</td>
                        <td className="px-3 py-2 font-mono text-xs">
                          {new Date(c.updated_at).toISOString().replace("T", " ").slice(0, 19)}
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
