"""add named chat_participant last_read FK

Revision ID: add_named_chat_participant_last_read
Revises: f3a2b1c4d5e6
Create Date: 2026-01-06 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'add_named_chat_participant_last_read'
down_revision = 'f3a2b1c4d5e6'
branch_labels = None
dependencies = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        # Add named FK on chat_participant.last_read_message_id if column exists and constraint missing
        op.execute("""
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_attribute a JOIN pg_class t ON a.attrelid = t.oid
    WHERE t.relname = 'chat_participant' AND a.attname = 'last_read_message_id' AND NOT a.attisdropped
  ) THEN
    IF NOT EXISTS (
      SELECT 1 FROM pg_constraint c
      JOIN pg_class t ON c.conrelid = t.oid
      WHERE t.relname = 'chat_participant' AND c.conname = 'fk_chat_conversation_last_read'
    ) THEN
      ALTER TABLE chat_participant
        ADD CONSTRAINT fk_chat_conversation_last_read
        FOREIGN KEY (last_read_message_id) REFERENCES chat_message(id) DEFERRABLE INITIALLY DEFERRED;
    END IF;
  END IF;
END$$;
""")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute("ALTER TABLE chat_participant DROP CONSTRAINT IF EXISTS fk_chat_conversation_last_read;")
