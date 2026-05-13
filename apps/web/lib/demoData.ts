/**
 * Demo-mode fixtures. Returned by lib/api.ts helpers when the `tg365_demo=1`
 * cookie is set. Lets you click around the UI without a live API.
 */

import type { AuditEntry, AuditPage, MeResponse } from "./api";

export const DEMO_ME: MeResponse = {
  id: "00000000-0000-0000-0000-000000000001",
  email: "admin@dev.local",
  display_name: "Local Admin (Demo)",
  is_active: true,
  role_keys: ["platform_admin"],
  permissions: [
    "platform.admin",
    "audit.read",
    "audit.read.raw",
    "audit.export",
    "reports.read",
    "reports.run",
    "reports.create",
    "reports.export",
    "reports.schedule",
    "entra.users.read",
    "entra.groups.read",
    "entra.signins.read",
    "entra.audits.read",
    "sharepoint.sites.read",
    "sharepoint.permissions.read",
    "security.alerts.read",
    "security.rules.read",
    "platform.users.read",
    "platform.users.manage",
    "platform.roles.read",
    "platform.roles.manage",
  ],
};

const NOW = "2026-05-13T13:00:00Z";

export const DEMO_AUDIT: AuditPage = {
  next_cursor: null,
  items: [
    {
      id: 11,
      tenant_id: "11111111-1111-1111-1111-111111111111",
      actor_id: DEMO_ME.id,
      actor_display: DEMO_ME.display_name,
      actor_type: "user",
      action: "auth.signin.success",
      target_type: "platform_user",
      target_id: DEMO_ME.id,
      target_label: DEMO_ME.email,
      result: "success",
      event_time: NOW,
    },
    {
      id: 10,
      tenant_id: "11111111-1111-1111-1111-111111111111",
      actor_id: DEMO_ME.id,
      actor_display: DEMO_ME.display_name,
      actor_type: "user",
      action: "report.export.downloaded",
      target_type: "saved_report",
      target_id: "rep-anon-links",
      target_label: "SharePoint anonymous links",
      result: "success",
      event_time: "2026-05-13T12:51:09Z",
    },
    {
      id: 9,
      tenant_id: "11111111-1111-1111-1111-111111111111",
      actor_id: DEMO_ME.id,
      actor_display: DEMO_ME.display_name,
      actor_type: "user",
      action: "security.rules.evaluated",
      target_type: null,
      target_id: null,
      target_label: null,
      result: "success",
      event_time: "2026-05-13T12:45:00Z",
    },
    {
      id: 8,
      tenant_id: "11111111-1111-1111-1111-111111111111",
      actor_id: null,
      actor_display: "system",
      actor_type: "system",
      action: "collector.run.ok",
      target_type: "collector",
      target_id: "entra.users",
      target_label: "Entra users",
      result: "success",
      event_time: "2026-05-13T12:30:00Z",
    },
    {
      id: 7,
      tenant_id: "11111111-1111-1111-1111-111111111111",
      actor_id: null,
      actor_display: "system",
      actor_type: "system",
      action: "collector.run.ok",
      target_type: "collector",
      target_id: "sharepoint.sites",
      target_label: "SharePoint sites",
      result: "success",
      event_time: "2026-05-13T12:00:00Z",
    },
    {
      id: 6,
      tenant_id: "11111111-1111-1111-1111-111111111111",
      actor_id: DEMO_ME.id,
      actor_display: DEMO_ME.display_name,
      actor_type: "user",
      action: "alert.updated",
      target_type: "security_alert",
      target_id: "alert-anon-1",
      target_label: "Anonymous SharePoint link on /sites/Finance",
      result: "success",
      event_time: "2026-05-13T11:42:11Z",
    },
    {
      id: 5,
      tenant_id: "11111111-1111-1111-1111-111111111111",
      actor_id: DEMO_ME.id,
      actor_display: DEMO_ME.display_name,
      actor_type: "user",
      action: "tenant.graph.connected",
      target_type: "tenant",
      target_id: "11111111-1111-1111-1111-111111111111",
      target_label: "Local Dev Tenant",
      result: "success",
      event_time: "2026-05-13T11:00:00Z",
    },
  ] as AuditEntry[],
};

export const DEMO_HEALTH = {
  api: { ok: true, status: "ok" },
  ready: { ok: true, status: "ok" },
};

export const DEMO_COLLECTORS = [
  {
    key: "entra.users",
    module: "entra",
    display_name: "Entra users",
    required_scopes: ["User.Read.All"],
    schedule_cron: "*/30 * * * *",
    description: "Mirror /users into m365_users.",
  },
  {
    key: "entra.groups",
    module: "entra",
    display_name: "Entra groups",
    required_scopes: ["Group.Read.All", "GroupMember.Read.All"],
    schedule_cron: "0 */6 * * *",
    description: "Mirror /groups into m365_groups.",
  },
  {
    key: "entra.licenses",
    module: "entra",
    display_name: "Subscribed SKUs",
    required_scopes: ["Organization.Read.All"],
    schedule_cron: "0 */12 * * *",
    description: "Mirror /subscribedSkus.",
  },
  {
    key: "entra.signins",
    module: "entra",
    display_name: "Entra sign-in logs",
    required_scopes: ["AuditLog.Read.All"],
    schedule_cron: "*/30 * * * *",
    description: "License-gated. Entra ID P1+.",
  },
  {
    key: "entra.directoryAudits",
    module: "entra",
    display_name: "Entra directory audit log",
    required_scopes: ["AuditLog.Read.All"],
    schedule_cron: "*/30 * * * *",
    description: "Directory audit log.",
  },
  {
    key: "sharepoint.sites",
    module: "sharepoint",
    display_name: "SharePoint sites",
    required_scopes: ["Sites.Read.All"],
    schedule_cron: "0 */6 * * *",
    description: "Inventory /sites?search=*.",
  },
  {
    key: "sharepoint.drives",
    module: "sharepoint",
    display_name: "SharePoint drives",
    required_scopes: ["Sites.Read.All", "Files.Read.All"],
    schedule_cron: "0 */12 * * *",
    description: "Drives per site.",
  },
  {
    key: "serviceHealth.snapshot",
    module: "serviceHealth",
    display_name: "Service health snapshot",
    required_scopes: ["ServiceHealth.Read.All"],
    schedule_cron: "*/15 * * * *",
    description: "Pull current health overviews + issues.",
  },
];

export const DEMO_REPORT_DEFS = [
  {
    key: "entra.users.all",
    module: "entra",
    display_name: "Entra users — all",
    description: "Full inventory of users in the tenant.",
    columns: Array(7).fill({ key: "x", label: "y", width: 0 }),
  },
  {
    key: "entra.users.guests",
    module: "entra",
    display_name: "Entra users — guests",
    description: "Guest users in the tenant.",
    columns: Array(5).fill({ key: "x", label: "y", width: 0 }),
  },
  {
    key: "entra.users.disabled",
    module: "entra",
    display_name: "Entra users — disabled",
    description: "Accounts with accountEnabled=false.",
    columns: Array(4).fill({ key: "x", label: "y", width: 0 }),
  },
  {
    key: "entra.users.inactive",
    module: "entra",
    display_name: "Entra users — inactive (90 days)",
    description: "No sign-in in the last N days.",
    columns: Array(4).fill({ key: "x", label: "y", width: 0 }),
  },
  {
    key: "entra.groups.inventory",
    module: "entra",
    display_name: "Entra groups — inventory",
    description: "All groups visible via Microsoft Graph.",
    columns: Array(6).fill({ key: "x", label: "y", width: 0 }),
  },
  {
    key: "entra.licenses.usage",
    module: "entra",
    display_name: "Entra licenses — usage",
    description: "Consumed vs prepaid per SKU.",
    columns: Array(3).fill({ key: "x", label: "y", width: 0 }),
  },
  {
    key: "sharepoint.sites.inventory",
    module: "sharepoint",
    display_name: "SharePoint — site inventory",
    description: "All sites.",
    columns: Array(5).fill({ key: "x", label: "y", width: 0 }),
  },
  {
    key: "sharepoint.sharing.anonymous_links",
    module: "sharepoint",
    display_name: "SharePoint — anonymous sharing links",
    description: "Anonymous / anyone-with-link.",
    columns: Array(5).fill({ key: "x", label: "y", width: 0 }),
  },
  {
    key: "sharepoint.sharing.company_wide_links",
    module: "sharepoint",
    display_name: "SharePoint — company-wide sharing links",
    description: "Organization-scope links.",
    columns: Array(5).fill({ key: "x", label: "y", width: 0 }),
  },
  {
    key: "sharepoint.sites.inactive",
    module: "sharepoint",
    display_name: "SharePoint — inactive sites (180 days)",
    description: "Stale sites.",
    columns: Array(3).fill({ key: "x", label: "y", width: 0 }),
  },
  {
    key: "serviceHealth.overviews",
    module: "serviceHealth",
    display_name: "Service health — overviews",
    description: "Current status per service.",
    columns: Array(2).fill({ key: "x", label: "y", width: 0 }),
  },
  {
    key: "security.alerts.open",
    module: "security",
    display_name: "Security alerts — open",
    description: "Active alerts.",
    columns: Array(6).fill({ key: "x", label: "y", width: 0 }),
  },
];

export const DEMO_RULES = [
  {
    key: "sharepoint.anonymous_link_present",
    display_name: "Anonymous SharePoint sharing link detected",
    description: "Any item shared with the 'anonymous' link scope.",
    severity: "trouble",
    enabled_by_default: true,
  },
  {
    key: "sharepoint.org_wide_link_present",
    display_name: "Company-wide SharePoint sharing link detected",
    description: "Any item shared with the 'organization' link scope.",
    severity: "attention",
    enabled_by_default: true,
  },
  {
    key: "entra.guest_user_active",
    display_name: "Active guest user account",
    description: "Guest accounts that remain enabled.",
    severity: "attention",
    enabled_by_default: true,
  },
  {
    key: "entra.disabled_user_present",
    display_name: "Disabled-but-present user account",
    description: "User is disabled but not soft-deleted.",
    severity: "info",
    enabled_by_default: true,
  },
  {
    key: "entra.guest_count_high",
    display_name: "High guest-user count",
    description: "More than 50 active guests in tenant.",
    severity: "trouble",
    enabled_by_default: true,
  },
];

export const DEMO_ALERTS = [
  {
    id: "alert-anon-1",
    rule_key: "sharepoint.anonymous_link_present",
    severity: "trouble",
    status: "new",
    title: "Anonymous SharePoint link on /sites/Finance",
    entity_kind: "sharepoint_link",
    entity_id: "lnk_001",
    occurrences: 1,
    first_seen_at: "2026-05-13T11:42:00Z",
    last_seen_at: "2026-05-13T11:42:00Z",
    assigned_to: null,
  },
  {
    id: "alert-guest-1",
    rule_key: "entra.guest_user_active",
    severity: "attention",
    status: "investigating",
    title: "Active guest user: ext.consultant@example.com",
    entity_kind: "m365_user",
    entity_id: "u_ext_001",
    occurrences: 3,
    first_seen_at: "2026-05-11T08:00:00Z",
    last_seen_at: "2026-05-13T09:15:00Z",
    assigned_to: DEMO_ME.id,
  },
  {
    id: "alert-disabled-1",
    rule_key: "entra.disabled_user_present",
    severity: "info",
    status: "new",
    title: "Disabled user still present: jane.doe@dev.local",
    entity_kind: "m365_user",
    entity_id: "u_jd",
    occurrences: 1,
    first_seen_at: "2026-05-13T07:00:00Z",
    last_seen_at: "2026-05-13T07:00:00Z",
    assigned_to: null,
  },
];

export const DEMO_REMEDIATION_POLICIES = [
  {
    key: "sharepoint.disable_risky_sharing_link",
    display_name: "Disable risky SharePoint sharing link",
    description: "Delete an anonymous / company-wide link permission.",
    required_permission: "remediation.submit",
    required_scopes: ["Sites.Manage.All"],
    supports_rollback: false,
    destructive: true,
    dry_run_default: true,
    approval_required: true,
    enabled_by_default: false,
  },
  {
    key: "entra.remove_guest_from_group",
    display_name: "Remove guest user from group",
    description: "Remove a guest from a security or M365 group.",
    required_permission: "remediation.submit",
    required_scopes: ["GroupMember.ReadWrite.All"],
    supports_rollback: true,
    destructive: true,
    dry_run_default: true,
    approval_required: true,
    enabled_by_default: false,
  },
  {
    key: "entra.disable_account",
    display_name: "Disable user account",
    description: "Set accountEnabled=false. Reversible.",
    required_permission: "remediation.submit",
    required_scopes: ["User.EnableDisableAccount.All"],
    supports_rollback: true,
    destructive: true,
    dry_run_default: true,
    approval_required: true,
    enabled_by_default: false,
  },
  {
    key: "entra.revoke_sign_in_sessions",
    display_name: "Revoke user sign-in sessions",
    description: "Invalidate all refresh tokens.",
    required_permission: "remediation.submit",
    required_scopes: ["User.RevokeSessions.All"],
    supports_rollback: false,
    destructive: true,
    dry_run_default: true,
    approval_required: true,
    enabled_by_default: false,
  },
  {
    key: "exchange.remove_mailbox_forwarding",
    display_name: "Remove mailbox forwarding",
    description: "Disable mailbox-setting forwarding + clear forwarding rules.",
    required_permission: "remediation.submit",
    required_scopes: ["MailboxSettings.ReadWrite"],
    supports_rollback: false,
    destructive: true,
    dry_run_default: true,
    approval_required: true,
    enabled_by_default: false,
  },
];

export const DEMO_INVESTIGATIONS = [
  {
    id: "case-001",
    tenant_id: "11111111-1111-1111-1111-111111111111",
    title: "Suspicious external sharing burst on Finance site",
    status: "in_progress",
    priority: "high",
    owner_id: DEMO_ME.id,
    summary: "Multiple anonymous links created on /sites/Finance in 1h window.",
    created_at: "2026-05-13T10:00:00Z",
    updated_at: "2026-05-13T12:00:00Z",
  },
  {
    id: "case-002",
    tenant_id: "11111111-1111-1111-1111-111111111111",
    title: "Stale guest accounts review — May 2026",
    status: "open",
    priority: "medium",
    owner_id: null,
    summary: "Quarterly review of guests with no sign-in in 90 days.",
    created_at: "2026-05-12T09:30:00Z",
    updated_at: "2026-05-12T09:30:00Z",
  },
];

export const DEMO_RBAC_ROLES = [
  { id: "r1", key: "platform_admin", display_name: "Platform Admin", description: "Full administrative access.", is_builtin: true },
  { id: "r2", key: "readonly_auditor", display_name: "Read-only Auditor", description: "Read everything; cannot change anything.", is_builtin: true },
  { id: "r3", key: "security_analyst", display_name: "Security Analyst", description: "Investigate alerts and run content searches.", is_builtin: true },
  { id: "r4", key: "sharepoint_auditor", display_name: "SharePoint Auditor", description: "Read SharePoint inventory + perms + audits.", is_builtin: true },
  { id: "r5", key: "helpdesk", display_name: "Helpdesk", description: "Helpdesk lookups + reports.", is_builtin: true },
  { id: "r6", key: "report_only", display_name: "Report-only", description: "Run and export saved reports.", is_builtin: true },
];

export const DEMO_RBAC_USERS = [
  {
    id: DEMO_ME.id,
    email: DEMO_ME.email,
    display_name: DEMO_ME.display_name,
    is_active: true,
  },
];

export function isDemoCookie(cookieHeader: string): boolean {
  return /(?:^|; )tg365_demo=1\b/.test(cookieHeader);
}

/** Server-side check: cookie OR ?demo=1 in the URL OR DEMO_MODE env. */
export function isDemoRequest(
  cookieHeader: string,
  searchParams?: Record<string, string | string[] | undefined>,
): boolean {
  if (isDemoCookie(cookieHeader)) return true;
  if (process.env.DEMO_MODE === "1") return true;
  if (searchParams) {
    const v = searchParams["demo"];
    if (v === "1" || (Array.isArray(v) && v.includes("1"))) return true;
  }
  return false;
}
