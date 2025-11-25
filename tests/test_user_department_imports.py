import io
from config import Config
from app import create_app, db
from app.models import User, Department


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def login_client(client, username, password):
    return client.post('/auth/login', data={'username': username, 'password': password}, follow_redirects=True)


def test_import_and_export_users():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('secret')
        db.session.add(admin)
        db.session.commit()

        client = app.test_client()
        login_client(client, 'admin', 'secret')

        csv_data = '用户名,邮箱,角色,所属部门\nuser1,user1@example.com,user,IT部\n'
        data = {'file': (io.BytesIO(csv_data.encode('utf-8')), 'users.csv')}
        resp = client.post('/admin/users/import', data=data, content_type='multipart/form-data')
        assert resp.status_code == 200
        j = resp.get_json()
        assert j and j.get('success') is True

        u = User.query.filter_by(username='user1').first()
        assert u is not None
        assert u.email == 'user1@example.com'

        # export
        resp2 = client.get('/admin/users/export')
        assert resp2.status_code == 200
        text = resp2.get_data(as_text=True)
        assert '用户名' in text and 'user1' in text


def test_import_and_export_departments():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        admin = User(username='admin', email='admin2@example.com', role='admin')
        admin.set_password('secret')
        db.session.add(admin)
        db.session.commit()

        client = app.test_client()
        login_client(client, 'admin', 'secret')

        csv_data = '部门名称,部门代码,成本中心,位置,描述\n测试部,TEST01,CC01,上海,测试部门\n'
        data = {'file': (io.BytesIO(csv_data.encode('utf-8')), 'depts.csv')}
        resp = client.post('/admin/departments/import', data=data, content_type='multipart/form-data')
        assert resp.status_code == 200
        j = resp.get_json()
        assert j and j.get('success') is True

        d = Department.query.filter_by(name='测试部').first()
        assert d is not None
        assert d.code == 'TEST01'

        # export
        resp2 = client.get('/admin/departments/export')
        assert resp2.status_code == 200
        text = resp2.get_data(as_text=True)
        assert '部门名称' in text and '测试部' in text
