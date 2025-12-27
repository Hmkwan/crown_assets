try:
    import eventlet
    eventlet.monkey_patch()
except Exception:
    pass

import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

from flask import Flask, jsonify
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


def get_beijing_now():
    """获取当前北京时间（Asia/Shanghai），返回时区感知的 datetime（tzinfo 不为 None）。"""
    try:
        import pytz
        from datetime import datetime
        tz = pytz.timezone('Asia/Shanghai')
        # 不再去除 tzinfo，返回带有 Asia/Shanghai tzinfo 的时间对象
        return datetime.now(tz)
    except:
        from datetime import datetime, timezone
        # 如果 pytz 不可用，返回一个带有 +08:00 偏移的 timezone-aware datetime
        from datetime import timedelta
        return datetime.now(timezone(timedelta(hours=8)))


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

    # 确保在测试上下文或自定义 TestConfig 未设置 SECRET_KEY 时仍能打开 session
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'test-secret'

    # 避免 Flask-SQLAlchemy 的 FSADeprecationWarning：确保显式设置 SQLALCHEMY_TRACK_MODIFICATIONS
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    # 如果在 pytest 上下文中运行（如 CI 或本地测试），或显式设置 TESTING=1，使用内存 SQLite 数据库以避免依赖外部 Postgres/psycopg2
    import sys as _sys
    if os.environ.get('PYTEST_CURRENT_TEST') or os.environ.get('TESTING') == '1' or 'pytest' in _sys.modules:
        # 运行在测试/CI 环境中时启用 TESTING，但不再默认回退到 SQLite。
        app.config['TESTING'] = True
        if os.environ.get('TEST_DATABASE_URI'):
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('TEST_DATABASE_URI')
        app.config['WTF_CSRF_ENABLED'] = False
        # 保持 SQLALCHEMY_ENGINE_OPTIONS 的默认配置（Postgres 优化配置不再被覆盖）

    # 安全默认：在非生产环境默认禁用 Redis（以避免开发环境/CI 被 Redis 连接卡住），生产环境仍需显示启用
    if app.config.get('ENV', '').lower() != 'production' and os.environ.get('REDIS_DISABLED') is None:
        # 允许环境或显式配置覆盖
        app.config.setdefault('REDIS_DISABLED', True)

    import platform

    # 配置时区 - 中国北京时间
    import importlib as _importlib
    try:
        _importlib.import_module('os').environ['TZ'] = 'Asia/Shanghai'
    except Exception:
        pass
    if platform.system() != 'Windows':
        import time
        time.tzset()

    # 性能优化：禁用模板自动重载（生产环境）
    if not app.debug:
        app.jinja_env.auto_reload = False

    db.init_app(app)
    login.init_app(app)
    # 兼容旧测试/脚本：确保 login.session_key 可用（测试中直接操作 session）
    try:
        login.session_key = '_user_id'
    except Exception:
        pass

    # Database readiness check: 如果关键表不存在，则设置标记并在请求时返回友好 503
    from sqlalchemy import inspect
    def _check_db_ready():
        try:
            inspector = inspect(db.engine)
            # 最小检查：必须存在 app_user 表（其他关键表可按需添加）
            required_tables = ['app_user']
            missing = [t for t in required_tables if not inspector.has_table(t)]
            if missing:
                app.logger.error("数据库 schema 不完整，缺失表: %s", missing)
                app.config['DB_READY'] = False
            else:
                app.config['DB_READY'] = True
        except Exception as e:
            # 无法连接数据库或其他错误，标记为不可用并记录
            app.logger.exception('数据库就绪检查失败')
            app.config['DB_READY'] = False

    # 在第一次请求前执行检查（避免在某些启动阶段早于 DB 可用性运行）
    @app.before_first_request
    def _run_db_check_once():
        _check_db_ready()

    # 在每次请求前确保 DB 就绪，否则返回 503（允许 /static 与 health 路径）
    from flask import request, jsonify, make_response

    @app.before_request
    def require_db_ready():
        if not app.config.get('DB_READY', True):
            # 允许健康检查或静态资源通过
            if request.path.startswith('/static') or request.path.startswith('/health'):
                return None
            app.logger.warning('拒绝请求：数据库未就绪（路径 %s）', request.path)
            # 对 API 请求返回 JSON 503
            if request.path.startswith('/api/') or request.is_json:
                return jsonify({'error': '服务暂不可用', 'message': '数据库尚未初始化或 schema 不完整，请稍后重试'}), 503
            # 对普通页面返回简短的 HTML 503 响应（避免渲染依赖 DB 的模板）
            return make_response('<h1>服务暂不可用</h1><p>数据库未初始化或 schema 不完整，请稍后重试。</p>', 503)

    # 全局 SQLAlchemy 错误处理：记录异常并返回友好信息，避免错误信息泄露到用户界面
    from sqlalchemy.exc import SQLAlchemyError
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(err):
        app.logger.exception('捕获到数据库异常：%s', err)
        # API 请求返回 JSON 错误
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({'error': '数据库错误', 'message': '内部错误，请稍后重试'}), 500
        # 页面请求显示通用提示（不泄露内部信息）
        return make_response('<h1>服务器错误</h1><p>数据库发生错误，请联系管理员。</p>', 500)

    # 配置未授权处理器 - API请求返回JSON而非重定向
    @login.unauthorized_handler
    def unauthorized():
        from flask import request
        # 判断是否为API请求
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Unauthorized', 'message': '请先登录'}), 401
        # 普通页面请求重定向到登录页
        from flask import redirect, url_for
        return redirect(url_for('auth.login', next=request.url))
    
    # 初始化SocketIO实时通知
    # 可通过环境变量 SKIP_SOCKETIO_INIT=1 跳过（脚本/维护场景）以避免因 Redis 不可用而阻塞启动
    try:
        if not os.environ.get('SKIP_SOCKETIO_INIT'):
            from app.socketio_handler import init_socketio
            socketio = init_socketio(app)
            app.socketio = socketio  # 保存到app对象
            print('✓ SocketIO实时通知系统已初始化')
        else:
            print('SKIP_SOCKETIO_INIT=1，跳过 SocketIO 初始化')
            app.socketio = None
    except Exception as e:
        print(f'⚠ SocketIO初始化失败: {e}')
        app.socketio = None
    
    # 初始化 CSRF 保护并在模板中提供 csrf_token() 全局函数
    try:
        csrf.init_app(app)
        app.jinja_env.globals['csrf_token'] = generate_csrf
        
        # CSRF 错误处理器：当CSRF检查失败时返回JSON而不是HTML
        from flask_wtf.csrf import CSRFError
        @app.errorhandler(CSRFError)
        def handle_csrf_error(e):
            return jsonify({'success': False, 'message': 'CSRF token missing or invalid'}), 400
        
    except Exception as e:
        # 如果 CSRF 初始化失败，不阻塞应用启动，但记录信息
        print('Warning: CSRFProtect init failed:', e)
    
    # 注册响应头过滤中间件,确保所有头都是 ASCII 兼容的
    app.after_request(ensure_ascii_headers)
    
    # 错误处理：确保每个请求开始时session状态正常
    @app.before_request
    def before_request():
        # 主动回滚任何可能处于错误状态的事务
        try:
            db.session.rollback()
        except Exception:
            pass
    
    # 错误处理：自动回滚失败的事务
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if exception:
            db.session.rollback()
        db.session.remove()

    @login.user_loader
    def load_user(user_id):
        # 延迟导入，避免循环依赖
        from app.models import User
        return User.query.get(int(user_id))
    
    @app.context_processor
    def inject_unread_notifications():
        from flask_login import current_user
        unread_count = 0
        if current_user.is_authenticated:
            try:
                # 延迟导入，避免循环依赖
                from app.models import Notification
                unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
            except Exception:
                # 遇到任何异常时记录并返回 0，避免模板因为未定义变量而抛出错误
                import logging
                logging.getLogger(__name__).exception('计算未读通知时出错，返回 0 作为默认值')
        # 返回模板中期望的变量名 `unread_notifications_count`
        return dict(unread_notifications_count=unread_count)

    @app.context_processor
    def inject_summernote_availability():
        """模板上下文：指示是否存在本地官方 Summernote 文件（用于优先加载本地完整版）"""
        try:
            vendor_path = os.path.join(app.static_folder, 'vendor', 'summernote', 'summernote-bs4.min.js')
            available = os.path.exists(vendor_path)
        except Exception:
            available = False
        return dict(SUMMERNOTE_FULL_AVAILABLE=available)

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
            # 以下角色仅用于显示历史数据，新用户仅可选择管理员或普通用户
            'technician': '技术员(已废弃)',
            'department_head': '部门主管(已废弃)',
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
    
    @app.template_filter('translate_maintenance_type')
    def translate_maintenance_type(mtype):
        """翻译保养类型为中文"""
        type_map = {
            'daily': '每日',
            'weekly': '每周',
            'monthly': '每月',
            'quarterly': '每季度',
            'yearly': '每年',
            'custom': '自定义',
        }
        return type_map.get(mtype, mtype)

    # 日期时间格式化过滤器：把存储的 UTC(naive) 时间转换为 Asia/Shanghai 并格式化
    def format_datetime_filter(dt, fmt='%Y-%m-%d %H:%M'):
        if not dt:
            return ''
        try:
            import pytz
            from datetime import datetime
            # 假定数据库中存储为 UTC naive（datetime.utcnow），先设置为 UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=pytz.UTC)
            tz = pytz.timezone('Asia/Shanghai')
            localized = dt.astimezone(tz)
            return localized.strftime(fmt)
        except Exception:
            try:
                # 最后兜底，直接用 str()
                return str(dt)
            except Exception:
                return ''

    # 注册模板过滤器，使用 add_template_filter 以确保在不同环境下可靠可见
    app.add_template_filter(format_datetime_filter, name='format_dt')

    # 日志过滤器：抑制一些常见但无害的 engineio/socketio 报错信息（例如短连接导致的 Bad file descriptor）
    try:
        import logging

        class _SuppressEngineIOSpecificMessages(logging.Filter):
            def filter(self, record):
                try:
                    msg = record.getMessage()
                    # 过滤掉短连接/套接字关闭相关的噪音日志
                    if 'Bad file descriptor' in msg or 'socket shutdown error' in msg or '未认证用户尝试连接' in msg:
                        return False
                except Exception:
                    # 若解析日志消息失败，保守起见不拦截
                    return True
                return True

        _suppress_filter = _SuppressEngineIOSpecificMessages()
        for logger_name in ('engineio', 'socketio'):
            try:
                lg = logging.getLogger(logger_name)
                lg.addFilter(_suppress_filter)
            except Exception:
                # 不阻塞启动，仅尽力而为
                pass

        # 额外附加到 root logger 和 gunicorn 的日志器，覆盖从 stdout/stderr 产生的噪音
        try:
            try:
                logging.getLogger().addFilter(_suppress_filter)
            except Exception:
                pass
            for logger_name in ('gunicorn.error', 'gunicorn.access', 'gunicorn'):
                try:
                    lg = logging.getLogger(logger_name)
                    lg.addFilter(_suppress_filter)
                except Exception:
                    pass
        except Exception:
            # 保守处理：任何错误都不阻塞应用启动
            pass
    except Exception:
        # 如果 logging 相关出现任何问题也不阻塞应用启动
        pass

    # 包装 sys.stderr，拦截直接写入 stderr 的噪音（例如 engineio 打印的 socket shutdown 信息）
    try:
        import sys

        class _FilteredStderr:
            def __init__(self, orig, blocked_substrings=None):
                self._orig = orig
                self._buffer = ''
                self._blocked = blocked_substrings or ['Bad file descriptor', 'socket shutdown error', '未认证用户尝试连接']

            def write(self, data):
                try:
                    text = str(data)
                except Exception:
                    try:
                        self._orig.write(data)
                    except Exception:
                        pass
                    return

                self._buffer += text
                # 逐行处理，只在行结束时输出，避免截断
                if '\n' in self._buffer:
                    parts = self._buffer.splitlines(True)
                    for part in parts:
                        # 如果该行包含任意被屏蔽子串则忽略
                        if any(sub in part for sub in self._blocked):
                            continue
                        try:
                            self._orig.write(part)
                        except Exception:
                            pass
                    # 保留未终止行片段
                    if not self._buffer.endswith('\n'):
                        self._buffer = parts[-1]
                    else:
                        self._buffer = ''

            def flush(self):
                try:
                    if self._buffer and not any(sub in self._buffer for sub in self._blocked):
                        self._orig.write(self._buffer)
                    self._orig.flush()
                except Exception:
                    pass

        # 仅在非交互终端中替换 stderr（避免干扰开发 REPL）
        try:
            if not getattr(sys, 'ps1', None):
                sys.stderr = _FilteredStderr(sys.stderr)
        except Exception:
            pass
    except Exception:
        pass

    # 强力方案：重定向文件描述符2 (stderr) 到过滤线程，拦截底层直接写入的噪音
    try:
        import threading, time

        def _install_fd2_filter(blocked_substrings=None):
            blocked = blocked_substrings or ['Bad file descriptor', 'socket shutdown error', '未认证用户尝试连接']
            try:
                import importlib
                _os = importlib.import_module('os')
                # 备份原始 stderr fd
                orig_fd = _os.dup(2)
                rfd, wfd = _os.pipe()

                # 将 process 的 fd 2 替换为写端；之后底层写入会进入管道
                _os.dup2(wfd, 2)
                try:
                    _os.close(wfd)
                except Exception:
                    pass

                def _reader():
                    try:
                        # 读取端以二进制模式读取并按行处理
                        with _os.fdopen(rfd, 'rb', closefd=True) as rf, _os.fdopen(orig_fd, 'wb', closefd=False) as wf:
                            buffer = b''
                            while True:
                                chunk = rf.read(1024)
                                if not chunk:
                                    # 若短时间无数据，避免忙等待
                                    time.sleep(0.1)
                                    continue
                                buffer += chunk
                                while b'\n' in buffer:
                                    line, buffer = buffer.split(b'\n', 1)
                                    line_nl = line + b'\n'
                                    try:
                                        text = line_nl.decode('utf-8', errors='replace')
                                    except Exception:
                                        text = ''
                                    if any(sub in text for sub in blocked):
                                        # 丢弃匹配行
                                        continue
                                    try:
                                        wf.write(line_nl)
                                        wf.flush()
                                    except Exception:
                                        # 忽略写失败
                                        pass
                    except Exception:
                        import logging
                        logging.getLogger(__name__).exception('fd2 reader thread 异常')

                t = threading.Thread(target=_reader, name='fd2-filter', daemon=True)
                t.start()
            except Exception:
                import logging
                logging.getLogger(__name__).exception('安装 fd2 过滤器失败')

        try:
            # 在非交互环境中安装（避免影响 REPL)
            # 该强力方案会对底层文件描述符进行替换，可能与 gunicorn/eventlet 的
            # worker fork/线程模型发生微妙交互，默认不开启。仅当明确设置
            # 环境变量 ENABLE_FD2_FILTER=1 时才启用（由运维/调试时手动打开）。
            if not getattr(__import__('sys'), 'ps1', None) and _importlib.import_module('os').environ.get('ENABLE_FD2_FILTER', '0') == '1':
                _install_fd2_filter()
        except Exception:
            pass
    except Exception:
        pass

    # 确保模型模块先初始化，避免在注册蓝图时出现循环导入
    try:
        # 使用普通导入，让包内的 shim 负责从顶层 models.py 加载符号以避免重复加载导致的表定义冲突
        import importlib
        importlib.import_module('app.models')
    except Exception as e:
        print('Warning: failed to import app.models early:', e)

    # 尝试提前加载审批相关模型并把关键类导出到 app.models 命名空间，
    # 以避免 `from app.models import WorkflowNode` 在注册蓝图时失败
    try:
        import importlib, sys
        approval_mod = importlib.import_module('app.approval_models')
        # 确保 app.models 已被加载为模块（create_app 中也尝试过），然后再设置属性
        try:
            importlib.import_module('app.models')
        except Exception:
            # 如果无法加载 models，此处仅记录并跳过设置（不阻塞启动）
            pass

        # 将审批相关类放到 app.models 模块命名空间，供旧代码直接导入使用
        import app as _app_pkg
        try:
            if hasattr(approval_mod, 'WorkflowNode'):
                setattr(_app_pkg.models, 'WorkflowNode', approval_mod.WorkflowNode)
            if hasattr(approval_mod, 'WorkflowTemplate'):
                setattr(_app_pkg.models, 'WorkflowTemplate', approval_mod.WorkflowTemplate)
        except AttributeError:
            # app.models 仍然不可用，记录并继续启动（create_app 的后续流程会再次尝试）
            print('Warning: app.models not available to attach approval models yet; will retry during runtime')
    except Exception as e:
        # 失败则继续，错误会在日志中体现
        print('Warning: preloading approval models failed:', e)

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

    # 旧版审批流 blueprint 已下线（避免与新版企业级审批接口重复）
    # 注册用户角色管理路由
    try:
        from app.user_roles_routes import user_roles_bp
        app.register_blueprint(user_roles_bp)
    except Exception as e:
        print('Error registering user_roles blueprint:', e)
    
    # 注册管理员路由（审批流程配置等）
    try:
        from app.admin.workflow_config_routes import admin_bp
        # 先导入审批角色管理路由（路由会自动添加到 admin_bp）
        from app.admin import approval_roles_routes
        from app.admin import approval_service_routes  # 审批服务API
        from app.admin import workflow_templates_routes  # 工作流模板管理
        from app.admin import approval_management_routes  # 审批流程管理
        # 然后注册 blueprint
        app.register_blueprint(admin_bp)
    except Exception as e:
        print('Error registering admin blueprint:', e)
        import traceback
        traceback.print_exc()
    
    # 注册企业级审批系统API
    try:
        from app.api.approval_routes import approval_api
        app.register_blueprint(approval_api, url_prefix='/api/approval')
    except Exception as e:
        print('Error registering approval_api blueprint:', e)
        import traceback
        traceback.print_exc()
    
    # 注册审批统计报表路由
    try:
        from app.main.approval_report_routes import bp as approval_report_bp
        app.register_blueprint(approval_report_bp)
    except Exception as e:
        print('Error registering approval_report blueprint:', e)
        import traceback
        traceback.print_exc()
    
    # 注册聊天系统页面路由，使用 /chat 前缀
    try:
        from app.chat_routes import chat_bp
        app.register_blueprint(chat_bp, url_prefix='/chat')
    except Exception as e:
        print('Error registering chat blueprint:', e)
        import traceback
        traceback.print_exc()

    # 注册聊天API路由，使用 /api/chat 前缀
    try:
        from app.chat_api import bp as chat_api_bp
        app.register_blueprint(chat_api_bp, url_prefix='/api/chat')
        print('✓ 聊天API路由已注册')
    except Exception as e:
        print('Error registering chat_api blueprint:', e)
        import traceback
        traceback.print_exc()
    
    # 初始化定时任务调度器
    try:
        from app.scheduler import init_scheduler
        init_scheduler(app)
    except Exception as e:
        print('Error initializing scheduler:', e)
        import traceback
        traceback.print_exc()

    # 尝试对缺失的 DB 列做一次简单兼容性修补(例如新增 ApprovalWorkflow.auto_assigned)
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
                    conn.execute("ALTER TABLE approval_workflow ADD COLUMN auto_assigned BOOLEAN DEFAULT false")
                    print('Patched database: added column approval_workflow.auto_assigned')
                except Exception as e:
                    # 非致命：打印警告，继续运行（某些环境需要手动迁移）
                    print('Warning: failed to add auto_assigned column automatically:', e)
            
            # 兼容性修补：为 workflow_node 添加并行字段与拒绝动作配置
            try:
                conn.execute('SELECT is_parallel FROM workflow_node LIMIT 1')
            except Exception:
                try:
                    conn.execute("ALTER TABLE workflow_node ADD COLUMN is_parallel BOOLEAN DEFAULT false")
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
                    conn.execute("ALTER TABLE workflow_template ADD COLUMN is_default BOOLEAN DEFAULT false")
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
            # 兼容性修补：为 workflow_node 添加 role_required_name 列（用于兼容旧库）
            try:
                conn.execute('SELECT role_required_name FROM workflow_node LIMIT 1')
            except Exception:
                try:
                    conn.execute("ALTER TABLE workflow_node ADD COLUMN role_required_name VARCHAR(64)")
                    print('Patched database: added workflow_node.role_required_name')
                except Exception as e:
                    print('Warning: failed to add workflow_node.role_required_name automatically:', e)
            # 兼容性修补：为 chat_attachment 添加 upload_user_id 列（上传者），避免缺失导致 500
            try:
                conn.execute('SELECT upload_user_id FROM chat_attachment LIMIT 1')
            except Exception:
                try:
                    conn.execute("ALTER TABLE chat_attachment ADD COLUMN upload_user_id INTEGER")
                    print('Patched database: added chat_attachment.upload_user_id')
                except Exception as e:
                    print('Warning: failed to add chat_attachment.upload_user_id automatically:', e)

            # 兼容性修补：允许 chat_attachment.message_id 为 NULL（上传时不强制关联消息），Postgres 需要 DROP NOT NULL
            try:
                # Try an ALTER that will succeed on Postgres
                conn.execute("ALTER TABLE chat_attachment ALTER COLUMN message_id DROP NOT NULL")
                print('Patched database: chat_attachment.message_id is now nullable')
            except Exception as e:
                # Not fatal; may already be nullable or running on DB that doesn't support this syntax
                print('Notice: could not ensure chat_attachment.message_id nullable automatically:', e)

            # 兼容性修补：允许 chat_attachment.upload_user_id 为 NULL（回填前临时可空，以便插入 NULL 值），Postgres 需要 DROP NOT NULL
            try:
                conn.execute("ALTER TABLE chat_attachment ALTER COLUMN upload_user_id DROP NOT NULL")
                print('Patched database: chat_attachment.upload_user_id is now nullable')
            except Exception as e:
                print('Notice: could not ensure chat_attachment.upload_user_id nullable automatically:', e)

            # 兼容性修补:为 user 表添加新的工作流权限列
            try:
                conn.execute('SELECT can_edit_workflow FROM app_user LIMIT 1')
            except Exception:
                try:
                    conn.execute("ALTER TABLE app_user ADD COLUMN can_edit_workflow BOOLEAN DEFAULT false")
                    print('Patched database: added user.can_edit_workflow')
                except Exception as e:
                    print('Warning: failed to add user.can_edit_workflow automatically:', e)
            try:
                conn.execute('SELECT can_manage_workflow_templates FROM app_user LIMIT 1')
            except Exception:
                try:
                    conn.execute("ALTER TABLE app_user ADD COLUMN can_manage_workflow_templates BOOLEAN DEFAULT false")
                    print('Patched database: added user.can_manage_workflow_templates')
                except Exception as e:
                    print('Warning: failed to add user.can_manage_workflow_templates automatically:', e)
            # 兼容性修补:为 user 表添加 is_active 列(用于选择审批人时过滤)
            try:
                conn.execute('SELECT is_active FROM app_user LIMIT 1')
            except Exception:
                try:
                    conn.execute("ALTER TABLE app_user ADD COLUMN is_active BOOLEAN DEFAULT true")
                    print('Patched database: added user.is_active')
                except Exception as e:
                    print('Warning: failed to add user.is_active automatically:', e)
            finally:
                conn.close()
    except Exception:
        # 在极端情况下跳过该步骤以避免阻塞应用启动
        pass

    from app.online_users import online_users_bp
    app.register_blueprint(online_users_bp, url_prefix='/api')

    from app.routes.announcement_routes import announcement_bp
    app.register_blueprint(announcement_bp, url_prefix='/api')

    # 开发辅助: 在调试模式或设置 DEV_ALLOW_DEV_ROUTE=1 时提供一个免登录的本地预览路由 `/ _dev/chat`。
    # 仅允许本地回环地址访问，避免在远程环境中暴露此路由。
    if app.debug or os.environ.get('DEV_ALLOW_DEV_ROUTE') == '1':
        from types import SimpleNamespace
        from flask import request, abort, render_template

        @app.route('/_dev/chat')
        def _dev_chat():
            if request.remote_addr not in ('127.0.0.1', '::1', 'localhost'):
                abort(403)
            fake_user = SimpleNamespace(id=1, is_authenticated=True)
            # 直接渲染 chat.html，传入一个伪造的 current_user 用于本地UI调试
            return render_template('chat.html', current_user=fake_user)

    return app



