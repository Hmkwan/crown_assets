from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf


db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = '请先登录以访问此页面。'
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    # 初始化 CSRF 保护并在模板中提供 csrf_token() 全局函数
    try:
        csrf.init_app(app)
        app.jinja_env.globals['csrf_token'] = generate_csrf
    except Exception as e:
        # 如果 CSRF 初始化失败，不阻塞应用启动，但记录信息
        print('Warning: CSRFProtect init failed:', e)

    @login.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # 提供一个最小的 `moment` 函数到模板上下文，避免未安装 Flask-Moment 时模板报错
    @app.context_processor
    def inject_moment():
        class _Moment:
            def __init__(self, dt):
                self.dt = dt

            def _to_strftime(self, fmt):
                """Convert a small subset of moment.js-like format tokens to Python strftime tokens.
                Supported mappings: YYYY->%Y, MM->%m, DD->%d, HH->%H, mm->%M, ss->%S
                """
                mappings = [
                    ('YYYY', '%Y'),
                    ('MM', '%m'),
                    ('DD', '%d'),
                    ('HH', '%H'),
                    ('mm', '%M'),
                    ('ss', '%S'),
                ]
                for a, b in mappings:
                    fmt = fmt.replace(a, b)
                return fmt

            def format(self, fmt):
                try:
                    if not self.dt:
                        return ''
                    # convert common moment format tokens to strftime
                    fmt_py = self._to_strftime(fmt)
                    return self.dt.strftime(fmt_py)
                except Exception:
                    return ''

        def moment(dt):
            return _Moment(dt)

        return dict(moment=moment)

    from app.auth import bp as auth_bp
    try:
        app.register_blueprint(auth_bp)
    except Exception as e:
        # 捕获并打印注册 auth blueprint 时的异常，方便调试
        print('Error registering auth blueprint:', e)

    from app.main import bp as main_bp
    try:
        app.register_blueprint(main_bp)
    except Exception as e:
        print('Error registering main blueprint:', e)

    from app.api import bp as api_bp
    try:
        app.register_blueprint(api_bp, url_prefix='/api')
    except Exception as e:
        print('Error registering api blueprint:', e)

    # 尝试对缺失的 DB 列做一次简单兼容性修补（例如新增 ApprovalWorkflow.auto_assigned）
    # 这样在没有执行 Alembic 迁移时，应用依然可以运行。
    try:
        with app.app_context():
            # 检查 approval_workflow 表是否存在并包含 auto_assigned 列
            engine = db.get_engine(app)
            conn = engine.connect()
            try:
                # 简单尝试查询该列；若不存在会抛出异常
                conn.execute('SELECT auto_assigned FROM approval_workflow LIMIT 1')
            except Exception:
                try:
                    # SQLite 支持 ADD COLUMN
                    conn.execute('ALTER TABLE approval_workflow ADD COLUMN auto_assigned BOOLEAN DEFAULT 0')
                    print('Patched database: added column approval_workflow.auto_assigned')
                except Exception as e:
                    # 非致命：打印警告，继续运行（某些环境需要手动迁移）
                    print('Warning: failed to add auto_assigned column automatically:', e)
            finally:
                conn.close()
    except Exception:
        # 在极端情况下跳过该步骤以避免阻塞应用启动
        pass

    return app


from app import models