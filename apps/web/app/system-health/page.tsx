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
import { isDemoCookie } from "../../lib/demoData";

export const dynamic = "force-dynamic";

type Check = { ok: boolean; error: string | null };
type SystemHealth = {
  status: "ok" | "degraded";
  checks: Record<"database" | "redis" | "opensearch" | "minio", Check>;
  jobs: {
    recent_total: number;
    by_status: Record<string, number>;
    failed_lifetime: number;
  };
};

const DEMO_SYSTEM_HEALTH: SystemHealth = {
  status: "ok",
  checks: {
    database: { ok: true, error: null },
    redis: { ok: true, error: null },
    opensearch: { ok: true, error: null },
    minio: { ok: true, error: null },
  },
  jobs: {
    recent_total: 41,
    by_status: { succeeded: 38, failed: 2, running: 1 },
    failed_lifetime: 6,
  },
};

async function fetchHealth(
  cookie: string,
): Promise<SystemHealth | { error: string }> {
  if (isDemoCookie(cookie)) return DEMO_SYSTEM_HEALTH;
  const base = apiBaseUrl({ serverSide: true });
  try {
    const r = await fetch(`${base}/api/system/health`, {
      headers: { cookie },
      cache: "no-store",
    });
    if (!r.ok) return { error: `${r.status}` };
    return (await r.json()) as SystemHealth;
  } catch (e) {
    return { error: String(e) };
  }
}

function StatusBadge({ ok, label }: { ok: boolean; label: string }) {
  return (
    <div className="flex items-center justify-between rounded-md border border-slate-800/80 bg-slate-900/40 px-3 py-2">
      <span className="text-sm text-slate-200">{label}</span>
      {ok ? <Badge variant="info">OK</Badge> : <Badge variant="critical">DOWN</Badge>}
    </div>
  );
}

export default async function SystemHealthPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");
  const data = await fetchHealth(cookie);

  return (
    <AppShell me={me} currentPath="/system-health">
      <main className="px-6 py-8">
        <header className="mb-6">
          <p className="mb-1 text-xs font-medium uppercase tracking-widest text-brand-400">
            Admin
          </p>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            System health
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Live status of the platform&apos;s own infrastructure. Independent
            from Microsoft Graph health (see Service health).
          </p>
        </header>

        {"error" in data ? (
          <Card>
            <CardContent>
              <p className="text-sm text-rose-300">
                Failed to load system health: {data.error}
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Dependencies</CardTitle>
                <CardDescription>
                  Overall status:{" "}
                  {data.status === "ok" ? (
                    <Badge variant="info">healthy</Badge>
                  ) : (
                    <Badge variant="critical">degraded</Badge>
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                  <StatusBadge ok={data.checks.database.ok} label="PostgreSQL" />
                  <StatusBadge ok={data.checks.redis.ok} label="Redis" />
                  <StatusBadge ok={data.checks.opensearch.ok} label="OpenSearch" />
                  <StatusBadge ok={data.checks.minio.ok} label="MinIO" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Job runs</CardTitle>
                <CardDescription>
                  Last 50 collector runs, grouped by status.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-1 text-sm text-slate-300">
                  <li className="flex justify-between border-b border-slate-800/80 pb-1">
                    <span>Total (recent 50)</span>
                    <span className="font-mono">{data.jobs.recent_total}</span>
                  </li>
                  {Object.entries(data.jobs.by_status).map(([k, v]) => (
                    <li key={k} className="flex justify-between">
                      <span className="capitalize text-slate-400">{k}</span>
                      <span className="font-mono">{v}</span>
                    </li>
                  ))}
                  <li className="flex justify-between border-t border-slate-800/80 pt-1 text-slate-400">
                    <span>Failed (lifetime)</span>
                    <span className="font-mono">{data.jobs.failed_lifetime}</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </AppShell>
  );
}
