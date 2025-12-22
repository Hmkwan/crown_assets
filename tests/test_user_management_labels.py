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
        # create an admin user
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('adminpw')
        db.session.add(admin)
        db.session.commit()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()


def login_admin(client):
    client.post('/auth/login', data={'username': 'admin', 'password': 'adminpw'}, follow_redirects=True)


def test_user_management_contains_workflow_label_and_help_link(client, app):
    # login as admin
    login_admin(client)

    # get user management page
    rv = client.get('/admin/users')
    assert rv.status_code == 200
    html = rv.get_data(as_text=True)

    # check new consistent label for workflow roles button and table header
    assert '审批流角色' in html

    # check help link to approval role assign page exists
    assert '/admin/approval_roles/assign' in html
