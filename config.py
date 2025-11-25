import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 可选：当无法找到 approver 时回退使用的管理员邮箱（优先于第一个 admin）
    FALLBACK_ADMIN_EMAIL = os.environ.get('FALLBACK_ADMIN_EMAIL') or None