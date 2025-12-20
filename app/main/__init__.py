from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes
from app.main import asset_routes  # 统一资产/配件管理中心
from app.main import cost_routes   # 成本分析
from app.main import inventory_routes  # 库存预警
from app.main import lifecycle_routes  # 生命周期管理
from app.main import workflow_routes  # 审批流程模板管理
from app.main import approval_history_routes  # 审批历史和管理员干预
from app.main import user_api_routes  # 用户API
from app.main import announcement_routes  # 系统公告
from app.main import wework_admin_routes  # 企业微信管理
from app.main import statistics_routes  # 统计报表中心
from app.main import loan_return_routes  # 借用归还验收
from app.main import scrap_disposal_routes  # 报废处置管理
from app.main import maintenance_routes  # 保养计划管理