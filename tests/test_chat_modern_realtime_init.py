import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        user = User(username='admin', email='admin@system.local', role='admin')
        user.set_password('admin12')
        db.session.add(user)
        db.session.commit()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()


def login_admin(client):
    client.post('/auth/login', data={'username': 'admin', 'password': 'admin12'}, follow_redirects=True)


def test_chat_modern_includes_socket_and_realtime(client, app):
    login_admin(client)
    rv = client.get('/chat')
    assert rv.status_code == 200
    html = rv.get_data(as_text=True)
    assert 'socket.io' in html.lower() or 'cdn.socket.io' in html.lower()
    assert 'realtime-notifications.js' in html
