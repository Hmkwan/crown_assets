import pytest
from app import create_app, db


def test_named_chat_fk_constraints_exist():
    """Ensure Alembic migration created named chat FK constraints on Postgres."""
    app = create_app()
    with app.app_context():
        if db.engine.dialect.name != 'postgresql':
            pytest.skip('Postgres required for this migration validation')

        # Verify the last_message FK exists
        rows = db.session.execute(
            """
SELECT c.conname
FROM pg_constraint c
JOIN pg_class t ON c.conrelid = t.oid
WHERE t.relname = 'chat_conversation'
  AND c.conname = 'fk_chat_conversation_last_message'
"""
        ).fetchall()
        names = {r[0] for r in rows}
        assert 'fk_chat_conversation_last_message' in names, 'fk_chat_conversation_last_message missing'

        # If last_read_message_id column exists, verify its FK constraint too; otherwise skip that check
        col = db.session.execute("SELECT 1 FROM information_schema.columns WHERE table_name='chat_conversation' AND column_name='last_read_message_id'").fetchone()
        if col:
            rows2 = db.session.execute(
                """
SELECT c.conname
FROM pg_constraint c
JOIN pg_class t ON c.conrelid = t.oid
WHERE t.relname = 'chat_conversation'
  AND c.conname = 'fk_chat_conversation_last_read'
"""
            ).fetchall()
            names2 = {r[0] for r in rows2}
            assert 'fk_chat_conversation_last_read' in names2, 'fk_chat_conversation_last_read missing'
        else:
            pytest.skip('last_read_message_id column not present; skipping last_read FK check')

        # Also verify that chat_participant has a named FK for last_read_message_id if the column exists there
        part_col = db.session.execute("SELECT 1 FROM information_schema.columns WHERE table_name='chat_participant' AND column_name='last_read_message_id'").fetchone()
        if part_col:
            rows3 = db.session.execute(
                """
SELECT c.conname
FROM pg_constraint c
JOIN pg_class t ON c.conrelid = t.oid
WHERE t.relname = 'chat_participant'
  AND c.conname = 'fk_chat_conversation_last_read'
"""
            ).fetchall()
            names3 = {r[0] for r in rows3}
            assert 'fk_chat_conversation_last_read' in names3, 'fk_chat_conversation_last_read missing on chat_participant'
        else:
            pytest.skip('chat_participant.last_read_message_id not present; skipping participant last_read FK check')


def test_patch_columns_present():
    """Ensure patch migration added commonly-missing columns (Postgres only)."""
    app = create_app()
    with app.app_context():
        if db.engine.dialect.name != 'postgresql':
            pytest.skip('Postgres required for this migration validation')

        from sqlalchemy import text

        def has_column(table, col):
            row = db.session.execute(
                text("SELECT 1 FROM information_schema.columns WHERE table_name=:table AND column_name=:col"),
                {'table': table, 'col': col}
            ).fetchone()
            return bool(row)

        assert has_column('chat_attachment', 'upload_user_id'), 'chat_attachment.upload_user_id missing'
        assert has_column('workflow_node', 'role_required_name'), 'workflow_node.role_required_name missing'
        assert has_column('approval_workflow', 'required_approvals'), 'approval_workflow.required_approvals missing'
