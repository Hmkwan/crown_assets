import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Notification

app = create_app()

with app.app_context():
    # 创建表（仅用于测试环境）
    db.create_all()

    # 创建测试用户
    user = User.query.filter_by(username='testuser').first()
    if not user:
        user = User(username='testuser', email='test@example.com', role='user')
        user.set_password('test')
        db.session.add(user)
        db.session.commit()

    # 创建一条通知
    notif = Notification(user_id=user.id, title='测试通知', message='这是一条测试通知')
    db.session.add(notif)
    db.session.commit()

    # 使用 test_client 并直接在会话里设置登录信息
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True

    resp = client.get('/notifications')
    print('status_code:', resp.status_code)
    data = resp.get_data(as_text=True)
    print('contains title:', '测试通知' in data)
    # 输出片段用于快速检查
    print(data[:1000])
