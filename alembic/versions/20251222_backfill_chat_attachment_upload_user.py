"""Backfill upload_user_id for chat_attachment

Revision ID: 20251222_backfill_chat_attachment_upload_user
Revises: 20251222_patch_chat_attachment_and_workflow_columns
Create Date: 2025-12-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20251222_backfill_chat_attachment_upload_user'
down_revision = '20251222_patch_chat_attachment_and_workflow_columns'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = inspect(bind)

    try:
        cols = [c['name'] for c in insp.get_columns('chat_attachment')]
    except Exception:
        print('Could not inspect chat_attachment; skipping backfill')
        return

    if 'upload_user_id' not in cols:
        print('upload_user_id column not present; skipping backfill')
        return

    try:
        bind.execute(
            """
            UPDATE chat_attachment
            SET upload_user_id = cm.sender_id
            FROM chat_message cm
            WHERE chat_attachment.upload_user_id IS NULL
              AND chat_attachment.message_id = cm.id
            """
        )
        print('Backfill step 1: set upload_user_id from message sender where possible')
    except Exception as e:
        print('Backfill step 1 failed (non-fatal):', e)

    try:
        res = bind.execute(sa.text("SELECT id FROM app_user ORDER BY id LIMIT 1")).fetchone()
        if res and res[0]:
            fallback = int(res[0])
            bind.execute(sa.text("UPDATE chat_attachment SET upload_user_id = :uid WHERE upload_user_id IS NULL"), {'uid': fallback})
            print(f'Backfill step 2: set remaining upload_user_id to fallback user id {fallback}')
        else:
            print('Backfill step 2: no users found; leaving NULLs as-is')
    except Exception as e:
        print('Backfill step 2 failed (non-fatal):', e)


def downgrade():
    print('Downgrade: no schema changes to revert for backfill')
