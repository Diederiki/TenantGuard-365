"""TOTP enrollments + tenant graph settings

Revision ID: 0003_totp_and_settings
Revises: 0002_full_schema
Create Date: 2026-05-13
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_totp_and_settings"
down_revision: str | None = "0002_full_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "platform_user_totps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("platform_users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("secret_encrypted", sa.LargeBinary, nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True)),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "tenant_graph_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("entra_tenant_id", sa.String(64)),
        sa.Column("portal_client_id", sa.String(64)),
        sa.Column("collector_client_id", sa.String(64)),
        # Both secrets stored encrypted via app.graph.token_cache._aead().
        sa.Column("portal_client_secret_encrypted", sa.LargeBinary),
        sa.Column("collector_client_secret_encrypted", sa.LargeBinary),
        sa.Column(
            "feature_2fa_required",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "allow_local_password",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # Add a local password hash + active 2FA enforcement flag to platform_users.
    op.add_column(
        "platform_users",
        sa.Column("password_hash", sa.LargeBinary),
    )
    op.add_column(
        "platform_users",
        sa.Column(
            "must_complete_totp",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "platform_users",
        sa.Column(
            "auth_method",
            sa.String(16),
            nullable=False,
            server_default="entra",
        ),
    )


def downgrade() -> None:
    op.drop_column("platform_users", "auth_method")
    op.drop_column("platform_users", "must_complete_totp")
    op.drop_column("platform_users", "password_hash")
    op.drop_table("tenant_graph_settings")
    op.drop_table("platform_user_totps")
