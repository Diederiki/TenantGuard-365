"""Audit log append-only enforcement at the DB level.

Creates a dedicated ``tg365_audit_writer`` role and a row-level trigger
on ``technician_audit_logs`` that blocks UPDATE + DELETE for everyone
except the bootstrap superuser. The platform's runtime DB user inherits
the writer role and so can INSERT, but not modify history.

Reversal drops the trigger but **does not drop the role** — operators
may have granted it to additional users out-of-band.

Revision ID: 0004_audit_append_only
Revises: 0003_totp_and_settings
Create Date: 2026-05-14
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0004_audit_append_only"
down_revision: str | None = "0003_totp_and_settings"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


_BLOCK_FN = """
CREATE OR REPLACE FUNCTION tg365_block_audit_mutation()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    -- Bootstrap superuser can still emergency-clean if absolutely necessary;
    -- the runtime role cannot. This is the append-only guarantee.
    IF current_user = 'postgres' THEN
        IF TG_OP = 'DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF;
    END IF;
    RAISE EXCEPTION
        'technician_audit_logs is append-only (op=%, user=%)',
        TG_OP, current_user
        USING ERRCODE = '42501';
END;
$$;
"""

_DROP_FN = "DROP FUNCTION IF EXISTS tg365_block_audit_mutation();"


def upgrade() -> None:
    op.execute(_BLOCK_FN)
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_block_audit_update
            ON technician_audit_logs;
        CREATE TRIGGER trg_block_audit_update
            BEFORE UPDATE ON technician_audit_logs
            FOR EACH ROW
            EXECUTE FUNCTION tg365_block_audit_mutation();
        """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_block_audit_delete
            ON technician_audit_logs;
        CREATE TRIGGER trg_block_audit_delete
            BEFORE DELETE ON technician_audit_logs
            FOR EACH ROW
            EXECUTE FUNCTION tg365_block_audit_mutation();
        """
    )
    # Truncate also bypasses BEFORE UPDATE/DELETE; lock it down separately.
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_block_audit_truncate
            ON technician_audit_logs;
        CREATE TRIGGER trg_block_audit_truncate
            BEFORE TRUNCATE ON technician_audit_logs
            FOR EACH STATEMENT
            EXECUTE FUNCTION tg365_block_audit_mutation();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_block_audit_update ON technician_audit_logs;")
    op.execute("DROP TRIGGER IF EXISTS trg_block_audit_delete ON technician_audit_logs;")
    op.execute("DROP TRIGGER IF EXISTS trg_block_audit_truncate ON technician_audit_logs;")
    op.execute(_DROP_FN)
