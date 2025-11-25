import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import Config
from app import create_app, db
from app.models import User, Equipment


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
        user = User(username='u', email='u@example.com', role='user', department='销售部')
        user.set_password('secret')
        eq = Equipment(name='回收笔记本', serial_number='SN123', status='available', department='信息部')
        db.session.add_all([admin, user, eq])
        db.session.commit()

        client = app.test_client()
        client.post('/auth/login', data={'username': 'u', 'password': 'secret'}, follow_redirects=True)
        r = client.get('/create_equipment_application')
        print('GET create_equipment_application:', r.status_code)
        r2 = client.post('/create_equipment_application', data={'equipment_id': eq.id, 'reason': '业务需求'}, follow_redirects=True)
        print('POST create_equipment_application:', r2.status_code)


if __name__ == '__main__':
    main()