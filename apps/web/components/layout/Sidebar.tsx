import Link from "next/link";

import { Badge } from "../ui/badge";

type Item = {
  href: string;
  label: string;
  module?: string;
  state?: "active" | "preview" | "soon" | "off";
};

const groups: { title: string; items: Item[] }[] = [
  {
    title: "Overview",
    items: [
      { href: "/", label: "Dashboard", state: "active" },
      { href: "/audit", label: "Audit log", state: "active" },
    ],
  },
  {
    title: "Reports",
    items: [
      { href: "/reports", label: "All reports", state: "preview" },
      { href: "/reports/scheduled", label: "Scheduled", state: "soon" },
    ],
  },
  {
    title: "Microsoft 365",
    items: [
      { href: "/entra", label: "Entra ID", state: "preview" },
      { href: "/entra/users", label: "  ↳ Users", state: "preview" },
      { href: "/sharepoint", label: "SharePoint", state: "preview" },
      { href: "/sharepoint/permissions", label: "  ↳ Permissions", state: "preview" },
      { href: "/onedrive", label: "OneDrive", state: "soon" },
      { href: "/exchange", label: "Exchange", state: "soon" },
      { href: "/teams", label: "Teams", state: "soon" },
      { href: "/service-health", label: "Service health", state: "preview" },
    ],
  },
  {
    title: "Security",
    items: [
      { href: "/security/alerts", label: "Alerts", state: "preview" },
      { href: "/security/rules", label: "Rules", state: "preview" },
      { href: "/security/investigations", label: "Investigations", state: "soon" },
      { href: "/content-search", label: "Content search", state: "off" },
      { href: "/remediation", label: "Remediation", state: "off" },
    ],
  },
  {
    title: "Admin",
    items: [
      { href: "/jobs", label: "Sync jobs", state: "preview" },
      { href: "/system-health", label: "System health", state: "active" },
      { href: "/settings/graph", label: "Graph connection", state: "preview" },
      { href: "/delegation", label: "Delegation / RBAC", state: "soon" },
      { href: "/settings", label: "Settings", state: "preview" },
    ],
  },
];

function stateBadge(state: Item["state"]): React.ReactNode {
  if (state === "active") return null;
  if (state === "preview") return <Badge variant="info">preview</Badge>;
  if (state === "soon") return <Badge variant="muted">soon</Badge>;
  if (state === "off") return <Badge variant="attention">off by default</Badge>;
  return null;
}

export function Sidebar({ currentPath }: { currentPath: string }) {
  return (
    <aside className="hidden w-72 shrink-0 border-r border-slate-800/80 bg-slate-950/60 px-4 py-6 lg:block">
      <div className="mb-6 px-2">
        <div className="text-xs font-medium uppercase tracking-widest text-brand-400">
          TenantGuard
        </div>
        <div className="text-sm font-semibold text-slate-100">
          M365 Control Center
        </div>
      </div>
      <nav className="space-y-6">
        {groups.map((g) => (
          <div key={g.title}>
            <div className="px-2 pb-1 text-[10px] font-semibold uppercase tracking-widest text-slate-500">
              {g.title}
            </div>
            <ul>
              {g.items.map((it) => {
                const active = currentPath === it.href;
                return (
                  <li key={it.href}>
                    <Link
                      href={it.href}
                      className={
                        "flex items-center justify-between rounded-md px-2 py-1.5 text-sm " +
                        (active
                          ? "bg-slate-800 text-slate-100"
                          : "text-slate-300 hover:bg-slate-900 hover:text-slate-100")
                      }
                    >
                      <span>{it.label}</span>
                      {stateBadge(it.state)}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  );
}
