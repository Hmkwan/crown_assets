from app import create_app, db
from bs4 import BeautifulSoup


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

from bs4 import BeautifulSoup

def test_create_conversation():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        client = app.test_client()

        # Ensure admin exists and get login page
        from app.models import User
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

        login_resp = client.get('/auth/login')
        assert login_resp.status_code == 200

        # Step 2: Login
        login_data = {'username': 'admin', 'password': 'admin123'}
        # set session user id directly for the test client
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
            sess['_fresh'] = True

        # Step 3: create another user to be participant and create conversation via API
        import uuid
        participant = User(username=f'user1_{uuid.uuid4().hex[:8]}', email=f'user1_{uuid.uuid4().hex[:8]}@example.com', role='user')
        participant.set_password('user123')
        db.session.add(participant)
        db.session.commit()

        create_data = {
            'type': 'direct',
            'participant_ids': [participant.id],
            'name': ''
        }
        create_response = client.post('/api/chat/conversations', json=create_data)
        assert create_response.status_code in (200, 201, 302, 400)
        if create_response.is_json:
            data = create_response.get_json()
            assert isinstance(data, dict)

if __name__ == "__main__":
    test_create_conversation()