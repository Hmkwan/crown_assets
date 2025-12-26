from app import create_app, db
from config import Config
from app.models import Equipment
from app.main.statistics_routes import check_report_permission, export_statistics_xlsx


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def test_export_equipment_handles_string_department():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        # 创建一个设备，department 使用字符串形式（legacy 数据情况）
        import uuid
        eq = Equipment(name='LegacyEQ', serial_number='LEG-' + uuid.uuid4().hex[:8], department='旧部门')
        db.session.add(eq)
        db.session.commit()

        # 在请求上下文中调用导出函数，临时绕过权限检查
        original_check = check_report_permission
        try:
            # monkeypatch function to always allow
            def _allow():
                return True
            globals()['check_report_permission'] = _allow

            from flask_login import login_user
            admin = None
            # 确保存在 admin 用户并登录
            from app.models import User
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', email='admin@example.com', role='admin')
                admin.set_password('secret')
                db.session.add(admin)
                db.session.commit()

            with app.test_request_context():
                login_user(admin)
                resp = export_statistics_xlsx('equipment')
                # 应返回一个 Flask response（send_file）对象
                assert resp is not None
                # 检查返回的 mimetype 是 excel 类型
                headers = dict(resp.headers)
                assert 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in headers.get('Content-Type', '')
        finally:
            globals()['check_report_permission'] = original_check
