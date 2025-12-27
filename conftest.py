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
        # 在创建新表之前，清理老旧/兼容性的审批相关表（如果存在旧结构），以免在测试中出现模式不一致
        try:
            from sqlalchemy import inspect, text
            insp = inspect(db.engine)
            for tbl in insp.get_table_names():
                if tbl.startswith('approval_') or tbl == 'workflow_instance':
                    db.session.execute(text(f"DROP TABLE IF EXISTS {tbl} CASCADE"))
            db.session.commit()
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass

        # 创建所有表
        db.create_all()

        # 使 db.drop_all 更加健壮：在 teardown 时如果因缺失命名约束导致 DROP CONSTRAINT 失败，或因约束依赖导致 DROP TABLE 失败，做容错处理
        try:
            from sqlalchemy.exc import ProgrammingError as SAProgrammingError, InternalError as SAInternalError
            from sqlalchemy import text
            _orig_drop_all = db.drop_all
            def _safe_drop_all(*args, **kwargs):
                try:
                    return _orig_drop_all(*args, **kwargs)
                except (SAProgrammingError, SAInternalError) as e:
                    # 如果是因为约束不存在导致的错误，回滚并忽略；否则尝试更强力的清理（仅适用于测试环境）
                    msg = str(e)
                    if 'does not exist' in msg or ('constraint' in msg and 'does not exist' in msg):
                        try:
                            db.session.rollback()
                        except Exception:
                            pass
                        return
                    # 如果是因为依赖对象仍存在导致 DROP TABLE 失败，尝试重建 schema（DROP SCHEMA CASCADE）以保证测试环境干净
                    if 'depends on' in msg or 'DependentObjectsStillExist' in msg:
                        try:
                            db.session.rollback()
                        except Exception:
                            pass
                        try:
                            # 只在测试数据库上执行强力清理；pytest_sessionstart 已经保证 TEST_DATABASE_URI 指向本地测试 DB
                            db.session.execute(text("DROP SCHEMA public CASCADE"))
                            db.session.execute(text("CREATE SCHEMA public"))
                            db.session.commit()
                        except Exception:
                            try:
                                db.session.rollback()
                            except Exception:
                                pass
                        return
                    raise
            db.drop_all = _safe_drop_all
        except Exception:
            # 在极端环境下保守回退到原行为
            pass

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
