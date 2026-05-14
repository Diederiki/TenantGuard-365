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

export const DEMO_TENANT_ID = "11111111-1111-1111-1111-111111111111";

export type DemoEntraUser = {
  id: string;
  user_principal_name: string;
  display_name: string;
  mail: string | null;
  user_type: "Member" | "Guest";
  account_enabled: boolean;
  job_title: string | null;
  department: string | null;
  office_location: string | null;
  last_signin_at: string | null;
};

export const DEMO_ENTRA_USERS: DemoEntraUser[] = [
  { id: "u-001", user_principal_name: "alice.admin@dev.local", display_name: "Alice Admin", mail: "alice.admin@dev.local", user_type: "Member", account_enabled: true, job_title: "Platform Admin", department: "IT", office_location: "HQ", last_signin_at: "2026-05-13T07:51:00Z" },
  { id: "u-002", user_principal_name: "bob.analyst@dev.local", display_name: "Bob Analyst", mail: "bob.analyst@dev.local", user_type: "Member", account_enabled: true, job_title: "Security Analyst", department: "Security", office_location: "HQ", last_signin_at: "2026-05-13T08:12:00Z" },
  { id: "u-003", user_principal_name: "charlie.contractor#EXT#@dev.onmicrosoft.com", display_name: "Charlie Contractor", mail: "charlie@partner.example", user_type: "Guest", account_enabled: true, job_title: "Contractor", department: null, office_location: null, last_signin_at: "2026-04-01T14:00:00Z" },
  { id: "u-004", user_principal_name: "dana.disabled@dev.local", display_name: "Dana Disabled", mail: "dana.disabled@dev.local", user_type: "Member", account_enabled: false, job_title: "Sales", department: "Sales", office_location: "Branch-2", last_signin_at: "2025-12-09T10:00:00Z" },
  { id: "u-005", user_principal_name: "erin.engineer@dev.local", display_name: "Erin Engineer", mail: "erin.engineer@dev.local", user_type: "Member", account_enabled: true, job_title: "Engineer", department: "Engineering", office_location: "HQ", last_signin_at: "2026-05-12T22:18:00Z" },
  { id: "u-006", user_principal_name: "frank.finance@dev.local", display_name: "Frank Finance", mail: "frank.finance@dev.local", user_type: "Member", account_enabled: true, job_title: "Controller", department: "Finance", office_location: "HQ", last_signin_at: "2026-05-13T09:01:00Z" },
  { id: "u-007", user_principal_name: "grace.guest#EXT#@dev.onmicrosoft.com", display_name: "Grace Guest", mail: "grace@vendor.example", user_type: "Guest", account_enabled: true, job_title: "Vendor PM", department: null, office_location: null, last_signin_at: "2026-02-15T11:30:00Z" },
  { id: "u-008", user_principal_name: "henry.hr@dev.local", display_name: "Henry HR", mail: "henry.hr@dev.local", user_type: "Member", account_enabled: true, job_title: "HR Lead", department: "HR", office_location: "HQ", last_signin_at: "2026-05-13T07:00:00Z" },
  { id: "u-009", user_principal_name: "ivy.intern@dev.local", display_name: "Ivy Intern", mail: "ivy.intern@dev.local", user_type: "Member", account_enabled: true, job_title: "Intern", department: "Engineering", office_location: "HQ", last_signin_at: "2026-05-10T13:45:00Z" },
  { id: "u-010", user_principal_name: "john.jansen@dev.local", display_name: "John Jansen", mail: "john.jansen@dev.local", user_type: "Member", account_enabled: true, job_title: "CFO", department: "Finance", office_location: "HQ", last_signin_at: "2026-05-13T08:55:00Z" },
];

export type DemoSpPermission = {
  id: string;
  site_url: string;
  resource: string;
  principal_display: string;
  principal_type: "User" | "Group" | "External" | "Anonymous";
  role: string;
  inheritance: "inherited" | "unique";
  granted_at: string;
};

export const DEMO_SP_PERMISSIONS: DemoSpPermission[] = [
  { id: "p-001", site_url: "/sites/finance", resource: "/sites/finance/Shared Documents/2026-Budget.xlsx", principal_display: "Frank Finance", principal_type: "User", role: "Owner", inheritance: "unique", granted_at: "2026-01-08T10:00:00Z" },
  { id: "p-002", site_url: "/sites/finance", resource: "/sites/finance/Shared Documents", principal_display: "Finance team", principal_type: "Group", role: "Member", inheritance: "inherited", granted_at: "2025-09-04T09:00:00Z" },
  { id: "p-003", site_url: "/sites/marketing", resource: "/sites/marketing/Public", principal_display: "Everyone", principal_type: "Anonymous", role: "Viewer", inheritance: "unique", granted_at: "2025-11-22T17:21:00Z" },
  { id: "p-004", site_url: "/sites/engineering", resource: "/sites/engineering/Shared Documents/Roadmap.pptx", principal_display: "grace@vendor.example", principal_type: "External", role: "Editor", inheritance: "unique", granted_at: "2026-03-02T12:00:00Z" },
  { id: "p-005", site_url: "/sites/hr", resource: "/sites/hr/Shared Documents", principal_display: "HR team", principal_type: "Group", role: "Owner", inheritance: "inherited", granted_at: "2024-06-10T08:00:00Z" },
  { id: "p-006", site_url: "/sites/legal", resource: "/sites/legal/Contracts", principal_display: "Legal team", principal_type: "Group", role: "Owner", inheritance: "inherited", granted_at: "2024-04-12T08:00:00Z" },
  { id: "p-007", site_url: "/sites/sales", resource: "/sites/sales/Forecast", principal_display: "charlie@partner.example", principal_type: "External", role: "Viewer", inheritance: "unique", granted_at: "2026-03-15T11:00:00Z" },
  { id: "p-008", site_url: "/sites/it", resource: "/sites/it/Runbooks", principal_display: "Engineering team", principal_type: "Group", role: "Member", inheritance: "inherited", granted_at: "2025-07-19T10:30:00Z" },
];

export const DEMO_GRAPH_SETTINGS = {
  tenant_id: DEMO_TENANT_ID,
  entra_tenant_id: "00000000-aaaa-bbbb-cccc-000000000000",
  portal_client_id: "11111111-2222-3333-4444-555555555555",
  collector_client_id: "66666666-7777-8888-9999-000000000000",
  portal_secret_present: true,
  collector_secret_present: true,
  feature_2fa_required: true,
  allow_local_password: false,
};

export const DEMO_ONEDRIVE = [
  { user: "alice@dev.local", used_gb: 12.4, quota_gb: 1024, last_active_at: "2026-05-13T08:00:00Z" },
  { user: "bob@dev.local", used_gb: 240.1, quota_gb: 1024, last_active_at: "2026-05-12T16:00:00Z" },
  { user: "carol@dev.local", used_gb: 0.6, quota_gb: 1024, last_active_at: "2026-04-01T09:00:00Z" },
];

export const DEMO_EXCHANGE = [
  { upn: "ceo@dev.local", mailbox_type: "user", forwarding_external: true, inbox_rules: 3 },
  { upn: "shared.invoices@dev.local", mailbox_type: "shared", forwarding_external: false, inbox_rules: 1 },
  { upn: "support@dev.local", mailbox_type: "shared", forwarding_external: false, inbox_rules: 5 },
];

export const DEMO_TEAMS: {
  name: string;
  visibility: string;
  members: number;
  guests: number;
  channels: number;
}[] = [
  { name: "All Company", visibility: "Public", members: 124, guests: 0, channels: 8 },
  { name: "Finance — Q2 close", visibility: "Private", members: 12, guests: 0, channels: 4 },
  { name: "External-Project-X", visibility: "Private", members: 9, guests: 3, channels: 6 },
];

export const DEMO_CONTENT_SEARCH_PATTERNS = [
  { key: "email_address", display_name: "Email address", severity: "info" },
  { key: "iban_eu", display_name: "EU IBAN", severity: "trouble" },
  { key: "visa_card", display_name: "Visa card number", severity: "critical" },
  { key: "us_ssn", display_name: "US Social Security Number", severity: "critical" },
  { key: "aws_access_key", display_name: "AWS access key", severity: "critical" },
];

export const DEMO_SCHEDULED_REPORTS: {
  id: string;
  report: string;
  cron: string;
  formats: string[];
  email_to: string[];
  enabled: boolean;
  next_run_at: string;
  last_run_at: string;
}[] = [
  { id: "sch-1", report: "SharePoint — anonymous sharing links", cron: "@daily", formats: ["csv", "xlsx"], email_to: ["secops@dev.local"], enabled: true, next_run_at: "2026-05-14T00:00:00Z", last_run_at: "2026-05-13T00:00:00Z" },
  { id: "sch-2", report: "Entra users — guests", cron: "@weekly", formats: ["html", "pdf"], email_to: ["compliance@dev.local"], enabled: true, next_run_at: "2026-05-19T00:00:00Z", last_run_at: "2026-05-12T00:00:00Z" },
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
