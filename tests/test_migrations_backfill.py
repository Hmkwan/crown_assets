import pytest
import uuid
from app import create_app, db
from app.models import User, ChatMessage, ChatAttachment


def test_backfill_chat_attachment_upload_user():
    # Create an app context so db.engine is available and tests run deterministically
    app = create_app()
    with app.app_context():
        # Only run on Postgres (migration semantics matter there)
        if db.engine.dialect.name != 'postgresql':
            pytest.skip('Postgres-only test')

        # Prepare data: create a user, a conversation, a message and attachments
        u = User(username=f'bf_user_{uuid.uuid4().hex}', password_hash='x')
        db.session.add(u)
        db.session.commit()

        # Create minimal conversation required by ChatMessage FK (use existing conversation or create one)
        from app.chat_models import ChatConversation
        conv = ChatConversation(conversation_type='direct', creator_id=u.id, name='bf')
        db.session.add(conv)
        db.session.commit()

        msg = ChatMessage(conversation_id=conv.id, sender_id=u.id, content='hi')
        db.session.add(msg)
        db.session.commit()

        # Attachment linked to message (should get upload_user_id from message.sender_id)
        a1 = ChatAttachment(message_id=msg.id, filename='f1.txt', stored_filename='f1.txt', file_path='/tmp/f1', file_size=1, file_type='text/plain', upload_user_id=None)
        # Attachment without message (should be set to fallback user id)
        a2 = ChatAttachment(message_id=None, filename='f2.txt', stored_filename='f2.txt', file_path='/tmp/f2', file_size=2, file_type='text/plain', upload_user_id=None)

        db.session.add_all([a1, a2])
        db.session.commit()

        # Run backfill SQL same as migration logic
        from sqlalchemy import text
        with db.engine.begin() as conn:
            conn.execute(text(
                """
                UPDATE chat_attachment
                SET upload_user_id = cm.sender_id
                FROM chat_message cm
                WHERE chat_attachment.upload_user_id IS NULL
                  AND chat_attachment.message_id = cm.id
                """
            ))
            res = conn.execute(text("SELECT id FROM app_user ORDER BY id LIMIT 1")).fetchone()
            if res and res[0]:
                fallback = int(res[0])
                conn.execute(text("UPDATE chat_attachment SET upload_user_id = :uid WHERE upload_user_id IS NULL"), {'uid': fallback})

        db.session.expire_all()

        # Assertions
        a1_db = ChatAttachment.query.get(a1.id)
        a2_db = ChatAttachment.query.get(a2.id)

        assert a1_db.upload_user_id == msg.sender_id
        assert a2_db.upload_user_id is not None
