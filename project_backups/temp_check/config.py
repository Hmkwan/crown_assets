import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLAlchemy 性能优化
    SQLALCHEMY_ECHO = False  # 生产环境不打印SQL
    SQLALCHEMY_POOL_SIZE = 10  # 连接池大小
    SQLALCHEMY_POOL_RECYCLE = 3600  # 连接回收时间
    SQLALCHEMY_MAX_OVERFLOW = 20  # 最大溢出连接数
    
    # 可选：当无法找到 approver 时回退使用的管理员邮箱（优先于第一个 admin）
    FALLBACK_ADMIN_EMAIL = os.environ.get('FALLBACK_ADMIN_EMAIL') or None
    # 时区配置 - 中国北京时间
    TIMEZONE = 'Asia/Shanghai'
    
    # 性能优化配置
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 静态文件缓存1年
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大上传16MB