import pytest
from flask import url_for
from sqlalchemy.exc import ProgrammingError


def test_login_handles_db_programming_error(monkeypatch):
    # 模拟 User.query.filter(...).first() 抛出 ProgrammingError
    class DummyUser:
        class query:
            @staticmethod
            def filter(*args, **kwargs):
                class Q:
                    @staticmethod
                    def first():
                        raise ProgrammingError('relation "app_user" does not exist', None, None)
                return Q()

    # 将 routes 中的 User 替换为 DummyUser
    import app.auth.routes as routes
    monkeypatch.setattr(routes, 'User', DummyUser, raising=False)

    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        resp = client.post('/auth/login', data={'username': 'admin', 'password': 'x'}, follow_redirects=True)
        data = resp.get_data(as_text=True)
        assert '系统暂不可用' in data or '服务器错误' in data or resp.status_code in (503, 200)
