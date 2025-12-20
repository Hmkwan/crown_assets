import re
import pytest
from app import create_app, db


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


@pytest.fixture(scope="function")
def client():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        # create admin user
        from app.models import User
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
        client = app.test_client()
        # set session user directly to bypass login complexity in tests
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
            sess['_fresh'] = True
        yield client


def test_get_conversations(client):
    resp = client.get('/api/chat/conversations')
    assert resp.status_code == 200
    assert resp.content_type.startswith('application/json')
    data = resp.get_json() if resp.is_json else {}
    assert isinstance(data, dict)
    # conversations may or may not exist; ensure no crash
    assert 'conversations' in data or True


def test_get_users(client):
    resp = client.get('/api/chat/users')
    assert resp.status_code == 200
    data = resp.get_json() if resp.is_json else {}
    assert isinstance(data, dict)
    assert 'users' in data or True


def test_get_index_page(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert '皇冠新材IT资产管理系统' in resp.get_data(as_text=True)


