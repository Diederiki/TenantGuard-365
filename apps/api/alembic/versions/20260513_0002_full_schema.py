"""full schema — Entra / SharePoint / Exchange / OneDrive / Teams / security / reports / remediation

Revision ID: 0002_full_schema
Revises: 0001_baseline
Create Date: 2026-05-13
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_full_schema"
down_revision: str | None = "0001_baseline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _ts() -> sa.Column:
    return sa.Column("created_at", sa.DateTime(timezone=True), nullable=False)


def upgrade() -> None:  # noqa: PLR0915
    # =========================================================================
    # Graph plumbing
    # =========================================================================
    op.create_table(
        "app_registrations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),  # collector | portal
        sa.Column("client_id", sa.String(64), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("granted_scopes", postgresql.ARRAY(sa.String), nullable=False, server_default=sa.text("ARRAY[]::varchar[]")),
        sa.Column("last_consent_check_at", sa.DateTime(timezone=True)),
        sa.Column("notes", sa.Text),
    )
    op.create_table(
        "graph_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scope", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False),  # application | delegated
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("required_for_modules", postgresql.ARRAY(sa.String), nullable=False, server_default=sa.text("ARRAY[]::varchar[]")),
        sa.UniqueConstraint("scope", "kind", name="uq_graph_permission_scope_kind"),
    )
    op.create_table(
        "graph_sync_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.String(128), nullable=False),  # module.collector
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("schedule_cron", sa.String(64)),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("last_success_at", sa.DateTime(timezone=True)),
        sa.Column("last_failure_at", sa.DateTime(timezone=True)),
        sa.Column("last_run_id", postgresql.UUID(as_uuid=True)),
        sa.UniqueConstraint("tenant_id", "key", name="uq_graph_sync_job_tenant_key"),
    )
    op.create_table(
        "graph_sync_job_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("graph_sync_jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="running"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("rows_in", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("rows_out", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("error", sa.Text),
        sa.Column("metrics", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True)),
    )
    op.create_index("ix_graph_sync_job_runs_job_started", "graph_sync_job_runs", ["job_id", sa.text("started_at DESC")])
    op.create_table(
        "graph_delta_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("resource", sa.String(128), nullable=False),
        sa.Column("delta_link", sa.Text),
        sa.Column("last_full_sync_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("tenant_id", "resource", name="uq_delta_tenant_resource"),
    )
    op.create_table(
        "graph_webhook_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subscription_id", sa.String(128)),
        sa.Column("resource", sa.String(255), nullable=False),
        sa.Column("client_state", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_renewed_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "graph_token_cache",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("envelope", sa.LargeBinary, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )

    # =========================================================================
    # Entra ID
    # =========================================================================
    op.create_table(
        "m365_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entra_object_id", sa.String(64), nullable=False),
        sa.Column("user_principal_name", sa.String(320), nullable=False),
        sa.Column("display_name", sa.String(255)),
        sa.Column("given_name", sa.String(128)),
        sa.Column("surname", sa.String(128)),
        sa.Column("mail", sa.String(320)),
        sa.Column("user_type", sa.String(32)),  # Member | Guest
        sa.Column("account_enabled", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("department", sa.String(128)),
        sa.Column("job_title", sa.String(255)),
        sa.Column("country", sa.String(64)),
        sa.Column("created_date_time", sa.DateTime(timezone=True)),
        sa.Column("last_signin_at", sa.DateTime(timezone=True)),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("tenant_id", "entra_object_id", name="uq_m365_user_tenant_oid"),
    )
    op.create_index("ix_m365_users_upn", "m365_users", ["tenant_id", "user_principal_name"])
    op.create_index("ix_m365_users_type", "m365_users", ["tenant_id", "user_type"])

    op.create_table(
        "m365_groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entra_object_id", sa.String(64), nullable=False),
        sa.Column("display_name", sa.String(255)),
        sa.Column("description", sa.Text),
        sa.Column("mail_enabled", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("security_enabled", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("mail", sa.String(320)),
        sa.Column("visibility", sa.String(32)),
        sa.Column("group_types", postgresql.ARRAY(sa.String), nullable=False, server_default=sa.text("ARRAY[]::varchar[]")),
        sa.Column("created_date_time", sa.DateTime(timezone=True)),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("tenant_id", "entra_object_id", name="uq_m365_group_tenant_oid"),
    )

    op.create_table(
        "m365_group_memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("group_object_id", sa.String(64), nullable=False),
        sa.Column("member_object_id", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False, server_default="member"),  # member | owner
        sa.UniqueConstraint("tenant_id", "group_object_id", "member_object_id", "kind", name="uq_m365_membership"),
    )

    op.create_table(
        "m365_licenses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sku_id", sa.String(64), nullable=False),
        sa.Column("sku_part_number", sa.String(64), nullable=False),
        sa.Column("consumed_units", sa.Integer, nullable=False, server_default="0"),
        sa.Column("prepaid_units_enabled", sa.Integer, nullable=False, server_default="0"),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("tenant_id", "sku_id", name="uq_m365_license_tenant_sku"),
    )

    op.create_table(
        "m365_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entra_role_id", sa.String(64), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.UniqueConstraint("tenant_id", "entra_role_id", name="uq_m365_role_tenant_id"),
    )

    op.create_table(
        "m365_role_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entra_role_id", sa.String(64), nullable=False),
        sa.Column("principal_object_id", sa.String(64), nullable=False),
        sa.Column("principal_kind", sa.String(32), nullable=False),
        sa.UniqueConstraint("tenant_id", "entra_role_id", "principal_object_id", name="uq_m365_role_assignment"),
    )

    op.create_table(
        "entra_signins",
        sa.Column("id", sa.BigInteger, sa.Identity(always=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("entra_id", sa.String(128)),
        sa.Column("user_object_id", sa.String(64)),
        sa.Column("user_principal_name", sa.String(320)),
        sa.Column("app_display_name", sa.String(255)),
        sa.Column("ip_address", postgresql.INET),
        sa.Column("status_code", sa.Integer),
        sa.Column("conditional_access_status", sa.String(32)),
        sa.Column("risk_level", sa.String(32)),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.PrimaryKeyConstraint("id", "event_time"),
    )
    op.create_index("ix_entra_signins_tenant_time", "entra_signins", ["tenant_id", sa.text("event_time DESC")])
    op.create_index("ix_entra_signins_user_time", "entra_signins", ["user_object_id", sa.text("event_time DESC")])

    op.create_table(
        "entra_directory_audits",
        sa.Column("id", sa.BigInteger, sa.Identity(always=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("entra_id", sa.String(128)),
        sa.Column("category", sa.String(64)),
        sa.Column("activity_display_name", sa.String(255)),
        sa.Column("operation_type", sa.String(64)),
        sa.Column("result", sa.String(32)),
        sa.Column("initiated_by", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("target_resources", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.PrimaryKeyConstraint("id", "event_time"),
    )
    op.create_index("ix_entra_audits_tenant_time", "entra_directory_audits", ["tenant_id", sa.text("event_time DESC")])
    op.create_index("ix_entra_audits_activity", "entra_directory_audits", ["activity_display_name"])

    # =========================================================================
    # Exchange Online
    # =========================================================================
    op.create_table(
        "exchange_mailboxes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_object_id", sa.String(64), nullable=False),
        sa.Column("primary_smtp", sa.String(320)),
        sa.Column("mailbox_type", sa.String(32)),  # user|shared|room|equipment
        sa.Column("forwarding_smtp", sa.String(320)),
        sa.Column("forwarding_external", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("inbox_rules_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("tenant_id", "user_object_id", name="uq_mailbox_tenant_user"),
    )
    op.create_table(
        "exchange_mailbox_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mailbox_user_object_id", sa.String(64), nullable=False),
        sa.Column("grantee_object_id", sa.String(64), nullable=False),
        sa.Column("permission_kind", sa.String(32), nullable=False),  # FullAccess|SendAs|SendOnBehalf
        sa.Column("source", sa.String(32), nullable=False, server_default="exo"),
        sa.UniqueConstraint("tenant_id", "mailbox_user_object_id", "grantee_object_id", "permission_kind", name="uq_mailbox_perm"),
    )
    op.create_table(
        "exchange_mailbox_audit_events",
        sa.Column("id", sa.BigInteger, sa.Identity(always=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("mailbox_user_object_id", sa.String(64)),
        sa.Column("operation", sa.String(64)),
        sa.Column("logon_type", sa.String(32)),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.PrimaryKeyConstraint("id", "event_time"),
    )
    op.create_index("ix_exch_audit_tenant_time", "exchange_mailbox_audit_events", ["tenant_id", sa.text("event_time DESC")])

    # =========================================================================
    # SharePoint Online
    # =========================================================================
    op.create_table(
        "sharepoint_sites",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("graph_id", sa.String(255), nullable=False),  # composite id
        sa.Column("web_url", sa.Text, nullable=False),
        sa.Column("display_name", sa.String(255)),
        sa.Column("name", sa.String(255)),
        sa.Column("description", sa.Text),
        sa.Column("is_personal_site", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_date_time", sa.DateTime(timezone=True)),
        sa.Column("last_modified_date_time", sa.DateTime(timezone=True)),
        sa.Column("storage_used_bytes", sa.BigInteger),
        sa.Column("hub_site_id", sa.String(64)),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("tenant_id", "graph_id", name="uq_sp_site_tenant_graphid"),
    )
    op.create_table(
        "sharepoint_drives",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("site_graph_id", sa.String(255), nullable=False),
        sa.Column("drive_id", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255)),
        sa.Column("drive_type", sa.String(32)),
        sa.Column("quota_used_bytes", sa.BigInteger),
        sa.Column("quota_total_bytes", sa.BigInteger),
        sa.UniqueConstraint("tenant_id", "drive_id", name="uq_sp_drive_tenant_id"),
    )
    op.create_table(
        "sharepoint_lists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("site_graph_id", sa.String(255), nullable=False),
        sa.Column("list_id", sa.String(64), nullable=False),
        sa.Column("display_name", sa.String(255)),
        sa.Column("template", sa.String(64)),
        sa.Column("item_count", sa.BigInteger, nullable=False, server_default="0"),
        sa.UniqueConstraint("tenant_id", "list_id", name="uq_sp_list_tenant_id"),
    )
    op.create_table(
        "sharepoint_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("drive_id", sa.String(255), nullable=False),
        sa.Column("item_id", sa.String(255), nullable=False),
        sa.Column("name", sa.String(512)),
        sa.Column("path", sa.Text),
        sa.Column("size_bytes", sa.BigInteger),
        sa.Column("kind", sa.String(16)),  # file|folder
        sa.Column("last_modified_date_time", sa.DateTime(timezone=True)),
        sa.Column("shared", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.UniqueConstraint("tenant_id", "drive_id", "item_id", name="uq_sp_item"),
    )
    op.create_index("ix_sp_items_drive_path", "sharepoint_items", ["tenant_id", "drive_id", "path"])
    op.create_table(
        "sharepoint_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scope_kind", sa.String(16), nullable=False),  # site|drive|item
        sa.Column("scope_id", sa.String(255), nullable=False),
        sa.Column("permission_id", sa.String(128), nullable=False),
        sa.Column("inherited_from", sa.String(255)),
        sa.Column("roles", postgresql.ARRAY(sa.String), nullable=False, server_default=sa.text("ARRAY[]::varchar[]")),
        sa.Column("grantee_kind", sa.String(32)),  # user|group|link|application
        sa.Column("grantee_principal", sa.String(320)),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("tenant_id", "scope_kind", "scope_id", "permission_id", name="uq_sp_perm"),
    )
    op.create_index("ix_sp_perm_grantee", "sharepoint_permissions", ["tenant_id", "grantee_kind", "grantee_principal"])
    op.create_table(
        "sharepoint_sharing_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scope_kind", sa.String(16), nullable=False),
        sa.Column("scope_id", sa.String(255), nullable=False),
        sa.Column("link_id", sa.String(128), nullable=False),
        sa.Column("scope", sa.String(32)),  # anonymous|organization|users
        sa.Column("type", sa.String(32)),   # view|edit|embed
        sa.Column("web_url", sa.Text),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("tenant_id", "link_id", name="uq_sp_link"),
    )
    op.create_index("ix_sp_links_scope", "sharepoint_sharing_links", ["tenant_id", "scope"])
    op.create_table(
        "sharepoint_audit_events",
        sa.Column("id", sa.BigInteger, sa.Identity(always=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("site_url", sa.Text),
        sa.Column("user_object_id", sa.String(64)),
        sa.Column("user_principal_name", sa.String(320)),
        sa.Column("operation", sa.String(64)),
        sa.Column("item_path", sa.Text),
        sa.Column("client_ip", postgresql.INET),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.PrimaryKeyConstraint("id", "event_time"),
    )
    op.create_index("ix_sp_audit_tenant_time", "sharepoint_audit_events", ["tenant_id", sa.text("event_time DESC")])
    op.create_index("ix_sp_audit_op", "sharepoint_audit_events", ["operation"])

    # =========================================================================
    # OneDrive
    # =========================================================================
    op.create_table(
        "onedrive_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_object_id", sa.String(64), nullable=False),
        sa.Column("drive_id", sa.String(255), nullable=False),
        sa.Column("storage_used_bytes", sa.BigInteger),
        sa.Column("storage_quota_bytes", sa.BigInteger),
        sa.Column("last_activity_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("tenant_id", "user_object_id", name="uq_onedrive_account"),
    )
    op.create_table(
        "onedrive_audit_events",
        sa.Column("id", sa.BigInteger, sa.Identity(always=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_object_id", sa.String(64)),
        sa.Column("operation", sa.String(64)),
        sa.Column("item_path", sa.Text),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.PrimaryKeyConstraint("id", "event_time"),
    )
    op.create_index("ix_od_audit_tenant_time", "onedrive_audit_events", ["tenant_id", sa.text("event_time DESC")])

    # =========================================================================
    # Teams
    # =========================================================================
    op.create_table(
        "teams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entra_group_id", sa.String(64), nullable=False),
        sa.Column("display_name", sa.String(255)),
        sa.Column("description", sa.Text),
        sa.Column("visibility", sa.String(32)),
        sa.Column("specialization", sa.String(32)),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("tenant_id", "entra_group_id", name="uq_teams_tenant_group"),
    )
    op.create_table(
        "teams_channels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("team_group_id", sa.String(64), nullable=False),
        sa.Column("channel_id", sa.String(128), nullable=False),
        sa.Column("display_name", sa.String(255)),
        sa.Column("membership_type", sa.String(32)),  # standard|private|shared
        sa.UniqueConstraint("tenant_id", "channel_id", name="uq_teams_channel"),
    )
    op.create_table(
        "teams_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("team_group_id", sa.String(64), nullable=False),
        sa.Column("user_object_id", sa.String(64), nullable=False),
        sa.Column("roles", postgresql.ARRAY(sa.String), nullable=False, server_default=sa.text("ARRAY[]::varchar[]")),
        sa.UniqueConstraint("tenant_id", "team_group_id", "user_object_id", name="uq_teams_member"),
    )
    op.create_table(
        "teams_audit_events",
        sa.Column("id", sa.BigInteger, sa.Identity(always=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("team_group_id", sa.String(64)),
        sa.Column("operation", sa.String(64)),
        sa.Column("user_object_id", sa.String(64)),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.PrimaryKeyConstraint("id", "event_time"),
    )
    op.create_index("ix_teams_audit_tenant_time", "teams_audit_events", ["tenant_id", sa.text("event_time DESC")])

    # =========================================================================
    # Service health
    # =========================================================================
    op.create_table(
        "service_health_overviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("service", sa.String(128), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("tenant_id", "service", name="uq_svc_health_overview"),
    )
    op.create_table(
        "service_health_issues",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("issue_id", sa.String(64), nullable=False),
        sa.Column("title", sa.String(512)),
        sa.Column("service", sa.String(128)),
        sa.Column("status", sa.String(64)),
        sa.Column("classification", sa.String(64)),
        sa.Column("impact_description", sa.Text),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("tenant_id", "issue_id", name="uq_svc_health_issue"),
    )

    # =========================================================================
    # Security ops
    # =========================================================================
    op.create_table(
        "security_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("key", sa.String(128), nullable=False, unique=True),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False, server_default="attention"),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("config", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_table(
        "security_alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rule_key", sa.String(128), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="new"),  # new|investigating|resolved|false_positive
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("entity_kind", sa.String(64)),
        sa.Column("entity_id", sa.String(255)),
        sa.Column("dedup_key", sa.String(255), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("occurrences", sa.Integer, nullable=False, server_default="1"),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True)),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("tenant_id", "rule_key", "dedup_key", name="uq_alert_dedup"),
    )
    op.create_index("ix_alerts_status_severity", "security_alerts", ["tenant_id", "status", "severity"])
    op.create_table(
        "security_rule_matches",
        sa.Column("id", sa.BigInteger, sa.Identity(always=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("rule_key", sa.String(128), nullable=False),
        sa.Column("alert_id", postgresql.UUID(as_uuid=True)),
        sa.Column("evidence", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.PrimaryKeyConstraint("id", "event_time"),
    )
    op.create_index("ix_rule_matches_alert", "security_rule_matches", ["alert_id"])
    op.create_table(
        "investigation_cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="open"),  # open|in_progress|closed
        sa.Column("priority", sa.String(16), nullable=False, server_default="medium"),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True)),
        sa.Column("summary", sa.Text),
    )
    op.create_table(
        "investigation_case_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("investigation_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),  # note|evidence|alert_link|status_change
        sa.Column("actor_id", postgresql.UUID(as_uuid=True)),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
    )

    # =========================================================================
    # Reporting
    # =========================================================================
    op.create_table(
        "saved_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("source", sa.String(64), nullable=False),  # built-in source name
        sa.Column("columns", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("filters", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True)),
        sa.UniqueConstraint("tenant_id", "key", name="uq_report_tenant_key"),
    )
    op.create_table(
        "report_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("saved_reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("rows", sa.BigInteger),
        sa.Column("status", sa.String(32), nullable=False, server_default="running"),
        sa.Column("triggered_by", postgresql.UUID(as_uuid=True)),
    )
    op.create_table(
        "report_exports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("report_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("format", sa.String(8), nullable=False),  # csv|xlsx|pdf|html
        sa.Column("size_bytes", sa.BigInteger),
        sa.Column("checksum_sha256", sa.String(64)),
        sa.Column("object_key", sa.String(512)),
        sa.Column("downloaded_at", sa.DateTime(timezone=True)),
        sa.Column("downloaded_by", postgresql.UUID(as_uuid=True)),
    )
    op.create_table(
        "scheduled_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("saved_reports.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cron", sa.String(64), nullable=False),
        sa.Column("formats", postgresql.ARRAY(sa.String), nullable=False, server_default=sa.text("ARRAY['csv']::varchar[]")),
        sa.Column("email_to", postgresql.ARRAY(sa.String), nullable=False, server_default=sa.text("ARRAY[]::varchar[]")),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("next_run_at", sa.DateTime(timezone=True)),
        sa.Column("last_run_at", sa.DateTime(timezone=True)),
    )

    # =========================================================================
    # Notifications
    # =========================================================================
    op.create_table(
        "notification_channels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),  # email | webhook | teams
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("config", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("true")),
    )
    op.create_table(
        "notification_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("notification_channels.id", ondelete="SET NULL")),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("result", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("body_summary", sa.Text),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
    )

    # =========================================================================
    # Content search
    # =========================================================================
    op.create_table(
        "content_search_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("scope", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("patterns", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("alert_on_match", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
    )
    op.create_table(
        "content_search_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_search_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="queued"),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("matches_total", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("triggered_by", postgresql.UUID(as_uuid=True)),
        sa.Column("metrics", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
    )

    # =========================================================================
    # Remediation
    # =========================================================================
    op.create_table(
        "remediation_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("key", sa.String(128), nullable=False, unique=True),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("required_permission", sa.String(128), nullable=False),
        sa.Column("required_scopes", postgresql.ARRAY(sa.String), nullable=False, server_default=sa.text("ARRAY[]::varchar[]")),
        sa.Column("supports_rollback", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("dry_run_default", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("false")),  # OFF
        sa.Column("approval_required", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("destructive", sa.Boolean, nullable=False, server_default=sa.text("true")),
    )
    op.create_table(
        "remediation_actions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("policy_key", sa.String(128), nullable=False),
        sa.Column("submitter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending_approval"),
        sa.Column("mode", sa.String(16), nullable=False, server_default="dry_run"),
        sa.Column("target_kind", sa.String(64)),
        sa.Column("target_id", sa.String(255)),
        sa.Column("parameters", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("dry_run_result", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("apply_result", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True)),
        sa.Column("rolled_back_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "remediation_approvals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("action_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("remediation_actions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("approver_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload_hash", sa.LargeBinary, nullable=False),
        sa.Column("comment", sa.Text),
    )


def downgrade() -> None:  # noqa: PLR0915
    for t in [
        "remediation_approvals",
        "remediation_actions",
        "remediation_policies",
        "content_search_runs",
        "content_search_profiles",
        "notification_events",
        "notification_channels",
        "scheduled_reports",
        "report_exports",
        "report_runs",
        "saved_reports",
        "investigation_case_events",
        "investigation_cases",
        "security_rule_matches",
        "security_alerts",
        "security_rules",
        "service_health_issues",
        "service_health_overviews",
        "teams_audit_events",
        "teams_members",
        "teams_channels",
        "teams",
        "onedrive_audit_events",
        "onedrive_accounts",
        "sharepoint_audit_events",
        "sharepoint_sharing_links",
        "sharepoint_permissions",
        "sharepoint_items",
        "sharepoint_lists",
        "sharepoint_drives",
        "sharepoint_sites",
        "exchange_mailbox_audit_events",
        "exchange_mailbox_permissions",
        "exchange_mailboxes",
        "entra_directory_audits",
        "entra_signins",
        "m365_role_assignments",
        "m365_roles",
        "m365_licenses",
        "m365_group_memberships",
        "m365_groups",
        "m365_users",
        "graph_token_cache",
        "graph_webhook_subscriptions",
        "graph_delta_tokens",
        "graph_sync_job_runs",
        "graph_sync_jobs",
        "graph_permissions",
        "app_registrations",
    ]:
        op.drop_table(t)


_ts = _ts  # silence unused
