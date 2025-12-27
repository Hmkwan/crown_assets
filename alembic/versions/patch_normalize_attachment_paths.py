"""Normalize attachment paths to resolve /app/app/uploads ↔ /app/uploads

Revision ID: patch_normalize_attachment_paths
Revises: pcam_msg_null
Create Date: 2025-12-21 14:43:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'patch_normalize_attachment_paths'
down_revision = 'pcam_msg_null'
branch_labels = None
depends_on = None


def upgrade():
    # Replace common container duplicate prefix
    op.execute("""
        UPDATE chat_attachment
        SET file_path = REPLACE(file_path, '/app/app/uploads', '/app/uploads')
        WHERE file_path LIKE '%/app/app/uploads%'
    """)
    op.execute("""
        UPDATE chat_attachment
        SET thumbnail_path = REPLACE(thumbnail_path, '/app/app/uploads', '/app/uploads')
        WHERE thumbnail_path LIKE '%/app/app/uploads%'
    """)

    # Also normalize any leading './uploads' variants to '/uploads'
    op.execute("""
        UPDATE chat_attachment
        SET file_path = REPLACE(file_path, './uploads', '/uploads')
        WHERE file_path LIKE './uploads%'
    """)
    op.execute("""
        UPDATE chat_attachment
        SET thumbnail_path = REPLACE(thumbnail_path, './uploads', '/uploads')
        WHERE thumbnail_path LIKE './uploads%'
    """)


def downgrade():
    # Best-effort rollback: restore /app/uploads -> /app/app/uploads when that pattern existed
    op.execute("""
        UPDATE chat_attachment
        SET file_path = REPLACE(file_path, '/app/uploads', '/app/app/uploads')
        WHERE file_path LIKE '%/app/uploads%'
    """)
    op.execute("""
        UPDATE chat_attachment
        SET thumbnail_path = REPLACE(thumbnail_path, '/app/uploads', '/app/app/uploads')
        WHERE thumbnail_path LIKE '%/app/uploads%'
    """)
