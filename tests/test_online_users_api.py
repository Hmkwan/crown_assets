import pytest
from app.models import User


import pytest
from app import create_app, db as _db


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as c:
        with app.app_context():
            _db.create_all()
        yield c
        with app.app_context():
            _db.session.remove()
            _db.drop_all()


def test_get_online_users_returns_user_objects(client, monkeypatch):
    import uuid

    # 创建两个用户（需要应用上下文以访问 db）
    with client.application.app_context():
        # 使用随机后缀避免与其他测试用例产生 UNIQUE 冲突
        suffix1 = uuid.uuid4().hex[:8]
        suffix2 = uuid.uuid4().hex[:8]
        u1 = User(username=f'alice_{suffix1}', email=f'alice_{suffix1}@example.com')
        u2 = User(username=f'bob_{suffix2}', email=f'bob_{suffix2}@example.com')
        _db.session.add_all([u1, u2])
        _db.session.commit()
        # 将 id 抽离为原始值，避免会话关闭后访问导致 DetachedInstanceError
        u1_id = u1.id
        u2_id = u2.id

    # Monkeypatch redis client used by the blueprint
    import app.online_users as online_mod

    class FakeRedis:
        def smembers(self, key):
            # 返回 bytes 风格的数据, 模拟真实 redis
            return {str(u1_id).encode('utf-8'), str(u2_id).encode('utf-8')}

    monkeypatch.setattr(online_mod, 'redis_client', FakeRedis())

    resp = client.get('/api/online_users')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'online_users' in data
    users = data['online_users']
    assert isinstance(users, list)
    ids = {u['id'] for u in users}
    assert u1_id in ids and u2_id in ids
    # 检查包含用户名前缀（使用随机后缀以防冲突）
    names = {u['username'] for u in users}
    assert any(n.startswith('alice_') for n in names) and any(n.startswith('bob_') for n in names)
