import { FrameworkPage } from "../../components/layout/FrameworkPage";
import { Badge } from "../../components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";

export const dynamic = "force-dynamic";

const RECENT: { ts: string; sev: string; channel: string; subject: string; status: "info" | "muted" | "critical" }[] = [
  { ts: "2026-05-13T19:21:00Z", sev: "critical", channel: "email", subject: "Anonymous link on /sites/marketing", status: "critical" },
  { ts: "2026-05-13T18:55:00Z", sev: "high", channel: "email", subject: "Guest sign-in from unusual location", status: "critical" },
  { ts: "2026-05-13T12:11:00Z", sev: "medium", channel: "—", subject: "Disabled user still present", status: "muted" },
  { ts: "2026-05-12T10:02:00Z", sev: "info", channel: "—", subject: "Daily SharePoint report ready", status: "info" },
];

export default async function NotificationsPage() {
  return (
    <FrameworkPage
      module="Admin"
      title="Notifications"
      subtitle="Recent platform-side notifications: who got pinged, when, why."
      currentPath="/notifications"
      status="framework"
      notes={
        <span>
          The send pipeline + history table land in Phase 28. Today this page
          renders demo events so you can see the intended shape; configure
          routing under{" "}
          <a className="text-brand-400 hover:underline" href="/settings/notifications">
            Settings → Notifications
          </a>
          .
        </span>
      }
    >
      <Card>
        <CardHeader>
          <CardTitle>Recent (demo)</CardTitle>
          <CardDescription>Last 4 fictional events to illustrate the schema.</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="divide-y divide-slate-800/80">
            {RECENT.map((r) => (
              <li key={r.ts} className="flex items-center justify-between py-2 text-sm">
                <div>
                  <div className="text-slate-200">{r.subject}</div>
                  <div className="font-mono text-xs text-slate-500">
                    {r.ts} · sev={r.sev} · channel={r.channel}
                  </div>
                </div>
                <Badge variant={r.status}>{r.sev}</Badge>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
