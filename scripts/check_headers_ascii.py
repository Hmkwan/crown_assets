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
        db.session.add(admin)
        db.session.commit()

        client = app.test_client()
        client.post('/auth/login', data={'username': 'admin', 'password': 'secret'}, follow_redirects=True)

        r = client.get('/admin/users/export')
        cd = r.headers.get('Content-Disposition', '')
        print('users header ascii:', all(ord(ch) < 128 for ch in cd), cd)

        r2 = client.get('/reports/export?type=equipment')
        cd2 = r2.headers.get('Content-Disposition', '')
        print('equipment header ascii:', all(ord(ch) < 128 for ch in cd2), cd2)


if __name__ == '__main__':
    main()