import os

# Pytest session hooks: 在测试收集之前创建数据库表并初始化少量测试数据

def pytest_sessionstart(session):
    """在 pytest 会话开始时初始化应用数据库并插入必要的种子数据。"""
    # Prefer an explicit TEST_DATABASE_URI (e.g., a Postgres testing DB). If not set, fall back to a shared sqlite file for session reuse.
    import os
    from urllib.parse import urlparse

    db_uri = os.environ.get('TEST_DATABASE_URI') or os.environ.get('TEST_DATABASE_URL')
    if db_uri:
        # Safety: if pointing to a Postgres host that is not localhost, require an explicit override to avoid accidental runs against remote/production DBs
        try:
            parsed = urlparse(db_uri)
            scheme = parsed.scheme or ''
            hostname = parsed.hostname
            if scheme.startswith('postgres') and hostname not in ('localhost', '127.0.0.1', '::1'):
                if os.environ.get('FORCE_ALLOW_REMOTE_DB') != '1':
                    raise RuntimeError(
                        f"TEST_DATABASE_URI points to remote host ({hostname}). To proceed set FORCE_ALLOW_REMOTE_DB=1 explicitly."
                    )
        except Exception:
            # If urlparse or checks fail, be conservative and require explicit setting to proceed with non-sqlite DB
            if 'sqlite' not in (db_uri or '') and os.environ.get('FORCE_ALLOW_REMOTE_DB') != '1':
                raise RuntimeError("Invalid or remote TEST_DATABASE_URI; set FORCE_ALLOW_REMOTE_DB=1 to proceed.")
        os.environ['TEST_DATABASE_URI'] = db_uri
    else:
        # 不再默认回退到 SQLite：强制要求在测试/CI 环境中显式设置 TEST_DATABASE_URI（例如指向一个本地或CI中的 PostgreSQL 测试数据库）。
        if not os.environ.get('TEST_DATABASE_URI'):
            raise RuntimeError("TEST_DATABASE_URI must be set to a PostgreSQL test database (e.g., postgresql://...) for running tests. SQLite support has been removed.")

    os.environ.setdefault('TESTING', '1')

    # 避免在初始化过程中跳过 SocketIO 初始化，以便测试能够检查 app.socketio
    # 但如果环境需要跳过，可通过设置 SKIP_SOCKETIO_INIT=1。
    from app import create_app, db
    app = create_app()
    with app.app_context():
        # 创建所有表
        db.create_all()

        # 初始化系统审批角色（如果尚未创建）
        try:
            from app.approval_roles import init_system_approval_roles
            init_system_approval_roles()
        except Exception:
            pass

        # 确保存在一个 admin 用户
        try:
            from app.models import User, Equipment
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', email='admin@example.com', role='admin', department='IT')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()

            # 创建一台测试设备，部分审批测试脚本依赖
            if not Equipment.query.first():
                eq = Equipment(name='测试设备', department='企管部', status='在用')
                db.session.add(eq)
                db.session.commit()
        except Exception:
            db.session.rollback()
            pass
