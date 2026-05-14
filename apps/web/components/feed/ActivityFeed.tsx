import {
  Activity,
  AlertTriangle,
  Bell,
  CheckCircle2,
  KeyRound,
  Lock,
  Shield,
  Workflow,
  type LucideIcon,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { fetchAudit } from "../../lib/api";

type Category = "auth" | "settings" | "collector" | "security" | "remediation" | "report" | "other";

const CATEGORY: Record<
  Category,
  { label: string; icon: LucideIcon; ring: string; chip: string; iconBg: string }
> = {
  auth: {
    label: "Auth",
    icon: KeyRound,
    ring: "ring-sky-500/20",
    chip: "bg-sky-500/15 text-sky-200 ring-sky-500/30",
    iconBg: "bg-sky-500/10 text-sky-300 ring-sky-500/30",
  },
  settings: {
    label: "Settings",
    icon: Lock,
    ring: "ring-violet-500/20",
    chip: "bg-violet-500/15 text-violet-200 ring-violet-500/30",
    iconBg: "bg-violet-500/10 text-violet-300 ring-violet-500/30",
  },
  collector: {
    label: "Sync",
    icon: Workflow,
    ring: "ring-emerald-500/20",
    chip: "bg-emerald-500/15 text-emerald-200 ring-emerald-500/30",
    iconBg: "bg-emerald-500/10 text-emerald-300 ring-emerald-500/30",
  },
  security: {
    label: "Security",
    icon: Shield,
    ring: "ring-rose-500/20",
    chip: "bg-rose-500/15 text-rose-200 ring-rose-500/30",
    iconBg: "bg-rose-500/10 text-rose-300 ring-rose-500/30",
  },
  remediation: {
    label: "Remediation",
    icon: AlertTriangle,
    ring: "ring-amber-500/20",
    chip: "bg-amber-500/15 text-amber-200 ring-amber-500/30",
    iconBg: "bg-amber-500/10 text-amber-300 ring-amber-500/30",
  },
  report: {
    label: "Report",
    icon: Activity,
    ring: "ring-cyan-500/20",
    chip: "bg-cyan-500/15 text-cyan-200 ring-cyan-500/30",
    iconBg: "bg-cyan-500/10 text-cyan-300 ring-cyan-500/30",
  },
  other: {
    label: "Other",
    icon: Bell,
    ring: "ring-slate-500/20",
    chip: "bg-slate-500/15 text-slate-200 ring-slate-500/30",
    iconBg: "bg-slate-500/10 text-slate-300 ring-slate-500/30",
  },
};

function categorize(action: string): Category {
  if (action.startsWith("auth.")) return "auth";
  if (action.startsWith("settings.")) return "settings";
  if (action.startsWith("collector.") || action.startsWith("scheduler.")) return "collector";
  if (action.startsWith("security.") || action.startsWith("audit.")) return "security";
  if (action.startsWith("remediation.")) return "remediation";
  if (action.startsWith("report.") || action.startsWith("export.")) return "report";
  return "other";
}

function formatAt(iso: string) {
  const d = new Date(iso);
  const now = new Date();
  const diff = (now.getTime() - d.getTime()) / 1000;
  if (diff < 60) return `${Math.max(1, Math.floor(diff))}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return d.toISOString().slice(0, 16).replace("T", " ");
}

export async function ActivityFeed({ cookie }: { cookie: string }) {
  const page = await fetchAudit(cookie, { limit: 20 });
  const items = "error" in page ? [] : page.items;
  const errored = "error" in page;

  return (
    <Card variant="glass" className="overflow-hidden">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Activity inbox</CardTitle>
            <CardDescription>
              Real-time stream of privileged platform actions. Grouped by category.
            </CardDescription>
          </div>
          <a
            href="/audit"
            className="rounded-lg border border-slate-800/60 bg-slate-900/60 px-2.5 py-1 text-xs text-slate-300 ring-1 ring-white/5 hover:text-slate-100"
          >
            View all
          </a>
        </div>
      </CardHeader>
      <CardContent className="-mx-2">
        {errored ? (
          <p className="px-2 py-4 text-sm text-rose-300">
            Failed to load activity feed. Sign in to load real events.
          </p>
        ) : items.length === 0 ? (
          <p className="px-2 py-4 text-sm text-slate-500">No activity yet.</p>
        ) : (
          <ul className="divide-y divide-slate-800/70">
            {items.map((e) => {
              const cat = categorize(e.action);
              const C = CATEGORY[cat];
              const Icon = C.icon;
              const success = e.result === "success";
              return (
                <li
                  key={e.id}
                  className="group flex items-start gap-3 px-2 py-3 hover:bg-slate-900/40"
                >
                  <div
                    className={`mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-xl ring-1 ${C.iconBg}`}
                  >
                    <Icon className="h-3.5 w-3.5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-slate-300">{e.action}</span>
                      <span
                        className={`rounded-full px-1.5 py-0.5 text-[10px] ring-1 ${C.chip}`}
                      >
                        {C.label}
                      </span>
                      {success ? (
                        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-1.5 py-0.5 text-[10px] text-emerald-300 ring-1 ring-emerald-500/30">
                          <CheckCircle2 className="h-3 w-3" /> ok
                        </span>
                      ) : (
                        <span className="rounded-full bg-rose-500/15 px-1.5 py-0.5 text-[10px] text-rose-300 ring-1 ring-rose-500/30">
                          {e.result}
                        </span>
                      )}
                    </div>
                    <div className="mt-0.5 truncate text-sm text-slate-200">
                      <span className="text-slate-400">by</span>{" "}
                      <span className="text-slate-100">{e.actor_display}</span>
                      {e.target_label ? (
                        <>
                          {" "}
                          <span className="text-slate-400">on</span>{" "}
                          <span className="text-slate-100">{e.target_label}</span>
                        </>
                      ) : e.target_id ? (
                        <>
                          {" "}
                          <span className="text-slate-400">on</span>{" "}
                          <span className="font-mono text-slate-400">{e.target_id}</span>
                        </>
                      ) : null}
                    </div>
                  </div>
                  <span className="shrink-0 self-center text-xs text-slate-500">
                    {formatAt(e.event_time)}
                  </span>
                </li>
              );
            })}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
