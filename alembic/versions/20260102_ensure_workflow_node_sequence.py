"""Ensure workflow_node.sequence exists and is non-null (idempotent)

Revision ID: ensure_wf_node_seq
Revises: add_missing_chat_workflow_fields
Create Date: 2026-01-02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = 'ensure_wf_node_seq'
down_revision = 'add_missing_chat_workflow_fields'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = inspect(bind)

    def has_table(t):
        try:
            return insp.has_table(t)
        except Exception:
            return False

    def has_col(t, c):
        if not has_table(t):
            return False
        try:
            return c in [col['name'] for col in insp.get_columns(t)]
        except Exception:
            return False

    # Add sequence column as nullable with default, backfill sensible values, then set NOT NULL
    if has_table('workflow_node') and not has_col('workflow_node', 'sequence'):
        try:
            # Add as nullable with default 1 to be safe for inserts
            op.add_column('workflow_node', sa.Column('sequence', sa.Integer(), nullable=True, server_default=sa.text('1')))
            print('Added workflow_node.sequence (nullable, default=1)')

            # Backfill sequence per template using row_number to ensure deterministic ordering
            try:
                op.execute('''
                WITH rn AS (
                    SELECT id, ROW_NUMBER() OVER (PARTITION BY template_id ORDER BY id) AS rn
                    FROM workflow_node
                )
                UPDATE workflow_node
                SET sequence = rn.rn
                FROM rn
                WHERE workflow_node.id = rn.id
                  AND (workflow_node.sequence IS NULL OR workflow_node.sequence = 0)
                ''')
                print('Backfilled workflow_node.sequence with per-template ordering')
            except Exception as e:
                print('Backfill of workflow_node.sequence failed (non-fatal):', e)

            # Make column non-nullable now that values are populated
            try:
                op.alter_column('workflow_node', 'sequence', existing_type=sa.Integer(), nullable=False, server_default=None)
                print('Set workflow_node.sequence to NOT NULL')
            except Exception as e:
                print('Could not set workflow_node.sequence to NOT NULL (non-fatal):', e)

        except Exception as e:
            print('Skip adding workflow_node.sequence (non-fatal):', e)


def downgrade():
    # No-op downgrade to avoid accidental destructive changes
    print('Downgrade: no-op for ensure_wf_node_seq')
