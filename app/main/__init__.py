from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes
from app.main import asset_routes  # 统一资产/配件管理中心