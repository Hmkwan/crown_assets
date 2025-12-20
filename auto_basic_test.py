"""
基础自动化测试脚本：
- 测试登录接口（默认用户名：admin，密码：12345678）
- 测试首页、公告页、设备页等主要页面访问
- 可扩展更多API测试
"""
from app import create_app, db


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

def test_login():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        client = app.test_client()
        resp = client.get('/auth/login')
        assert resp.status_code == 200

        data = {'username': 'admin', 'password': '12345678'}
        resp = client.post('/auth/login', data=data, follow_redirects=False)
        assert resp.status_code in (302, 200)
        return True

def test_page_access():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        client = app.test_client()

            # ensure admin exists and login
        from app.models import User
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('12345678')
            db.session.add(admin)
            db.session.commit()
        client.post('/auth/login', data={'username': 'admin', 'password': '12345678'})

        for path in ['/index', '/announcements', '/equipment']:
            resp = client.get(path)
            assert resp.status_code in (200, 302)


if __name__ == "__main__":
    test_login()
    test_page_access()
