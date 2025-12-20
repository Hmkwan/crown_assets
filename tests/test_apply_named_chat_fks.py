import pytest
from app import create_app, db


def test_apply_named_chat_fks_adds_missing_constraint():
    """Postgres-only test: drop named FK if present, run script, ensure constraint exists."""
    app = create_app()
    with app.app_context():
        if db.engine.dialect.name != 'postgresql':
            pytest.skip('Postgres required for this test')

        # Drop the named constraint if it exists to simulate a broken DB
        db.session.execute("ALTER TABLE chat_conversation DROP CONSTRAINT IF EXISTS fk_chat_conversation_last_message;")
        db.session.commit()

        # Sanity check: ensure it's dropped
        row = db.session.execute(
            "SELECT 1 FROM pg_constraint c JOIN pg_class t ON c.conrelid = t.oid WHERE t.relname='chat_conversation' AND c.conname='fk_chat_conversation_last_message'"
        ).fetchone()
        assert row is None

        # Run the remediation script
        from scripts.apply_named_chat_fks import main
        main()

        # Verify the named constraint now exists
        row2 = db.session.execute(
            "SELECT 1 FROM pg_constraint c JOIN pg_class t ON c.conrelid = t.oid WHERE t.relname='chat_conversation' AND c.conname='fk_chat_conversation_last_message'"
        ).fetchone()
        assert row2 is not None

        # Running the script again should be a no-op (idempotent)
        main()
        # still exists
        row3 = db.session.execute(
            "SELECT 1 FROM pg_constraint c JOIN pg_class t ON c.conrelid = t.oid WHERE t.relname='chat_conversation' AND c.conname='fk_chat_conversation_last_message'"
        ).fetchone()
        assert row3 is not None
