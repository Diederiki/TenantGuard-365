import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Badge } from "../components/ui/badge";

async function fetchHealth(): Promise<{
  api: { ok: boolean; status: string; error?: string };
  ready: { ok: boolean; status: string };
}> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://api:8000";
  try {
    const [h, r] = await Promise.all([
      fetch(`${base}/healthz`, { cache: "no-store" }),
      fetch(`${base}/readyz`, { cache: "no-store" }),
    ]);
    return {
      api: { ok: h.ok, status: h.ok ? "ok" : `${h.status}` },
      ready: { ok: r.ok, status: r.ok ? "ok" : "degraded" },
    };
  } catch (e: unknown) {
    return {
      api: { ok: false, status: "unreachable", error: String(e) },
      ready: { ok: false, status: "unreachable" },
    };
  }
}

const phases = [
  { n: 0, name: "Project blueprint & feasibility", state: "done" },
  { n: 1, name: "Repo bootstrap", state: "active" },
  { n: 2, name: "Authentication & RBAC", state: "todo" },
  { n: 3, name: "Microsoft Graph connection center", state: "todo" },
  { n: 4, name: "Core data collectors", state: "todo" },
  { n: 5, name: "Dashboard & report engine", state: "todo" },
  { n: 6, name: "SharePoint deep audit", state: "todo" },
  { n: 7, name: "Unified audit & security ops", state: "todo" },
  { n: 8, name: "Content search & investigations", state: "todo" },
  { n: 9, name: "Remediation framework (off by default)", state: "todo" },
  { n: 10, name: "Enterprise hardening", state: "todo" },
];

export default async function HomePage() {
  const health = await fetchHealth();

  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <header className="mb-10 flex items-start justify-between gap-6">
        <div>
          <p className="mb-2 text-sm font-medium uppercase tracking-widest text-brand-400">
            TenantGuard / Internal
          </p>
          <h1 className="text-4xl font-semibold tracking-tight text-slate-50">
            M365 Enterprise Control Center
          </h1>
          <p className="mt-3 max-w-2xl text-slate-400">
            Reporting, auditing, monitoring, SharePoint visibility, and security operations for
            Microsoft 365. Defensive read-first platform. No destructive actions without
            two-person approval and dry-run.
          </p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <Badge variant={health.api.ok ? "info" : "critical"}>
            API · {health.api.status}
          </Badge>
          <Badge variant={health.ready.ok ? "info" : "attention"}>
            Dependencies · {health.ready.status}
          </Badge>
        </div>
      </header>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Stack health</CardTitle>
            <CardDescription>
              Reachability of the API, database, Redis, OpenSearch, and MinIO.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1">
              <li className="flex items-center justify-between">
                <span>API</span>
                <Badge variant={health.api.ok ? "info" : "critical"}>
                  {health.api.status}
                </Badge>
              </li>
              <li className="flex items-center justify-between">
                <span>Dependencies</span>
                <Badge variant={health.ready.ok ? "info" : "attention"}>
                  {health.ready.status}
                </Badge>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Phase progress</CardTitle>
            <CardDescription>
              Phased delivery plan. Phase 1 ships now; Phases 2–10 follow.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ol className="space-y-1.5">
              {phases.map((p) => (
                <li key={p.n} className="flex items-center justify-between gap-3">
                  <span className="text-slate-200">
                    <span className="mr-2 inline-block w-10 font-mono text-xs text-slate-500">
                      P{String(p.n).padStart(2, "0")}
                    </span>
                    {p.name}
                  </span>
                  <Badge
                    variant={
                      p.state === "done"
                        ? "info"
                        : p.state === "active"
                          ? "attention"
                          : "muted"
                    }
                  >
                    {p.state}
                  </Badge>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>
      </section>

      <section className="mt-10 grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Read first</CardTitle>
            <CardDescription>
              No Microsoft Graph writes are made from any user-facing path. Collectors are read-only.
            </CardDescription>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Audited everything</CardTitle>
            <CardDescription>
              Every privileged action is recorded in an append-only audit log.
            </CardDescription>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Least privilege</CardTitle>
            <CardDescription>
              Per-feature Graph permission documentation; never run as Global Admin.
            </CardDescription>
          </CardHeader>
        </Card>
      </section>

      <footer className="mt-12 text-xs text-slate-500">
        Phase {phases.find((p) => p.state === "active")?.n ?? 0} ·{" "}
        <span className="font-mono">tg365-web 0.1.0</span>
      </footer>
    </main>
  );
}
