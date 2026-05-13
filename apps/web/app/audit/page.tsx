import { headers } from "next/headers";
import { redirect } from "next/navigation";

import { Badge } from "../../components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import { fetchAudit, fetchMe } from "../../lib/api";

export const dynamic = "force-dynamic";

function severityVariant(result: string): "info" | "critical" {
  return result === "success" ? "info" : "critical";
}

export default async function AuditPage({
  searchParams,
}: {
  searchParams: Promise<{ before_id?: string }>;
}) {
  const cookieHeader = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookieHeader);
  if (!me) redirect("/sign-in");

  const params = await searchParams;
  const beforeId = params.before_id ? Number(params.before_id) : undefined;
  const page = await fetchAudit(cookieHeader, { beforeId });

  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <header className="mb-8 flex items-end justify-between">
        <div>
          <p className="mb-1 text-xs font-medium uppercase tracking-widest text-brand-400">
            Audit
          </p>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Technician audit log
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Append-only. Every privileged action shows up here, server-side.
          </p>
        </div>
        <a href="/" className="text-sm text-brand-400 hover:underline">
          ← Back to overview
        </a>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Latest entries</CardTitle>
          <CardDescription>
            Newest first. Cursor-paginated by record id.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {"error" in page ? (
            <p className="text-sm text-rose-300">Failed to load: {page.error}</p>
          ) : page.items.length === 0 ? (
            <p className="text-sm text-slate-500">No audit entries yet.</p>
          ) : (
            <>
              <div className="overflow-x-auto rounded-lg border border-slate-800/80">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-slate-900/60 text-xs uppercase tracking-wider text-slate-500">
                    <tr>
                      <th className="px-3 py-2">When (UTC)</th>
                      <th className="px-3 py-2">Actor</th>
                      <th className="px-3 py-2">Action</th>
                      <th className="px-3 py-2">Target</th>
                      <th className="px-3 py-2">Result</th>
                    </tr>
                  </thead>
                  <tbody>
                    {page.items.map((e) => (
                      <tr
                        key={e.id}
                        className="border-t border-slate-800/80 text-slate-300"
                      >
                        <td className="px-3 py-2 font-mono text-xs">
                          {new Date(e.event_time).toISOString().replace("T", " ").slice(0, 19)}
                        </td>
                        <td className="px-3 py-2">
                          {e.actor_display}
                          <span className="ml-2 text-xs text-slate-500">
                            ({e.actor_type})
                          </span>
                        </td>
                        <td className="px-3 py-2 font-mono text-xs">{e.action}</td>
                        <td className="px-3 py-2 text-xs text-slate-400">
                          {e.target_label ?? e.target_id ?? "—"}
                          {e.target_type ? (
                            <span className="ml-1 text-slate-500">
                              [{e.target_type}]
                            </span>
                          ) : null}
                        </td>
                        <td className="px-3 py-2">
                          <Badge variant={severityVariant(e.result)}>
                            {e.result}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {page.next_cursor ? (
                <div className="mt-4 text-right">
                  <a
                    className="text-sm text-brand-400 hover:underline"
                    href={`/audit?before_id=${page.next_cursor}`}
                  >
                    Older →
                  </a>
                </div>
              ) : null}
            </>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
