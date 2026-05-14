import Link from "next/link";

import { Badge } from "../ui/badge";

type Item = {
  href: string;
  label: string;
  module?: string;
  state?: "active" | "preview" | "soon" | "off";
  /** If set, hide unless caller has the permission key. */
  permission?: string;
};

const groups: { title: string; items: Item[] }[] = [
  {
    title: "Overview",
    items: [
      { href: "/", label: "Dashboard", state: "active" },
      { href: "/audit", label: "Audit log", state: "active", permission: "audit.read" },
    ],
  },
  {
    title: "Reports",
    items: [
      { href: "/reports", label: "All reports", state: "preview", permission: "reports.read" },
      { href: "/reports/builder", label: "  ↳ Builder", state: "soon", permission: "reports.create" },
      { href: "/reports/scheduled", label: "  ↳ Scheduled", state: "soon", permission: "reports.schedule" },
      { href: "/exports", label: "Exports", state: "preview", permission: "reports.export" },
    ],
  },
  {
    title: "Microsoft 365",
    items: [
      { href: "/entra", label: "Entra ID", state: "preview" },
      { href: "/entra/users", label: "  ↳ Users", state: "preview", permission: "entra.users.read" },
      { href: "/entra/groups", label: "  ↳ Groups", state: "preview", permission: "entra.groups.read" },
      { href: "/entra/roles", label: "  ↳ Roles", state: "preview" },
      { href: "/entra/licenses", label: "  ↳ Licenses", state: "preview" },
      { href: "/entra/signins", label: "  ↳ Sign-ins", state: "preview", permission: "entra.signins.read" },
      { href: "/entra/audit", label: "  ↳ Directory audit", state: "preview", permission: "entra.audits.read" },
      { href: "/sharepoint", label: "SharePoint", state: "preview" },
      { href: "/sharepoint/sites", label: "  ↳ Sites", state: "preview", permission: "sharepoint.sites.read" },
      { href: "/sharepoint/permissions", label: "  ↳ Permissions", state: "preview", permission: "sharepoint.permissions.read" },
      { href: "/sharepoint/sharing-links", label: "  ↳ Sharing links", state: "preview", permission: "sharepoint.permissions.read" },
      { href: "/sharepoint/external-users", label: "  ↳ External users", state: "preview", permission: "sharepoint.permissions.read" },
      { href: "/sharepoint/broken-inheritance", label: "  ↳ Broken inheritance", state: "preview", permission: "sharepoint.permissions.read" },
      { href: "/onedrive", label: "OneDrive", state: "preview" },
      { href: "/onedrive/accounts", label: "  ↳ Accounts", state: "preview" },
      { href: "/onedrive/sharing", label: "  ↳ Sharing", state: "preview" },
      { href: "/exchange", label: "Exchange", state: "preview" },
      { href: "/exchange/mailboxes", label: "  ↳ Mailboxes", state: "preview" },
      { href: "/exchange/permissions", label: "  ↳ Permissions", state: "preview" },
      { href: "/exchange/forwarding-risk", label: "  ↳ Forwarding risk", state: "preview" },
      { href: "/teams", label: "Teams", state: "preview" },
      { href: "/teams/inventory", label: "  ↳ Inventory", state: "preview" },
      { href: "/teams/members", label: "  ↳ Members", state: "preview" },
      { href: "/service-health", label: "Service health", state: "preview" },
    ],
  },
  {
    title: "Security",
    items: [
      { href: "/security/alerts", label: "Alerts", state: "preview", permission: "security.alerts.read" },
      { href: "/security/rules", label: "Rules", state: "preview", permission: "security.rules.read" },
      { href: "/security/investigations", label: "Investigations", state: "soon", permission: "security.alerts.read" },
      { href: "/content-search", label: "Content search", state: "off" },
      { href: "/remediation", label: "Remediation", state: "off" },
    ],
  },
  {
    title: "Admin",
    items: [
      { href: "/jobs", label: "Sync jobs", state: "preview" },
      { href: "/notifications", label: "Notifications", state: "preview" },
      { href: "/system-health", label: "System health", state: "active", permission: "platform.admin" },
      { href: "/settings", label: "Settings", state: "preview" },
      { href: "/settings/graph", label: "  ↳ Graph connection", state: "preview", permission: "platform.admin" },
      { href: "/settings/tenant", label: "  ↳ Tenant", state: "preview", permission: "platform.admin" },
      { href: "/settings/security", label: "  ↳ Security", state: "preview", permission: "platform.admin" },
      { href: "/settings/retention", label: "  ↳ Retention", state: "preview", permission: "platform.admin" },
      { href: "/settings/notifications", label: "  ↳ Notifications", state: "preview", permission: "platform.admin" },
      { href: "/settings/general", label: "  ↳ General", state: "preview", permission: "platform.admin" },
      { href: "/settings/reports", label: "  ↳ Reports", state: "preview", permission: "platform.admin" },
      { href: "/settings/users", label: "  ↳ Users", state: "preview", permission: "platform.users.read" },
      { href: "/delegation", label: "Delegation / RBAC", state: "soon", permission: "platform.roles.read" },
    ],
  },
  {
    title: "Help",
    items: [
      { href: "/help", label: "Documentation", state: "active" },
      { href: "/capability-matrix", label: "Capability matrix", state: "active" },
      { href: "/catalog", label: "Feature catalog", state: "active" },
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

export function Sidebar({
  currentPath,
  permissions = [],
}: {
  currentPath: string;
  /** Caller permissions; items with a permission requirement are filtered. */
  permissions?: string[];
}) {
  const allowed = new Set(permissions);
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
        {groups.map((g) => {
          const items = g.items.filter(
            (it) => !it.permission || allowed.has(it.permission),
          );
          if (items.length === 0) return null;
          return (
            <div key={g.title}>
              <div className="px-2 pb-1 text-[10px] font-semibold uppercase tracking-widest text-slate-500">
                {g.title}
              </div>
              <ul>
                {items.map((it) => {
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
          );
        })}
      </nav>
    </aside>
  );
}
