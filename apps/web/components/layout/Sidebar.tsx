"use client";

import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bell,
  BookOpen,
  Briefcase,
  Building2,
  Cloud,
  FileSpreadsheet,
  Gauge,
  Globe,
  Inbox,
  KeyRound,
  LayoutDashboard,
  Library,
  LifeBuoy,
  Link2,
  ListChecks,
  Lock,
  Mail,
  Map,
  Plug,
  Search,
  Settings,
  Share2,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Trash2,
  Users,
  Users2,
  Workflow,
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { cn } from "../../lib/utils";

type Icon = React.ComponentType<{ className?: string }>;

type Item = {
  href: string;
  label: string;
  icon?: Icon;
  state?: "active" | "preview" | "soon" | "off";
  permission?: string;
};

type Group = { title: string; items: Item[] };

const groups: Group[] = [
  {
    title: "Overview",
    items: [
      { href: "/", label: "Dashboard", icon: LayoutDashboard, state: "active" },
      { href: "/audit", label: "Audit log", icon: ListChecks, state: "active", permission: "audit.read" },
    ],
  },
  {
    title: "Reports",
    items: [
      { href: "/reporting", label: "Reporting overview", icon: BarChart3, state: "active", permission: "reports.read" },
      { href: "/reports", label: "All reports", icon: FileSpreadsheet, state: "preview", permission: "reports.read" },
      { href: "/reports/builder", label: "Report builder", icon: Sparkles, state: "soon", permission: "reports.create" },
      { href: "/reports/scheduled", label: "Scheduled", icon: Workflow, state: "soon", permission: "reports.schedule" },
      { href: "/exports", label: "Exports", icon: Inbox, state: "preview", permission: "reports.export" },
    ],
  },
  {
    title: "Microsoft 365",
    items: [
      { href: "/entra", label: "Entra ID", icon: Users, state: "preview" },
      { href: "/entra/users", label: "Users", icon: Users, state: "preview", permission: "entra.users.read" },
      { href: "/entra/groups", label: "Groups", icon: Users2, state: "preview", permission: "entra.groups.read" },
      { href: "/entra/roles", label: "Roles", icon: KeyRound, state: "preview" },
      { href: "/entra/licenses", label: "Licenses", icon: Briefcase, state: "preview" },
      { href: "/entra/signins", label: "Sign-ins", icon: Activity, state: "preview", permission: "entra.signins.read" },
      { href: "/entra/audit", label: "Directory audit", icon: ListChecks, state: "preview", permission: "entra.audits.read" },
      { href: "/sharepoint", label: "SharePoint", icon: Globe, state: "preview" },
      { href: "/sharepoint/sites", label: "Sites", icon: Building2, state: "preview", permission: "sharepoint.sites.read" },
      { href: "/sharepoint/permissions", label: "Permissions", icon: Lock, state: "preview", permission: "sharepoint.permissions.read" },
      { href: "/sharepoint/sharing-links", label: "Sharing links", icon: Link2, state: "preview", permission: "sharepoint.permissions.read" },
      { href: "/sharepoint/external-users", label: "External users", icon: Users2, state: "preview", permission: "sharepoint.permissions.read" },
      { href: "/sharepoint/broken-inheritance", label: "Broken inheritance", icon: AlertTriangle, state: "preview", permission: "sharepoint.permissions.read" },
      { href: "/onedrive", label: "OneDrive", icon: Cloud, state: "preview" },
      { href: "/onedrive/accounts", label: "Accounts", icon: Users, state: "preview" },
      { href: "/onedrive/sharing", label: "Sharing", icon: Share2, state: "preview" },
      { href: "/exchange", label: "Exchange", icon: Mail, state: "preview" },
      { href: "/exchange/mailboxes", label: "Mailboxes", icon: Mail, state: "preview" },
      { href: "/exchange/permissions", label: "Permissions", icon: Lock, state: "preview" },
      { href: "/exchange/forwarding-risk", label: "Forwarding risk", icon: AlertTriangle, state: "preview" },
      { href: "/teams", label: "Teams", icon: Users2, state: "preview" },
      { href: "/teams/inventory", label: "Inventory", icon: Library, state: "preview" },
      { href: "/teams/members", label: "Members", icon: Users, state: "preview" },
      { href: "/service-health", label: "Service health", icon: Gauge, state: "preview" },
    ],
  },
  {
    title: "Security",
    items: [
      { href: "/security/alerts", label: "Alerts", icon: ShieldAlert, state: "preview", permission: "security.alerts.read" },
      { href: "/security/rules", label: "Rules", icon: Shield, state: "preview", permission: "security.rules.read" },
      { href: "/security/investigations", label: "Investigations", icon: Search, state: "soon", permission: "security.alerts.read" },
      { href: "/content-search", label: "Content search", icon: Search, state: "off" },
      { href: "/remediation", label: "Remediation", icon: Trash2, state: "off" },
    ],
  },
  {
    title: "Admin",
    items: [
      { href: "/jobs", label: "Sync jobs", icon: Workflow, state: "preview" },
      { href: "/notifications", label: "Notifications", icon: Bell, state: "preview" },
      { href: "/system-health", label: "System health", icon: Gauge, state: "active", permission: "platform.admin" },
      { href: "/settings", label: "Settings", icon: Settings, state: "preview" },
      { href: "/settings/graph", label: "Graph connection", icon: Plug, state: "preview", permission: "platform.admin" },
      { href: "/settings/tenant", label: "Tenant", icon: Building2, state: "preview", permission: "platform.admin" },
      { href: "/settings/security", label: "Security", icon: ShieldCheck, state: "preview", permission: "platform.admin" },
      { href: "/settings/retention", label: "Retention", icon: Trash2, state: "preview", permission: "platform.admin" },
      { href: "/settings/notifications", label: "Notifications", icon: Bell, state: "preview", permission: "platform.admin" },
      { href: "/settings/general", label: "General", icon: Settings, state: "preview", permission: "platform.admin" },
      { href: "/settings/reports", label: "Reports", icon: FileSpreadsheet, state: "preview", permission: "platform.admin" },
      { href: "/settings/users", label: "Users", icon: Users, state: "preview", permission: "platform.users.read" },
      { href: "/delegation", label: "Delegation / RBAC", icon: KeyRound, state: "soon", permission: "platform.roles.read" },
    ],
  },
  {
    title: "Help",
    items: [
      { href: "/help", label: "Documentation", icon: BookOpen, state: "active" },
      { href: "/capability-matrix", label: "Capability matrix", icon: Map, state: "active" },
      { href: "/catalog", label: "Feature catalog", icon: Library, state: "active" },
    ],
  },
];

function stateBadge(state: Item["state"]) {
  if (state === "active") return null;
  if (state === "preview")
    return (
      <span className="rounded-full bg-sky-500/10 px-1.5 py-0.5 text-[10px] text-sky-300 ring-1 ring-sky-500/20">
        preview
      </span>
    );
  if (state === "soon")
    return (
      <span className="rounded-full bg-slate-500/10 px-1.5 py-0.5 text-[10px] text-slate-400 ring-1 ring-slate-500/20">
        soon
      </span>
    );
  if (state === "off")
    return (
      <span className="rounded-full bg-amber-500/10 px-1.5 py-0.5 text-[10px] text-amber-300 ring-1 ring-amber-500/30">
        off
      </span>
    );
  return null;
}

export function Sidebar({
  currentPath,
  permissions = [],
}: {
  currentPath: string;
  permissions?: string[];
}) {
  const allowed = new Set(permissions);
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});

  return (
    <aside className="hidden w-72 shrink-0 lg:block">
      <div className="sticky top-0 max-h-screen overflow-y-auto px-3 py-5">
        <div className="mb-4 flex items-center gap-2 px-2">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-brand-500 via-violet-500 to-rose-500 shadow-glow-brand">
            <ShieldCheck className="h-4 w-4 text-white" />
          </div>
          <div>
            <div className="text-xs font-medium uppercase tracking-widest text-brand-300">
              TenantGuard
            </div>
            <div className="text-sm font-semibold text-slate-100">365 Control Center</div>
          </div>
        </div>

        <nav className="space-y-4">
          {groups.map((g) => {
            const items = g.items.filter(
              (it) => !it.permission || allowed.has(it.permission),
            );
            if (items.length === 0) return null;
            const isCollapsed = collapsed[g.title] ?? false;
            return (
              <div key={g.title} className="relative">
                <button
                  type="button"
                  onClick={() =>
                    setCollapsed((s) => ({ ...s, [g.title]: !isCollapsed }))
                  }
                  className="flex w-full items-center justify-between rounded-lg px-2 py-1 text-[10px] font-semibold uppercase tracking-widest text-slate-400 hover:text-slate-200"
                >
                  <span>{g.title}</span>
                  <span className="text-slate-600">{isCollapsed ? "▸" : "▾"}</span>
                </button>
                {!isCollapsed ? (
                  <ul className="mt-1 space-y-0.5">
                    {items.map((it) => {
                      const active = currentPath === it.href;
                      const Icon = it.icon ?? LifeBuoy;
                      return (
                        <li key={it.href}>
                          <Link
                            href={it.href}
                            className={cn(
                              "group relative flex items-center justify-between rounded-lg px-2 py-1.5 text-sm transition-colors",
                              active
                                ? "bg-gradient-to-r from-brand-500/15 to-transparent text-slate-50 ring-1 ring-brand-500/25"
                                : "text-slate-300 hover:bg-slate-900/60 hover:text-slate-100",
                            )}
                          >
                            {active ? (
                              <span className="absolute inset-y-1 left-0 w-0.5 rounded-full bg-gradient-to-b from-brand-400 to-violet-400" />
                            ) : null}
                            <span className="flex items-center gap-2 truncate pl-1">
                              <Icon
                                className={cn(
                                  "h-3.5 w-3.5 shrink-0",
                                  active
                                    ? "text-brand-300"
                                    : "text-slate-500 group-hover:text-slate-300",
                                )}
                              />
                              <span className="truncate">{it.label}</span>
                            </span>
                            {stateBadge(it.state)}
                          </Link>
                        </li>
                      );
                    })}
                  </ul>
                ) : null}
              </div>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
