import pytest
from datetime import datetime, timedelta
import pytz

from app import create_app, db, login
from app.models import User, Announcement


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def test_announcement_list_shows_localized_time_and_creator():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        # 创建用户
        user = User(username='tester', email='t@example.com')
        db.session.add(user)
        db.session.commit()

        # 创建公告（publish_time 存为 UTC naive）
        publish_utc = datetime.utcnow().replace(microsecond=0)
        ann = Announcement(
            title='测试公告',
            content='这是测试',
            is_published=True,
            publish_time=publish_utc,
            creator_id=user.id
        )
        db.session.add(ann)
        db.session.commit()

        client = app.test_client()

        # 模拟登录：设置 Flask-Login session
        with client.session_transaction() as sess:
            sess[login.session_key] = str(user.id)

        resp = client.get('/announcements')
        assert resp.status_code == 200
        data = resp.get_data(as_text=True)

        # 检查作者名显示
        assert 'tester' in data

        # 检查时间是否已本地化到 Asia/Shanghai 格式
        tz = pytz.timezone('Asia/Shanghai')
        expected = publish_utc.replace(tzinfo=pytz.UTC).astimezone(tz).strftime('%Y-%m-%d %H:%M')
        assert expected in data
