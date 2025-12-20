"""create chat tables

Revision ID: e8f7d6c5b4a3
Revises: f3a2b1c4d5e6
Create Date: 2025-12-20 01:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8f7d6c5b4a3'
down_revision: Union[str, Sequence[str], None] = 'f3a2b1c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    # Create tables (without circular named FKs) if they don't already exist
    inspector = sa.inspect(op.get_bind())

    if 'chat_conversation' not in inspector.get_table_names():
        op.create_table(
            'chat_conversation',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('conversation_type', sa.String(length=20), nullable=False, server_default='direct'),
            sa.Column('name', sa.String(length=200)),
            sa.Column('avatar_url', sa.String(length=512)),
            sa.Column('description', sa.Text()),
            sa.Column('creator_id', sa.Integer(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.text('true')),
            sa.Column('created_date', sa.DateTime(), nullable=True),
            sa.Column('updated_date', sa.DateTime(), nullable=True),
            sa.Column('last_message_id', sa.Integer(), nullable=True),
            sa.Column('last_message_time', sa.DateTime(), nullable=True),
        )

    if 'chat_message' not in inspector.get_table_names():
        op.create_table(
            'chat_message',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('conversation_id', sa.Integer(), nullable=False),
            sa.Column('sender_id', sa.Integer(), nullable=False),
            sa.Column('message_type', sa.String(length=20), nullable=False, server_default='text'),
            sa.Column('content', sa.Text()),
            sa.Column('is_recalled', sa.Boolean(), nullable=True, server_default=sa.text('false')),
            sa.Column('is_deleted', sa.Boolean(), nullable=True, server_default=sa.text('false')),
            sa.Column('created_date', sa.DateTime(), nullable=True),
            sa.Column('reply_to_message_id', sa.Integer(), nullable=True),
        )

    if 'chat_participant' not in inspector.get_table_names():
        op.create_table(
            'chat_participant',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('conversation_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('joined_date', sa.DateTime(), nullable=True),
            sa.Column('last_read_message_id', sa.Integer(), nullable=True),
            sa.Column('unread_count', sa.Integer(), nullable=True, server_default='0'),
            sa.Column('is_pinned', sa.Boolean(), nullable=True, server_default=sa.text('false')),
            sa.Column('is_muted', sa.Boolean(), nullable=True, server_default=sa.text('false')),
            sa.UniqueConstraint('conversation_id', 'user_id', name='uq_chat_participant_conversation_user')
        )

    if 'chat_attachment' not in inspector.get_table_names():
        op.create_table(
            'chat_attachment',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('message_id', sa.Integer(), nullable=False),
            sa.Column('filename', sa.String(length=255), nullable=False),
            sa.Column('stored_filename', sa.String(length=255), nullable=False),
            sa.Column('file_path', sa.String(length=512), nullable=False),
            sa.Column('file_size', sa.Integer(), nullable=False),
            sa.Column('file_type', sa.String(length=128)),
            sa.Column('thumbnail_path', sa.String(length=512)),
            sa.Column('upload_user_id', sa.Integer(), nullable=False),
            sa.Column('created_date', sa.DateTime(), nullable=True),
        )

    if 'chat_permission' not in inspector.get_table_names():
        op.create_table(
            'chat_permission',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('can_send_message', sa.Boolean(), nullable=True, server_default=sa.text('true')),
            sa.Column('can_send_file', sa.Boolean(), nullable=True, server_default=sa.text('true')),
            sa.Column('can_create_group', sa.Boolean(), nullable=True, server_default=sa.text('true')),
            sa.Column('muted_until', sa.DateTime(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('operated_by_id', sa.Integer(), nullable=True),
            sa.Column('operated_date', sa.DateTime(), nullable=True),
        )

    # Add foreign keys with explicit names (after tables created to avoid circular issues)
    inspector = sa.inspect(op.get_bind())
    bind = op.get_bind()

    def fk_exists(constraint_name, table_name):
        if bind.dialect.name != 'postgresql':
            return False
        res = bind.execute(sa.text("""
            SELECT 1 FROM pg_constraint c
            JOIN pg_class t ON c.conrelid = t.oid
            WHERE t.relname = :table AND c.conname = :constraint
        """), {'table': table_name, 'constraint': constraint_name}).first()
        return res is not None

    if 'chat_message' in inspector.get_table_names() and 'chat_conversation' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('chat_message')]
        if 'conversation_id' in cols and not fk_exists('fk_chat_message_conversation', 'chat_message'):
            op.create_foreign_key('fk_chat_message_conversation', 'chat_message', 'chat_conversation', ['conversation_id'], ['id'])

    if 'chat_message' in inspector.get_table_names() and 'app_user' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('chat_message')]
        if 'sender_id' in cols and not fk_exists('fk_chat_message_sender', 'chat_message'):
            op.create_foreign_key('fk_chat_message_sender', 'chat_message', 'app_user', ['sender_id'], ['id'])

    if 'chat_message' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('chat_message')]
        if 'reply_to_message_id' in cols and not fk_exists('fk_chat_message_reply_to', 'chat_message'):
            op.create_foreign_key('fk_chat_message_reply_to', 'chat_message', 'chat_message', ['reply_to_message_id'], ['id'])

    if 'chat_participant' in inspector.get_table_names() and 'chat_conversation' in inspector.get_table_names() and not fk_exists('fk_chat_participant_conversation', 'chat_participant'):
        op.create_foreign_key('fk_chat_participant_conversation', 'chat_participant', 'chat_conversation', ['conversation_id'], ['id'])

    if 'chat_participant' in inspector.get_table_names() and 'app_user' in inspector.get_table_names() and not fk_exists('fk_chat_participant_user', 'chat_participant'):
        op.create_foreign_key('fk_chat_participant_user', 'chat_participant', 'app_user', ['user_id'], ['id'])

    if 'chat_participant' in inspector.get_table_names() and 'chat_message' in inspector.get_table_names() and not fk_exists('fk_chat_participant_last_read', 'chat_participant'):
        op.create_foreign_key('fk_chat_participant_last_read', 'chat_participant', 'chat_message', ['last_read_message_id'], ['id'])

    if 'chat_attachment' in inspector.get_table_names() and 'chat_message' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('chat_attachment')]
        if 'message_id' in cols and not fk_exists('fk_chat_attachment_message', 'chat_attachment'):
            op.create_foreign_key('fk_chat_attachment_message', 'chat_attachment', 'chat_message', ['message_id'], ['id'])

    if 'chat_attachment' in inspector.get_table_names() and 'app_user' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('chat_attachment')]
        if 'upload_user_id' in cols and not fk_exists('fk_chat_attachment_uploader', 'chat_attachment'):
            op.create_foreign_key('fk_chat_attachment_uploader', 'chat_attachment', 'app_user', ['upload_user_id'], ['id'])

    # Conversation creator FK
    if 'chat_conversation' in inspector.get_table_names() and 'app_user' in inspector.get_table_names() and not fk_exists('fk_chat_conversation_creator', 'chat_conversation'):
        op.create_foreign_key('fk_chat_conversation_creator', 'chat_conversation', 'app_user', ['creator_id'], ['id'])

    # Chat permission FKs
    if 'chat_permission' in inspector.get_table_names() and 'app_user' in inspector.get_table_names() and not fk_exists('fk_chat_permission_user', 'chat_permission'):
        op.create_foreign_key('fk_chat_permission_user', 'chat_permission', 'app_user', ['user_id'], ['id'])
    if 'chat_permission' in inspector.get_table_names() and 'app_user' in inspector.get_table_names() and not fk_exists('fk_chat_permission_operated_by', 'chat_permission'):
        op.create_foreign_key('fk_chat_permission_operated_by', 'chat_permission', 'app_user', ['operated_by_id'], ['id'])

    # Finally, add named FK from conversation.last_message_id -> chat_message.id
    if 'chat_conversation' in inspector.get_table_names() and 'chat_message' in inspector.get_table_names() and not fk_exists('fk_chat_conversation_last_message', 'chat_conversation'):
        op.create_foreign_key('fk_chat_conversation_last_message', 'chat_conversation', 'chat_message', ['last_message_id'], ['id'])


def downgrade() -> None:
    # Drop FKs then tables
    op.drop_constraint('fk_chat_conversation_last_message', 'chat_conversation', type_='foreignkey')

    op.drop_constraint('fk_chat_attachment_message', 'chat_attachment', type_='foreignkey')
    op.drop_constraint('fk_chat_attachment_uploader', 'chat_attachment', type_='foreignkey')

    op.drop_constraint('fk_chat_conversation_creator', 'chat_conversation', type_='foreignkey')

    op.drop_constraint('fk_chat_permission_user', 'chat_permission', type_='foreignkey')
    op.drop_constraint('fk_chat_permission_operated_by', 'chat_permission', type_='foreignkey')

    op.drop_constraint('fk_chat_participant_conversation', 'chat_participant', type_='foreignkey')
    op.drop_constraint('fk_chat_participant_user', 'chat_participant', type_='foreignkey')
    op.drop_constraint('fk_chat_participant_last_read', 'chat_participant', type_='foreignkey')

    op.drop_constraint('fk_chat_message_conversation', 'chat_message', type_='foreignkey')
    op.drop_constraint('fk_chat_message_sender', 'chat_message', type_='foreignkey')
    op.drop_constraint('fk_chat_message_reply_to', 'chat_message', type_='foreignkey')

    op.drop_table('chat_permission')
    op.drop_table('chat_attachment')
    op.drop_table('chat_participant')
    op.drop_table('chat_message')
    op.drop_table('chat_conversation')
