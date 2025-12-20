from app import create_app
from app import db
from app.models import User

app = create_app()
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True

with app.test_client() as c:
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print('未找到 admin 用户')
            raise SystemExit(1)
        admin_id = str(admin.id)
    # 使用 session_transaction 注入 login 信息
    with c.session_transaction() as sess:
        sess['_user_id'] = admin_id
        sess['_fresh'] = True
    # 现在访问部门管理
    resp = c.get('/admin/departments')
    print('Status code:', resp.status_code)
    if resp.status_code == 200:
        print('部门管理页面长度:', len(resp.get_data(as_text=True)))
    else:
        print('响应片段:', resp.get_data(as_text=True)[:400])
