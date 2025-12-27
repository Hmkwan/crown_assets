"""Make chat_attachment.message_id nullable

Revision ID: pcam_msg_null
Revises: e8f7d6c5b4a3
Create Date: 2025-12-21 14:05:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'pcam_msg_null'
down_revision = 'e8f7d6c5b4a3'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('chat_attachment', 'message_id', existing_type=sa.Integer(), nullable=True)


def downgrade():
    op.alter_column('chat_attachment', 'message_id', existing_type=sa.Integer(), nullable=False)
