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

const ROUTING: { sev: string; channel: string; status: "info" | "muted" }[] = [
  { sev: "critical", channel: "email + Teams webhook (placeholder)", status: "muted" },
  { sev: "high", channel: "email", status: "muted" },
  { sev: "medium", channel: "(none)", status: "muted" },
  { sev: "low", channel: "(none)", status: "muted" },
];

export default async function NotificationsSettingsPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  return (
    <AppShell me={me} currentPath="/settings/notifications">
      <main className="px-6 py-8">
        <header className="mb-6 flex items-end justify-between">
          <div>
            <p className="mb-1 text-xs font-medium uppercase tracking-widest text-brand-400">
              Settings
            </p>
            <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
              Notifications
            </h1>
            <p className="mt-1 max-w-2xl text-sm text-slate-400">
              How TenantGuard 365 surfaces security and operational events.
              SMTP and webhook plumbing exist as DB tables — UI configuration
              + send pipeline lands in Phase 27.
            </p>
          </div>
          <Badge variant="muted">framework</Badge>
        </header>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>SMTP</CardTitle>
              <CardDescription>
                Set via env (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`,
                `SMTP_PASSWORD`). Dev defaults point at the Mailhog container.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1 text-sm text-slate-300">
                <li>Host: <span className="font-mono text-xs text-slate-400">mailhog:1025</span></li>
                <li>From: <span className="font-mono text-xs text-slate-400">M365 Control Center &lt;noreply@tg365.local&gt;</span></li>
                <li>TLS: <span className="font-mono text-xs text-slate-400">off (dev)</span></li>
              </ul>
              <div className="mt-3">
                <button
                  type="button"
                  disabled
                  className="rounded-md border border-slate-800 bg-slate-900 px-3 py-1.5 text-xs text-slate-500"
                >
                  Send test email (Phase 27)
                </button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Severity routing</CardTitle>
              <CardDescription>
                Which channels should receive alerts at each severity.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="divide-y divide-slate-800/80">
                {ROUTING.map((r) => (
                  <li
                    key={r.sev}
                    className="flex items-center justify-between py-2 text-sm text-slate-200"
                  >
                    <span className="font-mono text-xs uppercase tracking-wider text-slate-400">
                      {r.sev}
                    </span>
                    <span className="flex items-center gap-2">
                      <span className="text-xs text-slate-400">{r.channel}</span>
                      <Badge variant={r.status}>{r.status}</Badge>
                    </span>
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
