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


def ensure_ascii_headers(response):
    """
    WSGI 中间件：确保所有响应头都是 ASCII 编码的字符串或正确编码的字节。
    这样可以避免 UnicodeEncodeError: 'latin-1' codec can't encode characters...
    """
    for key, value in list(response.headers):
        # 如果头值包含非 ASCII 字符，则将其进行 RFC 5987 编码（用于文件名）或直接移除
        if isinstance(value, str):
            try:
                value.encode('latin-1')  # 尝试用 latin-1 编码（HTTP 头标准）
            except UnicodeEncodeError:
                # 包含非 ASCII 字符，尝试 UTF-8 编码后 base64 or quote
                if key.lower() == 'content-disposition':
                    # 已由 content_disposition() 处理，不应该出现这种情况
                    # 如果仍出现，移除该头或替换为 ASCII 版本
                    response.headers[key] = 'attachment; filename="download.csv"'
                else:
                    # 其他头移除非 ASCII 内容
                    try:
                        safe_value = value.encode('utf-8', 'ignore').decode('ascii', 'ignore')
                        if safe_value:
                            response.headers[key] = safe_value
                        else:
                            # 如果全是非 ASCII 字符，移除该头
                            del response.headers[key]
                    except Exception:
                        # 最后的手段：移除该头
                        if key in response.headers:
                            del response.headers[key]
    return response


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
    
    # 注册响应头过滤中间件，确保所有头都是 ASCII 兼容的
    app.after_request(ensure_ascii_headers)

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
    
    # 注册自定义Jinja2过滤器
    @app.template_filter('translate_role')
    def translate_role(role):
        """翻译用户角色为中文"""
        role_map = {
            'admin': '管理员',
            'user': '普通用户',
            'technician': '技术员',
            'department_head': '部门主管',
        }
        return role_map.get(role, role)
    
    @app.template_filter('translate_status')
    def translate_status(status):
        """翻译工单/审批状态为中文"""
        status_map = {
            'pending': '待审批',
            'approved': '已批准',
            'rejected': '已拒绝',
            'completed': '已完成',
            'cancelled': '已取消',
            'department_head_approved': '部门主管已批准',
            'admin_approved': '管理员已批准',
            'available': '可用',
            'unavailable': '不可用',
            'in_use': '使用中',
            'retired': '已报废',
            'draft': '草稿',
            'submitted': '已提交',
            'processing': '处理中',
            'on_loan': '借用中',
            'transferred': '已调拨',
            'scrapped': '已报废',
        }
        return status_map.get(status, status)

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
            # 兼容性修补：为 workflow_step 表添加 required_approvals 列（整数，默认1）
            try:
                conn.execute('SELECT required_approvals FROM workflow_step LIMIT 1')
            except Exception:
                try:
                    conn.execute('ALTER TABLE workflow_step ADD COLUMN required_approvals INTEGER DEFAULT 1')
                    print('Patched database: added column workflow_step.required_approvals')
                except Exception as e:
                    print('Warning: failed to add workflow_step.required_approvals automatically:', e)
            # 兼容性修补：为 workflow_node 添加并行字段与拒绝动作配置
            try:
                conn.execute('SELECT is_parallel FROM workflow_node LIMIT 1')
            except Exception:
                try:
                    conn.execute("ALTER TABLE workflow_node ADD COLUMN is_parallel BOOLEAN DEFAULT 0")
                    conn.execute("ALTER TABLE workflow_node ADD COLUMN required_approvals INTEGER DEFAULT 1")
                    conn.execute("ALTER TABLE workflow_node ADD COLUMN actions_on_reject TEXT")
                    print('Patched database: added workflow_node.is_parallel/required_approvals/actions_on_reject')
                except Exception as e:
                    print('Warning: failed to add workflow_node compatibility columns automatically:', e)
            # 兼容性修补：为 approval_workflow 添加 required_approvals 与 actions_on_reject
            try:
                conn.execute('SELECT required_approvals FROM approval_workflow LIMIT 1')
            except Exception:
                try:
                    conn.execute("ALTER TABLE approval_workflow ADD COLUMN required_approvals INTEGER DEFAULT 1")
                    conn.execute("ALTER TABLE approval_workflow ADD COLUMN actions_on_reject TEXT")
                    print('Patched database: added approval_workflow.required_approvals/actions_on_reject')
                except Exception as e:
                    print('Warning: failed to add approval_workflow compatibility columns automatically:', e)
            # 兼容性修补：为 workflow_template 添加 is_default 列
            try:
                conn.execute('SELECT is_default FROM workflow_template LIMIT 1')
            except Exception:
                try:
                    conn.execute("ALTER TABLE workflow_template ADD COLUMN is_default BOOLEAN DEFAULT 0")
                    print('Patched database: added workflow_template.is_default')
                except Exception as e:
                    print('Warning: failed to add workflow_template.is_default automatically:', e)
            # 兼容性修补：为 workflow_node 添加 approver_user_id 列
            try:
                conn.execute('SELECT approver_user_id FROM workflow_node LIMIT 1')
            except Exception:
                try:
                    conn.execute("ALTER TABLE workflow_node ADD COLUMN approver_user_id INTEGER")
                    print('Patched database: added workflow_node.approver_user_id')
                except Exception as e:
                    print('Warning: failed to add workflow_node.approver_user_id automatically:', e)
            # 兼容性修补：为 workflow_node 添加 approver_user_ids 列（JSON 文本）
            try:
                conn.execute('SELECT approver_user_ids FROM workflow_node LIMIT 1')
            except Exception:
                try:
                    conn.execute("ALTER TABLE workflow_node ADD COLUMN approver_user_ids TEXT")
                    print('Patched database: added workflow_node.approver_user_ids')
                except Exception as e:
                    print('Warning: failed to add workflow_node.approver_user_ids automatically:', e)
            # 兼容性修补：为 user 表添加新的工作流权限列
            try:
                conn.execute('SELECT can_edit_workflow FROM user LIMIT 1')
            except Exception:
                try:
                    conn.execute("ALTER TABLE user ADD COLUMN can_edit_workflow BOOLEAN DEFAULT 0")
                    print('Patched database: added user.can_edit_workflow')
                except Exception as e:
                    print('Warning: failed to add user.can_edit_workflow automatically:', e)
            try:
                conn.execute('SELECT can_manage_workflow_templates FROM user LIMIT 1')
            except Exception:
                try:
                    conn.execute("ALTER TABLE user ADD COLUMN can_manage_workflow_templates BOOLEAN DEFAULT 0")
                    print('Patched database: added user.can_manage_workflow_templates')
                except Exception as e:
                    print('Warning: failed to add user.can_manage_workflow_templates automatically:', e)
            # 兼容性修补：为 user 表添加 is_active 列（用于选择审批人时过滤）
            try:
                conn.execute('SELECT is_active FROM user LIMIT 1')
            except Exception:
                try:
                    conn.execute("ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT 1")
                    print('Patched database: added user.is_active')
                except Exception as e:
                    print('Warning: failed to add user.is_active automatically:', e)
            finally:
                conn.close()
    except Exception:
        # 在极端情况下跳过该步骤以避免阻塞应用启动
        pass

    return app


from app import models
