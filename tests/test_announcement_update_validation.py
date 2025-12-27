# -*- coding: utf-8 -*-
import pytest
from app import create_app, db
from app.models import User, Announcement


def test_edit_announcement_empty_content_does_not_commit(tmp_path):
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()

        # create admin user (use unique email to avoid collisions with other tests)
        import uuid
        suffix = uuid.uuid4().hex[:8]
        admin = User(username=f'admin-test-{suffix}', email=f'admin-{suffix}@example.com', is_admin=True)
        admin.set_password('pass')
        db.session.add(admin)
        db.session.flush()

        # create an announcement with content (set creator_id to the admin user)
        ann = Announcement(title='T', content='initial content', creator_id=admin.id)
        db.session.add(ann)
        db.session.commit()

        client = app.test_client()
        # login
        resp = client.post('/auth/login', data={'username': admin.username, 'password': 'pass'}, follow_redirects=True)
        assert resp.status_code in (200, 302)

        # attempt to edit with empty content
        resp2 = client.post(f'/admin/announcements/{ann.id}/edit', data={'title': 'T2', 'content': ''}, follow_redirects=True)
        assert resp2.status_code == 200
        # use text for unicode matching
        assert '公告内容不能为空' in resp2.get_data(as_text=True)

        # reload announcement and ensure content unchanged
        ann2 = Announcement.query.get(ann.id)
        assert ann2.content == 'initial content'


def test_edit_announcement_empty_content_does_not_leak_db_errors(tmp_path):
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()

        import uuid
        suffix = uuid.uuid4().hex[:8]
        admin = User(username=f'admin-test-{suffix}', email=f'admin-{suffix}@example.com', is_admin=True)
        admin.set_password('pass')
        db.session.add(admin)
        db.session.flush()

        ann = Announcement(title='T', content='initial content', creator_id=admin.id)
        db.session.add(ann)
        db.session.commit()

        client = app.test_client()
        resp = client.post('/auth/login', data={'username': admin.username, 'password': 'pass'}, follow_redirects=True)
        assert resp.status_code in (200, 302)

        resp2 = client.post(f'/admin/announcements/{ann.id}/edit', data={'title': 'T2', 'content': ''}, follow_redirects=True)
        text = resp2.get_data(as_text=True)
        assert resp2.status_code == 200
        # flash present
        assert '公告内容不能为空' in text
        # 不应把 DB/psycopg2 异常细节展示给用户
        assert 'psycopg2' not in text
        assert 'null value' not in text
        assert 'This Session' not in text


def test_prevent_null_content_flush(tmp_path):
    """模拟意外把 announcement.content 设为 None，然后触发会导致 Session.autoflush 的查询，
    验证 before_flush 钩子会恢复原始内容以避免 DB IntegrityError。"""
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()

        import uuid
        suffix = uuid.uuid4().hex[:8]
        admin = User(username=f'admin-test-{suffix}', email=f'admin-{suffix}@example.com', is_admin=True)
        admin.set_password('pass')
        db.session.add(admin)
        db.session.flush()

        ann = Announcement(title='T', content='initial content', creator_id=admin.id)
        db.session.add(ann)
        db.session.commit()

        # Simulate a buggy code path that assigns None
        ann.content = None

        # Trigger an autoflush by doing an unrelated query
        # Should not raise IntegrityError due to our before_flush listener
        from app.models import Notification
        count = Notification.query.filter_by(user_id=admin.id).count()

        ann2 = Announcement.query.get(ann.id)
        assert ann2.content == 'initial content' or ann2.content == ''  # 恢复为旧值或空字符串
