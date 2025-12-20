import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # 如果在 pytest 环境中或明确设置 TESTING=1，则默认使用内存 sqlite，避免在收集测试时依赖外部 Postgres/psycopg2
    import sys as _sys
    if os.environ.get('PYTEST_CURRENT_TEST') or os.environ.get('TESTING') == '1' or 'pytest' in _sys.modules:
        SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI', 'sqlite:///:memory:')
    else:
        # PostgreSQL 数据库配置（默认）
        # 格式: postgresql://用户名:密码@主机:端口/数据库名
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'postgresql://postgres:difyai123456@host.docker.internal:15432/it_asset'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLAlchemy 性能优化
    SQLALCHEMY_ECHO = False  # 生产环境不打印SQL
    
    # PostgreSQL 连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,           # 连接池大小
        'pool_recycle': 3600,      # 连接回收时间(秒)
        'max_overflow': 20,        # 超过pool_size后最多创建的连接数
        'pool_pre_ping': True,     # 连接前测试连接是否有效
    }
    
    # 可选：当无法找到 approver 时回退使用的管理员邮箱（优先于第一个 admin）
    FALLBACK_ADMIN_EMAIL = os.environ.get('FALLBACK_ADMIN_EMAIL') or None
    # 时区配置 - 中国北京时间
    TIMEZONE = 'Asia/Shanghai'
    
    # 定时任务配置 - 可以通过环境变量禁用特定任务
    SCHEDULER_ENABLED = os.environ.get('SCHEDULER_ENABLED', 'true').lower() == 'true'
    SCHEDULER_JOBS = {
        'maintenance_due': os.environ.get('SCHEDULER_MAINTENANCE_DUE', 'true').lower() == 'true',
        'overdue_loans': os.environ.get('SCHEDULER_OVERDUE_LOANS', 'true').lower() == 'true',
        'upcoming_returns': os.environ.get('SCHEDULER_UPCOMING_RETURNS', 'true').lower() == 'true',
        'pending_inspections': os.environ.get('SCHEDULER_PENDING_INSPECTIONS', 'true').lower() == 'true',
        'pending_approvals': os.environ.get('SCHEDULER_PENDING_APPROVALS', 'true').lower() == 'true',
    }
    
    # 性能优化配置
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 静态文件缓存1年
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大上传16MB
    
    # 企业微信集成配置
    # 在生产环境中,这些值应该从环境变量读取
    WEWORK_CORP_ID = os.environ.get('WEWORK_CORP_ID') or ''  # 企业ID
    WEWORK_AGENT_ID = os.environ.get('WEWORK_AGENT_ID') or ''  # 应用AgentId
    WEWORK_SECRET = os.environ.get('WEWORK_SECRET') or ''  # 应用Secret
    WEWORK_ENABLED = os.environ.get('WEWORK_ENABLED', 'false').lower() == 'true'  # 是否启用企业微信登录