import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import Config
from app import create_app, db
from app.models import User


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def main():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('secret')
        tech = User(username='tech', email='tech@example.com', role='technician', department='IT')
        tech.set_password('secret')
        db.session.add(admin)
        db.session.add(tech)
        db.session.commit()

        client = app.test_client()

        client.post('/auth/login', data={'username': 'tech', 'password': 'secret'}, follow_redirects=True)
        r1 = client.get('/reports/export?type=equipment')
        print('tech equipment export:', r1.status_code)

        client.post('/auth/logout', follow_redirects=True)
        client.post('/auth/login', data={'username': 'admin', 'password': 'secret'}, follow_redirects=True)
        r2 = client.get('/admin/users/export')
        print('admin users export:', r2.status_code)


if __name__ == '__main__':
    main()