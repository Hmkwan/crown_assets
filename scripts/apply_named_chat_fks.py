"""Safely add named FK constraints to chat_conversation if missing.

This module exposes `ensure_named_chat_fks(session)` for programmatic use and a
`main()` entrypoint for CLI use. It's idempotent and safe to run repeatedly.
"""
from app import create_app, db
import logging

logger = logging.getLogger(__name__)


def ensure_named_chat_fks(session):
    """Ensure named FK constraints exist on `chat_conversation`.

    Returns a list of action messages performed (or observed).
    Raises: will re-raise any underlying DB exception after rolling back the session.
    """
    actions = []
    query_template = "SELECT 1 FROM pg_constraint c JOIN pg_class t ON c.conrelid = t.oid WHERE t.relname='chat_conversation' AND c.conname='{}'"
    try:
        if not session.execute(query_template.format('fk_chat_conversation_last_message')).fetchone():
            session.execute(
                "ALTER TABLE chat_conversation ADD CONSTRAINT fk_chat_conversation_last_message FOREIGN KEY (last_message_id) REFERENCES chat_message(id) DEFERRABLE INITIALLY DEFERRED;"
            )
            actions.append('added fk_chat_conversation_last_message')
        else:
            actions.append('fk_chat_conversation_last_message already exists')

        # Only attempt to add the last_read FK if the column exists
        col_exists = session.execute(
            "SELECT 1 FROM information_schema.columns WHERE table_name='chat_conversation' AND column_name='last_read_message_id'"
        ).fetchone()
        if col_exists:
            if not session.execute(query_template.format('fk_chat_conversation_last_read')).fetchone():
                session.execute(
                    "ALTER TABLE chat_conversation ADD CONSTRAINT fk_chat_conversation_last_read FOREIGN KEY (last_read_message_id) REFERENCES chat_message(id) DEFERRABLE INITIALLY DEFERRED;"
                )
                actions.append('added fk_chat_conversation_last_read')
            else:
                actions.append('fk_chat_conversation_last_read already exists')
        else:
            actions.append('column last_read_message_id not present; skipping')

        return actions
    except Exception:
        session.rollback()
        logger.exception('Failed to ensure named chat FKs')
        raise


def main():
    app = create_app()
    with app.app_context():
        actions = ensure_named_chat_fks(db.session)
        for a in actions:
            print(a)
        db.session.commit()


if __name__ == '__main__':
    main()
