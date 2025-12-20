from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes
from app.auth import wework_routes  # 企业微信登录