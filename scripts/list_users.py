from app import create_app
from app.models import User

app = create_app()
with app.app_context():
    try:
        users = User.query.limit(100).all()
        print('用户数:', User.query.count())
        print('用户名列表:', [u.username for u in users])
    except Exception as e:
        import traceback
        traceback.print_exc()
        print('发生异常:', e)
