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

        r = client.post('/admin/workflow_nodes/add', data={
            'name': '部门领导审批',
            'order_type': 'repair',
            'role_required': 'department_head',
            'sequence': '1'
        })
        print('add node:', r.status_code, r.get_json())

        r2 = client.get('/workflow_nodes')
        print('list nodes:', r2.status_code)


if __name__ == '__main__':
    main()