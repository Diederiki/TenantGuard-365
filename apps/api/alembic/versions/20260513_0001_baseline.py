"""baseline — tenants, platform RBAC, technician audit log

Revision ID: 0001_baseline
Revises:
Create Date: 2026-05-13

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_baseline"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("entra_tenant_id", sa.String(64)),
        sa.Column("primary_domain", sa.String(255)),
        sa.UniqueConstraint("entra_tenant_id", name="uq_tenants_entra_tenant_id"),
    )

    op.create_table(
        "tenant_connections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("last_check_at", sa.DateTime(timezone=True)),
        sa.Column("last_error", sa.Text),
        sa.Column(
            "settings",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.create_index("ix_tenant_connections_tenant_id", "tenant_connections", ["tenant_id"])

    op.create_table(
        "platform_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("entra_object_id", sa.String(64)),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.UniqueConstraint("email", name="uq_platform_users_email"),
        sa.UniqueConstraint("entra_object_id", name="uq_platform_users_entra_object_id"),
    )

    op.create_table(
        "platform_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("category", sa.String(64), nullable=False, server_default="general"),
        sa.UniqueConstraint("key", name="uq_platform_permissions_key"),
    )

    op.create_table(
        "platform_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("key", sa.String(64), nullable=False),
        sa.Column("display_name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("is_builtin", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.UniqueConstraint("key", name="uq_platform_roles_key"),
    )

    op.create_table(
        "platform_role_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("platform_roles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "permission_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("platform_permissions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    op.create_table(
        "platform_role_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("platform_users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("platform_roles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("scope", sa.String(255), nullable=False, server_default=""),
        sa.Column(
            "scope_meta",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.UniqueConstraint("user_id", "role_id", "scope", name="uq_user_role_scope"),
    )

    op.create_table(
        "technician_audit_logs",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True)),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True)),
        sa.Column("actor_display", sa.String(255), nullable=False),
        sa.Column("actor_type", sa.String(16), nullable=False, server_default="user"),
        sa.Column(
            "actor_role_ids",
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            nullable=False,
            server_default=sa.text("ARRAY[]::uuid[]"),
        ),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("target_type", sa.String(64)),
        sa.Column("target_id", sa.String(255)),
        sa.Column("target_label", sa.String(255)),
        sa.Column("old_value", postgresql.JSONB),
        sa.Column("new_value", postgresql.JSONB),
        sa.Column("result", sa.String(16), nullable=False, server_default="success"),
        sa.Column("failure_reason", sa.Text),
        sa.Column("ip", postgresql.INET),
        sa.Column("user_agent", sa.Text),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True)),
        sa.Column("request_id", postgresql.UUID(as_uuid=True)),
        sa.Column("payload_hash", sa.LargeBinary),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_audit_event_time_desc", "technician_audit_logs", [sa.text("event_time DESC")]
    )
    op.create_index(
        "ix_audit_tenant_event_time",
        "technician_audit_logs",
        ["tenant_id", sa.text("event_time DESC")],
    )
    op.create_index(
        "ix_audit_actor_event_time",
        "technician_audit_logs",
        ["actor_id", sa.text("event_time DESC")],
    )
    op.create_index("ix_audit_action", "technician_audit_logs", ["action"])

    # Append-only enforcement: refuse UPDATE on audit log rows.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION tg365_audit_immutable() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'technician_audit_logs is append-only';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER tg365_audit_no_update
        BEFORE UPDATE ON technician_audit_logs
        FOR EACH ROW EXECUTE FUNCTION tg365_audit_immutable();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS tg365_audit_no_update ON technician_audit_logs")
    op.execute("DROP FUNCTION IF EXISTS tg365_audit_immutable()")
    op.drop_index("ix_audit_action", table_name="technician_audit_logs")
    op.drop_index("ix_audit_actor_event_time", table_name="technician_audit_logs")
    op.drop_index("ix_audit_tenant_event_time", table_name="technician_audit_logs")
    op.drop_index("ix_audit_event_time_desc", table_name="technician_audit_logs")
    op.drop_table("technician_audit_logs")
    op.drop_table("platform_role_assignments")
    op.drop_table("platform_role_permissions")
    op.drop_table("platform_roles")
    op.drop_table("platform_permissions")
    op.drop_table("platform_users")
    op.drop_index("ix_tenant_connections_tenant_id", table_name="tenant_connections")
    op.drop_table("tenant_connections")
    op.drop_table("tenants")
