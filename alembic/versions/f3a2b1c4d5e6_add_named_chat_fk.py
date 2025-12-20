"""add named chat FK constraints

Revision ID: f3a2b1c4d5e6
Revises: d7e8f9a0b1c2
Create Date: 2025-12-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3a2b1c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'd7e8f9a0b1c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add named foreign key constraints if missing (Postgres only)."""
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        # Add named FK for last_message_id if it doesn't already exist and the column exists
        op.execute("""
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_attribute a JOIN pg_class t ON a.attrelid = t.oid
    WHERE t.relname = 'chat_conversation' AND a.attname = 'last_message_id' AND NOT a.attisdropped
  ) THEN
    IF NOT EXISTS (
      SELECT 1 FROM pg_constraint c
      JOIN pg_class t ON c.conrelid = t.oid
      WHERE t.relname = 'chat_conversation' AND c.conname = 'fk_chat_conversation_last_message'
    ) THEN
      ALTER TABLE chat_conversation
        ADD CONSTRAINT fk_chat_conversation_last_message
        FOREIGN KEY (last_message_id) REFERENCES chat_message(id) DEFERRABLE INITIALLY DEFERRED;
    END IF;
  END IF;
END$$;
""")

        # Add named FK for last_read_message_id if the column exists and the constraint doesn't exist
        op.execute("""
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_attribute a JOIN pg_class t ON a.attrelid = t.oid
    WHERE t.relname = 'chat_conversation' AND a.attname = 'last_read_message_id' AND NOT a.attisdropped
  ) THEN
    IF NOT EXISTS (
      SELECT 1 FROM pg_constraint c
      JOIN pg_class t ON c.conrelid = t.oid
      WHERE t.relname = 'chat_conversation' AND c.conname = 'fk_chat_conversation_last_read'
    ) THEN
      ALTER TABLE chat_conversation
        ADD CONSTRAINT fk_chat_conversation_last_read
        FOREIGN KEY (last_read_message_id) REFERENCES chat_message(id) DEFERRABLE INITIALLY DEFERRED;
    END IF;
  END IF;
END$$;
""")
    else:
        # On non-Postgres backends, skip (tests will run against Postgres in CI)
        pass


def downgrade() -> None:
    """Drop the named FK constraints if present (Postgres only)."""
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute("ALTER TABLE chat_conversation DROP CONSTRAINT IF EXISTS fk_chat_conversation_last_message;")
        op.execute("ALTER TABLE chat_conversation DROP CONSTRAINT IF EXISTS fk_chat_conversation_last_read;")
