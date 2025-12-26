# -*- coding: utf-8 -*-
import pytest
from app.models import User, Announcement, UserActivityLog
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


def test_announcements_detail_logs_activity(client):
    # 使用传入的 client fixture 创建用户和公告
    with client.application.app_context():
        u = User(username='actuser', email='actuser@example.com')
        u.set_password('pass')
        ann = Announcement(title='Test', content='x')
        # 将公告的 creator 设置为创建者，满足 NOT NULL 约束
        ann.creator = u
        _db.session.add_all([u, ann])
        _db.session.commit()
        u_id = u.id
        ann_id = ann.id

    # 登录（测试模式下 CSRF 一般被禁用）
    client.post('/auth/login', data={'username': 'actuser', 'password': 'pass'})
    resp = client.get(f'/announcements/{ann_id}')
    assert resp.status_code == 200

    # 在应用上下文中检查 UserActivityLog
    with client.application.app_context():
        logs = UserActivityLog.query.filter_by(user_id=u_id).all()
        assert any('查看公告详情' in (l.action or '') for l in logs)
