import pytest
from app import create_app, db
from app.models import User
from app.chat_models import ChatConversation, ChatMessage, ChatParticipant, ChatAttachment

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        # create a user
        user = User(username='testuser', email='test@local')
        user.set_password('pass')
        db.session.add(user)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()


def test_create_conversation_and_message(app):
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        # create conversation
        conv = ChatConversation(conversation_type='direct', name='T1', creator_id=user.id)
        db.session.add(conv)
        db.session.flush()

        msg = ChatMessage(conversation_id=conv.id, sender_id=user.id, content='hello', message_type='text')
        db.session.add(msg)
        db.session.flush()

        # associate last_message
        conv.last_message_id = msg.id
        db.session.commit()

        # create participant
        p = ChatParticipant(conversation_id=conv.id, user_id=user.id)
        db.session.add(p)
        db.session.commit()

        # create attachment
        att = ChatAttachment(message_id=msg.id, filename='f.txt', stored_filename='f.txt', file_path='/tmp/f.txt', file_size=10, file_type='text/plain', upload_user_id=user.id)
        db.session.add(att)
        db.session.commit()

        # assertions
        assert ChatConversation.query.count() == 1
        assert ChatMessage.query.count() == 1
        assert ChatParticipant.query.count() == 1
        assert ChatAttachment.query.count() == 1
        assert conv.last_message.id == msg.id
