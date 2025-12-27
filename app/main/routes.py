from flask import render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user, login_user, logout_user
from app import db, get_beijing_now
from app.models import (
    User, Equipment, RepairOrder, SparePart, Department,
    PartReplacement, PartRequestOrder, UserActivityLog,
    ApprovalWorkflow, EquipmentType, Notification,
    EquipmentTransfer, EquipmentScrap, EquipmentLoan, EquipmentApplication,
    AccountRequest, AssetCost, AssetLifecycle, InventoryWarning, SparePartType,
    RoleDefinition, Permission
)
from app.approval_roles import ApprovalRole
from sqlalchemy import func, or_
from datetime import datetime, timedelta, timezone
import json
import os

from app.main import bp
from app.utils.import_export import content_disposition
from app.utils.db_management import (
    backup_database, restore_database, reset_database,
    list_backups, delete_backup, get_database_info,
    export_database_to_mysql, export_database_to_mssql, export_database_to_postgresql,
    validate_database_file, get_database_tables_info, get_table_data, get_table_chinese_name,
    get_backup_dir
)
from app.utils.qrcode_generator import (
    generate_qrcode, generate_asset_label,
    image_to_base64, image_to_bytes
)
from werkzeug.utils import secure_filename
import pathlib
try:
    import markdown2
except Exception:
    # Optional dependency for markdown rendering in a few routes.
    # Provide a minimal passthrough fallback for tests/environments without markdown2.
    class _FakeMarkdown:
        @staticmethod
        def markdown(s):
            return s

    markdown2 = _FakeMarkdown()

# 测试路由
@bp.route('/test_buttons')
def test_buttons():
    """测试按钮功能的诊断页面"""
    return render_template('test_buttons.html')


# 聊天功能路由
@bp.route('/chat')
@login_required
def chat():
    """聊天页面（使用现代视图作为默认实时页面）"""
    import time
    # 直接返回现代视图，实时功能通过 Socket.IO 在客户端初始化
    return render_template('chat_modern.html', cache_version=int(time.time()))

# 开发辅助：在开发环境下允许快速登录管理员（仅当 DEV_AUTO_LOGIN=1 或 DEBUG=True）
@bp.route('/__dev_login_admin')
def __dev_login_admin():
    import os
    from flask import current_app, abort
    # 开发辅助路由（仅用于本地调试）
    # 注意：暂时放宽访问检查以便本地开发时快速登录管理员，部署前应移除或限制访问。
    from app.models import User
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        return 'admin not found', 404
    # 直接登录管理员（仅限本地开发）
    login_user(admin)
    return redirect(url_for('main.index'))


# 旧版聊天页面(备用)
@bp.route('/chat/modern')
@login_required
def chat_modern():
    """现代化聊天页面(轮询方式)"""
    import time
    return render_template('chat_modern.html', cache_version=int(time.time()))


@bp.route('/chat/simple')
@login_required
def chat_simple():
    """简化版聊天页面(轮询方式)"""
    import time
    return render_template('chat_simple.html', cache_version=int(time.time()))


# API测试页面
@bp.route('/chat/test')
@login_required
def chat_test():
    """聊天API测试页面"""
    return render_template('chat_test.html')


# 手册查看路由
@bp.route('/manual')
@login_required
def user_manual():
    """根据用户角色显示相应的操作手册"""
    # 根据角色确定手册文件
    role_manual_map = {
        'user': '用户手册-普通员工.md',
        'department_head': '用户手册-部门主管.md',
        'technician': '用户手册-技术员.md',
        'admin': '用户手册-系统管理员.md'
    }
    
    manual_file = role_manual_map.get(current_user.role, '用户手册-普通员工.md')
    manual_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'docs', manual_file)
    
    try:
        with open(manual_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # 将Markdown转换为HTML
        html_content = markdown2.markdown(md_content, extras=['tables', 'fenced-code-blocks', 'header-ids'])
        
        # 获取角色名称
        role_names = {
            'user': '普通员工',
            'department_head': '部门主管',
            'technician': '技术员',
            'admin': '系统管理员'
        }
        role_name = role_names.get(current_user.role, '用户')
        
        return render_template('main/user_manual.html', 
                             content=html_content, 
                             role_name=role_name,
                             all_manuals=role_manual_map)
    except FileNotFoundError:
        flash('操作手册文件未找到', 'warning')
        return redirect(url_for('main.index'))
    except Exception as e:
        flash(f'读取手册时出错: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/manual/<role_type>')
@login_required
def view_manual(role_type):
    """查看指定角色的手册（仅管理员可查看所有）"""
    # 非管理员只能查看自己的手册
    if current_user.role != 'admin' and role_type != current_user.role:
        flash('您没有权限查看其他角色的手册', 'warning')
        return redirect(url_for('main.user_manual'))
    
    role_manual_map = {
        'user': '用户手册-普通员工.md',
        'department_head': '用户手册-部门主管.md',
        'technician': '用户手册-技术员.md',
        'admin': '用户手册-系统管理员.md'
    }
    
    manual_file = role_manual_map.get(role_type, '用户手册-普通员工.md')
    manual_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'docs', manual_file)
    
    try:
        with open(manual_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        html_content = markdown2.markdown(md_content, extras=['tables', 'fenced-code-blocks', 'header-ids'])
        
        role_names = {
            'user': '普通员工',
            'department_head': '部门主管',
            'technician': '技术员',
            'admin': '系统管理员'
        }
        role_name = role_names.get(role_type, '用户')
        
        return render_template('main/user_manual.html', 
                             content=html_content, 
                             role_name=role_name,
                             all_manuals=role_manual_map,
                             current_manual=role_type)
    except FileNotFoundError:
        flash('操作手册文件未找到', 'warning')
        return redirect(url_for('main.index'))
    except Exception as e:
        flash(f'读取手册时出错: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

# ------------------------- 通用辅助 -------------------------
STATUS_LABELS = {
    'equipment': {
        'active': '正常',
        'available': '可申请',
        'repair': '维修中',
        'loaned': '已借出',
        'retired': '已报废',
        'in_use': '使用中',
        'maintenance': '维护中',
        'scrapped': '已报废',
    },
    'repair_order': {
        'submitted': '已提交',
        'pending': '待处理',
        'department_head_approved': '部门已批',
        'admin_approved': '管理员已批',
        'in_progress': '处理中',
        'completed': '已完成',
        'cancelled': '已取消',
        'rejected': '已驳回',
    },
    'part_request': {
        'submitted': '已提交',
        'pending': '待处理',
        'department_head_approved': '部门已批',
        'admin_approved': '管理员已批',
        'completed': '已完成',
        'cancelled': '已取消',
        'rejected': '已驳回',
    },
    'transfer': {
        'submitted': '已提交',
        'pending': '待审批',
        'approved': '已批准',
        'rejected': '已驳回',
        'completed': '已完成',
        'cancelled': '已取消',
    },
    'scrap': {
        'submitted': '已提交',
        'pending': '待审批',
        'approved': '已批准',
        'rejected': '已驳回',
        'completed': '已完成',
        'cancelled': '已取消',
    },
    'loan': {
        'submitted': '待审批',
        'pending': '待审批',
        'approved': '已批准',
        'borrowed': '已借出',
        'returned': '已归还',
        'cancelled': '已取消',
        'rejected': '已驳回',
    },
    'approval': {
        'pending': '待审批',
        'approved': '已通过',
        'rejected': '已拒绝',
    },
}

DATE_INPUT_FORMATS = [
    '%Y-%m-%d',
    '%Y/%m/%d',
    '%Y.%m.%d',
    '%Y%m%d',
    '%Y-%m-%d %H:%M:%S',
    '%Y/%m/%d %H:%M:%S',
]


def _status_label(category, status):
    if not status:
        return ''
    return STATUS_LABELS.get(category, {}).get(status, status)


def _status_key(category, value):
    """将中文/英文展示值转换为系统内部状态值"""
    if not value:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    labels = STATUS_LABELS.get(category, {})
    for key, label in labels.items():
        if normalized == label or normalized.lower() == key.lower():
            return key
    return normalized


def _parse_flexible_date(value):
    """支持多种格式（YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD, YYYYMMDD）的日期解析"""
    if not value:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    normalized = (
        normalized.replace('年', '-')
        .replace('月', '-')
        .replace('日', '')
        .replace('.', '-')
    )
    for fmt in DATE_INPUT_FORMATS:
        try:
            dt = datetime.strptime(normalized, fmt)
            return dt.date()
        except ValueError:
            continue
    return None


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # 获取有效公告(最新3条)
    from app.models import Announcement
    announcements = Announcement.get_active_announcements(limit=3)
    
    # 获取当前用户的待处理事项数量
    pending_repairs = RepairOrder.query.filter_by(status='submitted').count()
    # 只统计真正需要当前用户审批的待审批事项
    pending_approvals = ApprovalWorkflow.query.filter_by(
        approver_id=current_user.id,
        status='pending'
    ).count()
    
    # 构建仪表盘卡片列表(后端构造更稳定,便于测试与调整顺序)
    tiles = []
    if current_user.role == 'admin':
        # 统一排序：按功能分类排列
        tiles.extend([
            # 第一组：账号和权限管理
            {'title':'账号申请','text':'查看待审批的账号申请','url': url_for('main.account_request_list')},
            {'title':'用户管理','text':'管理系统中的所有用户','url': url_for('main.user_management')},
            {'title':'权限管理','text':'管理自定义角色和权限','url': url_for('main.role_permission_management')},
            {'title':'部门管理','text':'管理系统中的所有部门','url': url_for('main.department_management')},
            {'title':'公开仓库','text':'查看和管理所有部门公开的设备和配件','url': url_for('main.public_pool'), 'class': 'border-success'},
            {'title':'审批流配置','text':'按工单类型配置审批流程','url': url_for('main.admin_workflow_nodes'), 'class': 'border-info'},
            
            # 第二组：资产和配件管理
            {'title':'资产/配件管理中心','text':'统一管理资产和配件，整合所有功能','url': url_for('main.asset_center')},
            {'title':'设备管理','text':'查看和管理 IT 设备','url': url_for('main.equipment_list')},
            {'title':'配件管理','text':'查看和管理配件库存','url': url_for('main.spare_parts')},
            {'title':'设备类型管理','text':'管理设备类型字典','url': url_for('main.equipment_types')},
            {'title':'配件类型管理','text':'管理配件类型字典','url': url_for('main.spare_part_types')},
            
            # 第三组：工单和申请管理
            {'title':'维修工单','text':'查看和管理维修工单','url': url_for('main.repair_orders')},
            {'title':'配件申请管理','text':'查看和管理配件申请','url': url_for('main.part_request_orders')},
            {'title':'发起设备调拨','text':'发起或管理设备调拨申请','url': url_for('main.create_transfer')},
            {'title':'发起设备报废','text':'发起或管理设备报废申请','url': url_for('main.create_scrap')},
            
            # 第四组：分析和报表
            {'title':'成本分析','text':'查看资产成本分析和成本预算','url': url_for('main.cost_analysis')},
            {'title':'库存预警','text':'查看库存不足预警和采购建议','url': url_for('main.inventory_warning')},
            {'title':'生命周期','text':'查看资产生命周期和报废分析','url': url_for('main.lifecycle_dashboard')},
            {'title':'报表统计','text':'查看各类统计报表','url': url_for('main.reports')},
            
            # 第五组：系统管理
            {'title':'系统公告','text':'发布和管理系统公告','url': url_for('main.admin_announcements'), 'class': 'border-primary'},
            {'title':'企业微信集成','text':'企业微信同步和配置','url': url_for('main.admin_wework'), 'class': 'border-success'},
            {'title':'操作日志','text':'查看用户操作日志','url': url_for('main.user_activity_logs')},
            {'title':'审批历史','text':'查看我的审批记录','url': url_for('main.approval_history')},
            {'title':'通知中心','text':'查看系统通知与消息','url': url_for('main.notifications')},
            {'title':'数据库管理','text':'备份、恢复、重置数据库','url': url_for('main.database_management')},
        ])
    elif current_user.role == 'technician':
        # 业务类（靠前）
        tiles.extend([
            {'title':'技术员工作台','text':'技术员专用仪表板','url': url_for('main.technician_dashboard')},
            {'title':'维修工单','text':'查看和管理维修工单','url': url_for('main.repair_orders')},
            {'title':'配件申请管理','text':'查看和管理配件申请','url': url_for('main.part_request_orders')},
            {'title':'设备管理','text':'查看和管理 IT 设备','url': url_for('main.equipment_list')},
            {'title':'配件管理','text':'查看和管理配件库存','url': url_for('main.spare_parts')},
            {'title':'设备申请','text':'申请可用设备','url': url_for('main.create_equipment_application')},
            {'title':'设备借用申请','text':'申请或管理设备借用','url': url_for('main.create_loan_request')},
            {'title':'我的借用','text':'查看我的借用记录','url': url_for('main.my_loans')},
            {'title':'发起设备调拨','text':'发起或管理设备调拨申请','url': url_for('main.create_transfer')},
            {'title':'发起设备报废','text':'发起或管理设备报废申请','url': url_for('main.create_scrap')},
            {'title':'公开仓库','text':'查看所有部门公开的设备和配件','url': url_for('main.public_pool'), 'class': 'border-success'},
        ])
        # 信息类（末行）
        tiles.extend([
            # 受授权的只读入口
            *([{'title':'报表统计','text':'查看各类统计报表','url': url_for('main.reports')}] if current_user.has_module_access('reports') else []),
            *([{'title':'操作日志','text':'查看用户操作日志','url': url_for('main.user_activity_logs')}] if current_user.has_module_access('logs') else []),
            {'title':'系统公告','text':'查看系统公告和通知','url': url_for('main.announcements'), 'class': 'border-primary'},
            {'title':'审批历史','text':'查看我的审批记录','url': url_for('main.approval_history')},
            {'title':'通知中心','text':'系统通知与提醒','url': url_for('main.notifications')}
        ])
    elif current_user.role == 'department_head':
        # 业务类（靠前）
        tiles.extend([
            {'title':'我的审批','text':'待处理审批','url': url_for('main.approvals')},
            {'title':'维修工单','text':'查看和管理维修工单','url': url_for('main.repair_orders')},
            {'title':'设备管理','text':'查看和管理 IT 设备','url': url_for('main.equipment_list')},
            {'title':'配件管理','text':'查看和管理配件库存','url': url_for('main.spare_parts')},
            {'title':'设备申请','text':'申请可用设备','url': url_for('main.create_equipment_application')},
            {'title':'设备借用申请','text':'申请或管理设备借用','url': url_for('main.create_loan_request')},
            {'title':'我的借用','text':'查看我的借用记录','url': url_for('main.my_loans')},
            {'title':'发起设备调拨','text':'发起或管理设备调拨申请','url': url_for('main.create_transfer')},
            {'title':'发起设备报废','text':'发起或管理设备报废申请','url': url_for('main.create_scrap')},
            {'title':'公开仓库','text':'查看所有部门公开的设备和配件','url': url_for('main.public_pool'), 'class': 'border-success'},
        ])
        # 信息类（末行）
        tiles.extend([
            *([{'title':'报表统计','text':'查看各类统计报表','url': url_for('main.reports')}] if current_user.has_module_access('reports') else []),
            *([{'title':'操作日志','text':'查看用户操作日志','url': url_for('main.user_activity_logs')}] if current_user.has_module_access('logs') else []),
            {'title':'系统公告','text':'查看系统公告和通知','url': url_for('main.announcements'), 'class': 'border-primary'},
            {'title':'审批历史','text':'查看我的审批记录','url': url_for('main.approval_history')},
            {'title':'通知中心','text':'系统通知与提醒','url': url_for('main.notifications')}
        ])
    else:  # 普通用户
        # 业务类（靠前）
        tiles.extend([
            {'title':'我的工单','text':'查看我提交的工单','url': url_for('main.repair_orders')},
            {'title':'提交维修申请','text':'提交维修工单','url': url_for('main.create_repair_order')},
            {'title':'提交配件申请','text':'提交配件申请','url': url_for('main.create_part_request_order')},
            {'title':'设备申请','text':'申请可用设备','url': url_for('main.create_equipment_application')},
            {'title':'设备借用申请','text':'申请或管理设备借用','url': url_for('main.create_loan_request')},
            {'title':'我的借用','text':'查看我的借用记录','url': url_for('main.my_loans')},
            {'title':'发起设备调拨','text':'发起或管理设备调拨申请','url': url_for('main.create_transfer')},
            {'title':'发起设备报废','text':'发起或管理设备报废申请','url': url_for('main.create_scrap')},
            {'title':'公开仓库','text':'查看所有部门公开的设备和配件','url': url_for('main.public_pool'), 'class': 'border-success'},
        ])
        # 可选模块访问
        if current_user.has_module_access('equipment'):
            tiles.append({'title':'设备管理','text':'查看和管理 IT 设备','url': url_for('main.equipment_list')})
        if current_user.has_module_access('spare_parts'):
            tiles.append({'title':'配件管理','text':'查看和管理配件库存','url': url_for('main.spare_parts')})
        # 信息类（末行）
        tiles.extend([
            *([{'title':'报表统计','text':'查看各类统计报表','url': url_for('main.reports')}] if current_user.has_module_access('reports') else []),
            *([{'title':'操作日志','text':'查看用户操作日志','url': url_for('main.user_activity_logs')}] if current_user.has_module_access('logs') else []),
            {'title':'系统公告','text':'查看系统公告和通知','url': url_for('main.announcements'), 'class': 'border-primary'},
            {'title':'审批历史','text':'查看我的审批记录','url': url_for('main.approval_history')},
            {'title':'通知中心','text':'系统通知与提醒','url': url_for('main.notifications')}
        ])
    
    # 智能添加审批历史:如果用户有任何审批记录但tiles中没有审批历史入口,自动添加
    has_approval_history_tile = any(tile.get('title') == '审批历史' for tile in tiles)
    if not has_approval_history_tile:
        # 检查用户是否有审批记录
        try:
            user_has_approvals = ApprovalWorkflow.query.filter_by(approver_id=current_user.id).first() is not None
            if user_has_approvals:
                # 在通知中心之前插入审批历史
                notification_index = next((i for i, tile in enumerate(tiles) if tile.get('title') == '通知中心'), None)
                if notification_index is not None:
                    tiles.insert(notification_index, {'title':'审批历史','text':'查看我的审批记录','url': url_for('main.approval_history')})
                else:
                    tiles.append({'title':'审批历史','text':'查看我的审批记录','url': url_for('main.approval_history')})
        except Exception:
            pass  # 数据库查询失败时忽略

    # 补充首页需要的设备统计数据（避免模板中缺少变量导致显示为0）
    try:
        total_equipment = Equipment.query.count()
        equipment_available = Equipment.query.filter_by(status='available').count()
        equipment_maintenance = Equipment.query.filter_by(status='repair').count()
        equipment_retired = Equipment.query.filter_by(status='retired').count()
    except Exception:
        # 在数据库为空或异常时回退为0，保持首页能正常渲染
        total_equipment = 0
        equipment_available = 0
        equipment_maintenance = 0
        equipment_retired = 0

    # 最近活动（取最新5条），非致命：若UserActivityLog不存在则回退为空列表
    try:
        # UserActivityLog 使用字段 `timestamp` 存储时间，之前误用 `created_date` 导致查询异常
        recent_activities = UserActivityLog.query.order_by(UserActivityLog.timestamp.desc()).limit(5).all()
    except Exception:
        recent_activities = []

    return render_template('main/index.html', 
                         title='首页',
                         pending_repairs=pending_repairs,
                         pending_approvals=pending_approvals,
                         tiles=tiles,
                         total_equipment=total_equipment,
                         equipment_available=equipment_available,
                         equipment_maintenance=equipment_maintenance,
                         equipment_retired=equipment_retired,
                         recent_activities=recent_activities,
                         announcements=announcements)


@bp.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    pending_account_requests = AccountRequest.query.filter_by(status='pending').count()
    
    # 优化后的管理面板卡片排序 - 按功能分类统一排列 (与首页保持一致)
    tiles = [
        # 第一组：账号和权限管理
        {'title':'账号申请','text':'查看待审批的账号申请','url': url_for('main.account_request_list')},
        {'title':'用户管理','text':'管理系统中的所有用户','url': url_for('main.user_management')},
        {'title':'权限管理','text':'管理自定义角色和权限','url': url_for('main.role_permission_management')},
        {'title':'部门管理','text':'管理系统中的所有部门','url': url_for('main.department_management')},
        {'title':'公开仓库','text':'查看和管理所有部门公开的设备和配件','url': url_for('main.public_pool'), 'class': 'border-success'},
        {'title':'审批流配置','text':'按工单类型配置审批流程','url': url_for('main.admin_workflow_nodes'), 'class': 'border-info'},
        
        # 第二组：资产和配件管理
        {'title':'资产/配件管理中心','text':'统一管理资产和配件，整合所有功能','url': url_for('main.asset_center')},
        {'title':'设备管理','text':'查看和管理 IT 设备','url': url_for('main.equipment_list')},
        {'title':'配件管理','text':'查看和管理配件库存','url': url_for('main.spare_parts')},
        {'title':'设备类型管理','text':'管理设备类型字典','url': url_for('main.equipment_types')},
        {'title':'配件类型管理','text':'管理配件类型字典','url': url_for('main.spare_part_types')},
        
        # 第三组：工单和申请管理
        {'title':'维修工单','text':'查看和管理维修工单','url': url_for('main.repair_orders')},
        {'title':'配件申请管理','text':'查看和管理配件申请','url': url_for('main.part_request_orders')},
        {'title':'发起设备调拨','text':'发起或管理设备调拨申请','url': url_for('main.create_transfer')},
        {'title':'发起设备报废','text':'发起或管理设备报废申请','url': url_for('main.create_scrap')},
        
        # 第四组：分析和报表
        {'title':'成本分析','text':'查看资产成本分析和成本预算','url': url_for('main.cost_analysis')},
        {'title':'库存预警','text':'查看库存不足预警和采购建议','url': url_for('main.inventory_warning')},
        {'title':'生命周期','text':'查看资产生命周期和报废分析','url': url_for('main.lifecycle_dashboard')},
        {'title':'报表统计','text':'查看各类统计报表','url': url_for('main.reports')},
        
        # 第五组：系统管理
        {'title':'系统公告','text':'发布和管理系统公告','url': url_for('main.admin_announcements'), 'class': 'border-primary'},
        {'title':'企业微信集成','text':'企业微信同步和配置','url': url_for('main.admin_wework'), 'class': 'border-success'},
        {'title':'操作日志','text':'查看用户操作日志','url': url_for('main.user_activity_logs')},
        {'title':'审批历史','text':'查看我的审批记录','url': url_for('main.approval_history')},
        {'title':'通知中心','text':'查看系统通知与消息','url': url_for('main.notifications')},
        {'title':'数据库管理','text':'备份、恢复、重置数据库','url': url_for('main.database_management')},
    ]

    return render_template('main/admin_dashboard.html', title='管理员仪表板', pending_account_requests=pending_account_requests, tiles=tiles)


@bp.route('/technician')
@login_required
def technician_dashboard():
    if current_user.role != 'technician':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    # 获取技术员相关的统计数据
    pending_repairs = RepairOrder.query.filter_by(status='submitted').count()
    in_progress_repairs = RepairOrder.query.filter_by(status='in_progress').count()
    
    # 本月已完成的工单
    from datetime import datetime
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    completed_repairs = RepairOrder.query.filter(
        RepairOrder.status == 'completed',
        RepairOrder.completed_date >= start_of_month
    ).count()
    
    return render_template('main/technician_dashboard.html', 
                         title='技术员仪表板',
                         pending_repairs=pending_repairs,
                         in_progress_repairs=in_progress_repairs,
                         completed_repairs=completed_repairs)


@bp.route('/admin/users')
@login_required
def user_management():
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    search_query = (request.args.get('search') or '').strip()
    department_id = request.args.get('department_id', type=int)
    role_filter = (request.args.get('role') or '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ADMIN_USERS_PER_PAGE', 12)
    
    query = User.query
    
    if department_id:
        query = query.filter(User.department_id == department_id)
    if role_filter:
        query = query.filter(User.role == role_filter)
    if search_query:
        like = f"%{search_query}%"
        query = query.filter(
            or_(
                User.username.ilike(like),
                User.email.ilike(like)
            )
        )
    
    pagination = query.order_by(User.id.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    users = pagination.items
    departments = Department.query.order_by(Department.name).all()
    return render_template(
        'main/user_management.html',
        title='用户管理',
        users=users,
        departments=departments,
        pagination=pagination,
        search_query=search_query,
        selected_department_id=department_id,
        role_filter=role_filter,
        per_page=per_page
    )


@bp.route('/account_requests')
@login_required
def account_request_list():
    if current_user.role != 'admin':
        flash('只有管理员可以查看账号申请')
        return redirect(url_for('main.index'))
    
    status = request.args.get('status', 'pending')
    search = (request.args.get('q') or '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ACCOUNT_REQUESTS_PER_PAGE', 12)
    
    query = AccountRequest.query
    if status != 'all':
        query = query.filter_by(status=status)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                AccountRequest.username.ilike(like),
                AccountRequest.full_name.ilike(like),
                AccountRequest.employee_no.ilike(like),
                AccountRequest.email.ilike(like)
            )
        )
    
    pagination = query.order_by(AccountRequest.created_date.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template(
        'main/account_request_list.html',
        title='账号申请列表',
        requests=pagination.items,
        pagination=pagination,
        status=status,
        search=search
    )


@bp.route('/account_requests/<int:id>', methods=['GET', 'POST'])
@login_required
def account_request_detail(id):
    if current_user.role != 'admin':
        flash('只有管理员可以审批账号申请')
        return redirect(url_for('main.index'))
    
    account_request = AccountRequest.query.get_or_404(id)
    # 角色选择仅保留管理员和普通用户，其他权限在权限管理模块中分配
    role_choices = [
        ('user', '普通用户'),
        ('admin', '管理员')
    ]
    
    if request.method == 'POST':
        action = request.form.get('action')
        comments = (request.form.get('comments') or '').strip()
        selected_role = request.form.get('role') or account_request.role_requested or 'user'
        
        if account_request.status != 'pending':
            flash('该申请已被处理')
            return redirect(url_for('main.account_request_detail', id=id))
        
        if action == 'approve':
            if User.query.filter_by(username=account_request.username).first():
                flash('审批失败：系统中已存在同名用户。')
                return redirect(url_for('main.account_request_detail', id=id))
            
            user = User(
                username=account_request.username,
                email=account_request.email,
                role=selected_role,
                department=account_request.department
            )
            dept = None
            if account_request.department:
                dept = Department.query.filter_by(name=account_request.department).first()
            if dept:
                user.department_id = dept.id
            user.password_hash = account_request.password_hash
            db.session.add(user)
            db.session.flush()
            
            account_request.status = 'approved'
            account_request.processed_date = get_beijing_now()
            account_request.approver_id = current_user.id
            account_request.approver_comments = comments
            
            note = Notification(
                user_id=user.id,
                title='账号已开通',
                message='管理员已经批准了您的账号申请，现在可以使用申请时设置的密码登录系统。'
            )
            db.session.add(note)
            db.session.commit()
            
            flash('申请已通过，账号已创建。')
            return redirect(url_for('main.account_request_detail', id=id))
        elif action == 'reject':
            account_request.status = 'rejected'
            account_request.processed_date = get_beijing_now()
            account_request.approver_id = current_user.id
            account_request.approver_comments = comments or '管理员已拒绝该申请'
            db.session.commit()
            flash('申请已拒绝。')
            return redirect(url_for('main.account_request_detail', id=id))
        else:
            flash('无效操作')
            return redirect(url_for('main.account_request_detail', id=id))
    
    return render_template(
        'main/account_request_detail.html',
        title='账号申请审批',
        account_request=account_request,
        role_choices=role_choices
    )


@bp.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': '您没有权限执行此操作'}), 403
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    departments = Department.query.all()
    
    if request.method == 'POST':
        payload = request.form or request.get_json(silent=True) or {}
        username = (payload.get('username') or '').strip()
        email = (payload.get('email') or '').strip()
        password = (payload.get('password') or '').strip()
        password2 = payload.get('password2')
        role = (payload.get('role') or '').strip()
        department_id_raw = payload.get('department_id')
        
        if not username or not email or not role or not department_id_raw:
            return jsonify({'success': False, 'message': '请完整填写用户信息'})
        
        if not password:
            return jsonify({'success': False, 'message': '密码不能为空'})
        
        if password2 is not None and password != password2:
            return jsonify({'success': False, 'message': '两次输入的密码不一致'})
        
        try:
            department_id = int(department_id_raw)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'message': '请选择有效的部门'})
        
        department = Department.query.get(department_id)
        if not department:
            return jsonify({'success': False, 'message': '请选择有效的部门'})
        
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': '该用户名已存在'})
            
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': '该邮箱已存在'})
            
        user = User(
            username=username,
            email=email,
            role=role,
            department_id=department.id,
            department=department.name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        _log_activity('创建用户', f'管理员 {current_user.username} 创建了用户 {user.username}')
        db.session.commit()
        
        return jsonify({'success': True, 'message': '用户添加成功'})
        
    return render_template('main/add_user.html', title='添加用户', departments=departments)


@bp.route('/admin/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '您没有权限执行此操作'}), 403
        
    user = User.query.get_or_404(id)
    departments = Department.query.all()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        department_id = request.form.get('department_id')
        
        # 检查用户名是否已存在（排除当前用户）
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({'success': False, 'message': '该用户名已存在'})
            
        # 检查邮箱是否已存在（排除当前用户）
        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.id != user.id:
            return jsonify({'success': False, 'message': '该邮箱已存在'})
            
        # 获取部门信息
        department = Department.query.get(department_id)
        if not department:
            return jsonify({'success': False, 'message': '请选择有效的部门'})
            
        user.username = username
        user.email = email
        user.role = role
        user.department_id = department_id
        user.department = department.name
        
        db.session.commit()
        
        # 记录用户编辑活动
        _log_activity('编辑用户', f'管理员 {current_user.username} 编辑了用户 {user.username}')
        db.session.commit()
        
        return jsonify({'success': True, 'message': '用户信息更新成功'})
        
    return render_template('main/edit_user.html', title='编辑用户', user=user, departments=departments)


@bp.route('/repair_orders')
@login_required
def repair_orders():
    # 获取筛选参数
    filter_type = request.args.get('filter', 'all')
    
    # 根据用户角色和筛选条件确定查询条件
    query = RepairOrder.query
    
    # 用户角色过滤
    # admin可以查看所有维修单
    # 普通用户可以看：1) 自己提交的工单 2) 需要自己审批的工单
    if current_user.role == 'user':
        # 获取需要当前用户审批的工单ID列表
        pending_approval_order_ids = db.session.query(ApprovalWorkflow.order_id).filter(
            ApprovalWorkflow.order_type == 'repair_order',
            ApprovalWorkflow.approver_id == current_user.id,
            ApprovalWorkflow.status == 'pending'
        ).distinct().all()
        pending_ids = [oid[0] for oid in pending_approval_order_ids]
        
        # 查询条件：自己创建的 OR 需要自己审批的
        from sqlalchemy import or_
        query = query.filter(
            or_(
                RepairOrder.requester_id == current_user.id,
                RepairOrder.id.in_(pending_ids) if pending_ids else False
            )
        )
    
    # 状态筛选
    if filter_type != 'all':
        query = query.filter_by(status=filter_type)
    
    orders = query.all()
    
    # 如果是Ajax请求，只返回表格部分
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('main/repair_orders_table.html', orders=orders)
    
    return render_template('main/repair_orders.html', title='维修工单', orders=orders)


@bp.route('/admin/users/export')
@login_required
def export_users():
    """导出用户数据为CSV格式（支持筛选）"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    # 获取筛选参数
    role = request.args.get('role', '').strip()
    department_id = request.args.get('department_id', type=int)
    
    # 构建查询
    query = User.query
    
    if role:
        query = query.filter_by(role=role)
    if department_id:
        query = query.filter_by(department_id=department_id)
    
    users = query.all()
    
    # 创建CSV数据
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow(['用户名', '邮箱', '角色', '所属部门', '设备管理', '配件管理', '维修工单', '配件申请'])
    
    # 写入数据
    for user in users:
        writer.writerow([
            user.username,
            user.email,
            user.role,
            user.department or '',
            '是' if user.can_manage_equipment else '否',
            '是' if user.can_manage_spare_parts else '否',
            '是' if user.can_manage_repairs else '否',
            '是' if user.can_manage_part_requests else '否'
        ])
    
    # 返回CSV文件
    from flask import Response
    csv_data = output.getvalue()
    output.close()
    
    filename = f'用户数据_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': content_disposition(filename, 'users.csv')}
    )


@bp.route('/admin/users/import', methods=['POST'])
@login_required
def import_users():
    """从CSV文件导入用户数据"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '请选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '请选择文件'}), 400
    
    if file and file.filename.endswith('.csv'):
        try:
            import csv
            import io
            raw = file.stream.read()
            text = None
            for enc in ('utf-8', 'utf-8-sig', 'gbk'):
                try:
                    text = raw.decode(enc)
                    break
                except Exception:
                    continue
            if text is None:
                raise Exception('文件编码不支持，请使用 UTF-8 或 GBK')
            stream = io.StringIO(text)
            reader = csv.reader(stream)
            # 跳过表头
            try:
                next(reader)
            except StopIteration:
                pass
            
            # 导入数据
            imported_count = 0
            for row in reader:
                if len(row) >= 4:
                    username = (row[0] or '').strip()
                    email = (row[1] or '').strip()
                    role = (row[2] or '').strip() or 'user'
                    department = (row[3] or '').strip()
                    if not username or not email:
                        continue
                    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
                        continue
                    user = User(username=username, email=email, role=role, department=department)
                    user.set_password('123456')
                    db.session.add(user)
                    imported_count += 1
            
            db.session.commit()
            return jsonify({'success': True, 'message': f'成功导入 {imported_count} 个用户'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'导入失败: {str(e)}'}), 500
    else:
        return jsonify({'success': False, 'message': '请上传CSV文件'}), 400


@bp.route('/admin/users/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
        
    user = User.query.get_or_404(id)
    
    # 禁止删除自己
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': '不能删除当前登录用户'}), 400
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '用户删除成功'})


@bp.route('/admin/departments')
@login_required
def department_management():
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    search_query = (request.args.get('search') or '').strip()
    location_filter = (request.args.get('location') or '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('DEPARTMENT_PER_PAGE', 12)
    
    query = Department.query
    if search_query:
        like = f"%{search_query}%"
        query = query.filter(
            or_(
                Department.name.ilike(like),
                Department.code.ilike(like),
                Department.cost_center.ilike(like)
            )
        )
    if location_filter:
        query = query.filter(Department.location.ilike(f"%{location_filter}%"))
    
    pagination = query.order_by(Department.name).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    dept_list = []
    for dept in pagination.items:
        user_count = User.query.filter_by(department_id=dept.id).count()
        dept_list.append({
            'id': dept.id,
            'name': dept.name,
            'code': dept.code,
            'cost_center': dept.cost_center,
            'location': dept.location,
            'description': dept.description,
            'user_count': user_count
        })
    
    location_options = [
        loc[0] for loc in Department.query.with_entities(Department.location)
        .filter(Department.location.isnot(None), Department.location != '')
        .distinct()
        .order_by(Department.location)
        .all()
    ]
    
    _log_activity('访问页面', '部门管理')
    return render_template(
        'main/department_management.html',
        title='部门管理',
        departments=dept_list,
        pagination=pagination,
        search_query=search_query,
        location_filter=location_filter,
        location_options=location_options,
        per_page=per_page
    )


@bp.route('/admin/departments/export')
@login_required
def export_departments():
    """导出部门数据为CSV格式"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    # 创建CSV数据
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow(['部门名称', '部门代码', '成本中心', '位置', '描述'])
    
    # 写入数据
    departments = Department.query.all()
    for dept in departments:
        writer.writerow([
            dept.name,
            dept.code,
            dept.cost_center,
            dept.location,
            dept.description
        ])
    
    # 返回CSV文件
    from flask import Response
    csv_data = output.getvalue()
    output.close()
    
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': content_disposition('部门数据.csv', 'departments.csv')}
    )


@bp.route('/admin/departments/import', methods=['POST'])
@login_required
def import_departments():
    """从CSV文件导入部门数据"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '请选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '请选择文件'}), 400
    
    if file and file.filename.endswith('.csv'):
        try:
            import csv
            import io
            raw = file.stream.read()
            text = None
            for enc in ('utf-8', 'utf-8-sig', 'gbk'):
                try:
                    text = raw.decode(enc)
                    break
                except Exception:
                    continue
            if text is None:
                raise Exception('文件编码不支持，请使用 UTF-8 或 GBK')
            stream = io.StringIO(text)
            reader = csv.reader(stream)
            # 跳过表头
            try:
                next(reader)
            except StopIteration:
                pass
            
            # 导入数据
            imported_count = 0
            for row in reader:
                if len(row) >= 5:
                    name = (row[0] or '').strip()
                    code = (row[1] or '').strip()
                    cost_center = (row[2] or '').strip()
                    location = (row[3] or '').strip()
                    description = (row[4] or '').strip()
                    if not name or not code:
                        continue
                    if Department.query.filter_by(name=name).first() or Department.query.filter_by(code=code).first():
                        continue
                    dept = Department(name=name, code=code, cost_center=cost_center, location=location, description=description)
                    db.session.add(dept)
                    imported_count += 1
            
            db.session.commit()
            return jsonify({'success': True, 'message': f'成功导入 {imported_count} 个部门'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'导入失败: {str(e)}'}), 500
    else:
        return jsonify({'success': False, 'message': '请上传CSV文件'}), 400


@bp.route('/admin/department/<int:dept_id>/users')
@login_required
def department_users(dept_id):
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    department = Department.query.get_or_404(dept_id)
    users = User.query.filter_by(department_id=dept_id).all()
    
    return render_template('main/department_users.html', 
                         title=f'{department.name} - 部门用户',
                         department=department,
                         users=users)


@bp.route('/admin/departments/add', methods=['POST'])
@login_required
def add_department():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    name = request.form.get('name')
    code = request.form.get('code')
    cost_center = request.form.get('cost_center')
    location = request.form.get('location')
    description = request.form.get('description')
    
    # 验证必填字段
    if not name or not code:
        return jsonify({'success': False, 'message': '部门名称和部门代码为必填项'})
    
    # 检查部门名称是否已存在
    if Department.query.filter_by(name=name).first():
        return jsonify({'success': False, 'message': '该部门名称已存在'})
    
    # 检查部门代码是否已存在
    if Department.query.filter_by(code=code).first():
        return jsonify({'success': False, 'message': '该部门代码已存在'})
    
    # 创建新部门
    department = Department(
        name=name,
        code=code,
        cost_center=cost_center,
        location=location,
        description=description
    )
    
    db.session.add(department)
    db.session.commit()
    _log_activity('添加部门', f'添加部门 {name}')
    
    return jsonify({'success': True, 'message': '部门添加成功'})


@bp.route('/admin/departments/update', methods=['POST'])
@login_required
def update_department():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    department_id = request.form.get('department_id')
    name = request.form.get('name')
    code = request.form.get('code')
    cost_center = request.form.get('cost_center')
    location = request.form.get('location')
    description = request.form.get('description')
    
    # 获取部门
    department = Department.query.get(department_id)
    if not department:
        return jsonify({'success': False, 'message': '部门不存在'})
    
    # 检查部门名称是否已存在（排除当前部门）
    existing_dept = Department.query.filter_by(name=name).first()
    if existing_dept and existing_dept.id != int(department_id):
        return jsonify({'success': False, 'message': '该部门名称已存在'})
    
    # 检查部门代码是否已存在（排除当前部门）
    existing_code = Department.query.filter_by(code=code).first()
    if existing_code and existing_code.id != int(department_id):
        return jsonify({'success': False, 'message': '该部门代码已存在'})
    
    # 更新部门信息
    department.name = name
    department.code = code
    department.cost_center = cost_center
    department.location = location
    department.description = description
    
    old_name = department.name
    db.session.commit()
    try:
        User.query.filter((User.department_id == department.id) | (User.department == old_name)).update({User.department: name}, synchronize_session=False)
        Equipment.query.filter((Equipment.department_id == department.id) | (Equipment.department == old_name)).update({Equipment.department: name}, synchronize_session=False)
        SparePart.query.filter(SparePart.department == old_name).update({SparePart.department: name}, synchronize_session=False)
        db.session.commit()
    except Exception:
        db.session.rollback()
    _log_activity('更新部门', f'更新部门 {old_name} -> {name}')
    
    return jsonify({'success': True, 'message': '部门信息更新成功'})


@bp.route('/admin/departments/<int:id>/update', methods=['POST'])
@login_required
def update_department_by_id(id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    department_id = id
    name = request.form.get('name')
    code = request.form.get('code')
    cost_center = request.form.get('cost_center')
    location = request.form.get('location')
    description = request.form.get('description')

    department = Department.query.get(department_id)
    if not department:
        return jsonify({'success': False, 'message': '部门不存在'})

    existing_dept = Department.query.filter_by(name=name).first()
    if existing_dept and existing_dept.id != int(department_id):
        return jsonify({'success': False, 'message': '该部门名称已存在'})

    existing_code = Department.query.filter_by(code=code).first()
    if existing_code and existing_code.id != int(department_id):
        return jsonify({'success': False, 'message': '该部门代码已存在'})

    old_name = department.name
    department.name = name
    department.code = code
    department.cost_center = cost_center
    department.location = location
    department.description = description

    db.session.commit()
    try:
        User.query.filter((User.department_id == department.id) | (User.department == old_name)).update({User.department: name}, synchronize_session=False)
        Equipment.query.filter((Equipment.department_id == department.id) | (Equipment.department == old_name)).update({Equipment.department: name}, synchronize_session=False)
        SparePart.query.filter(SparePart.department == old_name).update({SparePart.department: name}, synchronize_session=False)
        db.session.commit()
    except Exception:
        db.session.rollback()
    _log_activity('更新部门', f'更新部门 {old_name} -> {name}')
    return jsonify({'success': True, 'message': '部门信息更新成功'})

@bp.route('/admin/departments/delete/<int:id>', methods=['POST'])
@login_required
def delete_department(id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    department = Department.query.get_or_404(id)
    
    # 检查是否有用户属于这个部门
    user_count = User.query.filter_by(department=department.name).count()
    if user_count > 0:
        return jsonify({'success': False, 'message': '该部门下还有员工，无法删除'})
    
    # 检查是否有设备属于这个部门
    equipment_count = Equipment.query.filter_by(department=department.name).count()
    if equipment_count > 0:
        return jsonify({'success': False, 'message': '该部门下还有设备，无法删除'})
    
    db.session.delete(department)
    db.session.commit()
    _log_activity('删除部门', f'删除部门 {department.name}')
    
    return jsonify({'success': True, 'message': '部门删除成功'})


@bp.route('/equipment')
@login_required
def equipment_list():
    equipment_types = EquipmentType.query.all()
    departments = Department.query.order_by(Department.name).all()
    
    type_id = request.args.get('type_id', type=int)
    department_id = request.args.get('department_id', type=int)
    status_filter = request.args.get('status', '').strip()
    search_query = (request.args.get('search') or '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('EQUIPMENT_PER_PAGE', 10)
    
    query = Equipment.query
    
    # admin可以查看所有部门，其他用户只能查看本部门
    if current_user.role != 'admin' and current_user.department:
        query = query.filter(Equipment.department == current_user.department)
    
    if type_id:
        query = query.filter(Equipment.type_id == type_id)
    
    selected_department_name = None
    if department_id:
        department = Department.query.get(department_id)
        if department:
            selected_department_name = department.name
            query = query.filter(
                or_(
                    Equipment.department_id == department.id,
                    Equipment.department == department.name
                )
            )
    
    if status_filter:
        query = query.filter(Equipment.status == status_filter)
    
    if search_query:
        like = f"%{search_query}%"
        query = query.filter(
            or_(
                Equipment.name.ilike(like),
                Equipment.brand.ilike(like),
                Equipment.model.ilike(like),
                Equipment.serial_number.ilike(like)
            )
        )
    
    pagination = query.order_by(Equipment.id.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    equipments = pagination.items
    
    from app.models import EquipmentLoan
    equipment_loan_status = {}
    for equipment in equipments:
        active_loan = EquipmentLoan.query.filter_by(
            equipment_id=equipment.id
        ).filter(
            EquipmentLoan.status.in_(['borrowed', 'approved'])
        ).order_by(EquipmentLoan.created_date.desc()).first()
        
        if active_loan:
            if active_loan.status == 'borrowed':
                equipment_loan_status[equipment.id] = {
                    'status': 'borrowed',
                    'text': '已借出',
                    'requester': active_loan.requester.username if active_loan.requester else '未知',
                    'start_date': active_loan.start_date,
                    'end_date': active_loan.end_date
                }
            elif active_loan.status == 'approved':
                equipment_loan_status[equipment.id] = {
                    'status': 'approved',
                    'text': '已批准待借出',
                    'requester': active_loan.requester.username if active_loan.requester else '未知'
                }
        else:
            returned_loan = EquipmentLoan.query.filter_by(
                equipment_id=equipment.id,
                status='returned'
            ).order_by(EquipmentLoan.returned_date.desc()).first()
            
            if returned_loan:
                equipment_loan_status[equipment.id] = {
                    'status': 'returned',
                    'text': '已归还',
                    'returned_date': returned_loan.returned_date
                }
            else:
                equipment_loan_status[equipment.id] = {
                    'status': 'available',
                    'text': '可借用'
                }
        
    _log_activity('访问页面', '设备列表')
    return render_template(
        'main/equipment_list.html',
                         title='设备列表', 
                         equipments=equipments,
                         equipment_types=equipment_types,
        departments=departments,
        selected_type_id=type_id,
        selected_department_id=department_id,
        selected_department_name=selected_department_name,
        selected_status=status_filter,
        search_query=search_query,
        pagination=pagination,
        per_page=per_page,
        equipment_loan_status=equipment_loan_status
    )


@bp.route('/equipment/public')
@login_required
def public_equipment():
    type_id = request.args.get('type_id', type=int)
    status_filter = (request.args.get('status') or '').strip()
    search_query = (request.args.get('search') or '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('EQUIPMENT_PER_PAGE', 10)
    # 初始化查询：仅显示公开池（public pool）设备
    query = Equipment.query.filter_by(is_public_pool=True)
    # 筛选设备类型（可选）
    if type_id:
        query = query.filter(Equipment.type_id == type_id)
    # 按状态筛选（仅在提供状态字符串时）
    if status_filter:
        query = query.filter(Equipment.status == status_filter)
    if search_query:
        like = f"%{search_query}%"
        query = query.filter(
            or_(
                Equipment.name.ilike(like),
                Equipment.brand.ilike(like),
                Equipment.model.ilike(like),
                Equipment.serial_number.ilike(like)
            )
        )
    
    pagination = query.order_by(Equipment.id.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    equipments = pagination.items
    
    from app.models import EquipmentLoan
    equipment_loan_status = {}
    for equipment in equipments:
        active_loan = EquipmentLoan.query.filter_by(
            equipment_id=equipment.id
        ).filter(
            EquipmentLoan.status.in_(['borrowed', 'approved'])
        ).order_by(EquipmentLoan.created_date.desc()).first()
        
        if active_loan:
            if active_loan.status == 'borrowed':
                equipment_loan_status[equipment.id] = {
                    'status': 'borrowed',
                    'text': '已借出',
                    'requester': active_loan.requester.username if active_loan.requester else '未知',
                    'start_date': active_loan.start_date,
                    'end_date': active_loan.end_date
                }
            elif active_loan.status == 'approved':
                equipment_loan_status[equipment.id] = {
                    'status': 'approved',
                    'text': '已批准待借出',
                    'requester': active_loan.requester.username if active_loan.requester else '未知'
                }
        else:
            returned_loan = EquipmentLoan.query.filter_by(
                equipment_id=equipment.id,
                status='returned'
            ).order_by(EquipmentLoan.returned_date.desc()).first()
            
            if returned_loan:
                equipment_loan_status[equipment.id] = {
                    'status': 'returned',
                    'text': '已归还',
                    'returned_date': returned_loan.returned_date
                }
            else:
                equipment_loan_status[equipment.id] = {
                    'status': 'available',
                    'text': '可借用'
                }
    
    equipment_types = EquipmentType.query.all()
    departments = Department.query.order_by(Department.name).all()
    _log_activity('访问页面', '公开设备仓库')
    return render_template(
        'main/equipment_list.html',
        title='信息部公开设备仓库',
        equipments=equipments,
        equipment_types=equipment_types,
        departments=departments,
        selected_type_id=type_id,
        selected_department_id=None,
        selected_status=status_filter,
        search_query=search_query,
        pagination=pagination,
        per_page=per_page,
        equipment_loan_status=equipment_loan_status,
        public_only=True
    )


@bp.route('/public_pool')
@login_required
def public_pool():
    """公开仓库 - 显示所有部门公开的设备和配件"""
    # 获取筛选参数
    resource_type = request.args.get('type', 'equipment')  # equipment 或 spare_part
    department_id = request.args.get('department_id', type=int)
    search_query = (request.args.get('search') or '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('PUBLIC_POOL_PER_PAGE', 15)
    
    if resource_type == 'spare_part':
        # 查询公开的配件 (使用 is_public 字段)
        query = SparePart.query.filter_by(is_public=True)
        
        if department_id:
            query = query.filter(SparePart.department_id == department_id)
        
        if search_query:
            like = f"%{search_query}%"
            query = query.filter(
                or_(
                    SparePart.name.ilike(like),
                    SparePart.part_number.ilike(like),
                    SparePart.location.ilike(like)
                )
            )
        
        pagination = query.order_by(SparePart.name.asc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        items = pagination.items
        item_type = 'spare_part'
    else:
        # 查询公开的设备 (使用 is_public_pool 字段)
        query = Equipment.query.filter_by(is_public_pool=True)
        
        if department_id:
            query = query.filter(Equipment.department_id == department_id)
        
        if search_query:
            like = f"%{search_query}%"
            query = query.filter(
                or_(
                    Equipment.name.ilike(like),
                    Equipment.brand.ilike(like),
                    Equipment.model.ilike(like),
                    Equipment.serial_number.ilike(like)
                )
            )
        
        pagination = query.order_by(Equipment.id.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        items = pagination.items
        item_type = 'equipment'
    
    departments = Department.query.order_by(Department.name).all()
    
    # 统计数据
    total_public_equipment = Equipment.query.filter_by(is_public_pool=True).count()
    total_public_spare_parts = SparePart.query.filter_by(is_public=True).count()
    
    _log_activity('访问页面', '公开仓库')
    
    return render_template(
        'main/public_pool.html',
        title='公开仓库',
        items=items,
        item_type=item_type,
        departments=departments,
        selected_department_id=department_id,
        search_query=search_query,
        pagination=pagination,
        per_page=per_page,
        resource_type=resource_type,
        total_public_equipment=total_public_equipment,
        total_public_spare_parts=total_public_spare_parts
    )


@bp.route('/equipment/add', methods=['GET', 'POST'])
@login_required
def add_equipment():
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限添加设备')
        return redirect(url_for('main.equipment_list'))
        
    # 获取所有部门和设备类型
    departments = Department.query.all()
    equipment_types = EquipmentType.query.all()
        
    if request.method == 'POST':
        name = request.form.get('name')
        type_id = request.form.get('type_id', type=int)
        brand = request.form.get('brand')
        model = request.form.get('model')
        serial_number = request.form.get('serial_number')
        purchase_date_raw = (request.form.get('purchase_date') or '').strip()
        price_raw = (request.form.get('price') or '').strip()
        department_id = request.form.get('department_id')
        location = request.form.get('location', '').strip()
        
        # 验证必填字段
        if not name or not type_id or not serial_number or not department_id:
            flash('请填写所有必填字段')
            return render_template('main/add_equipment.html', 
                                 title='添加设备', 
                                 departments=departments,
                                 equipment_types=equipment_types)
        
        # 检查序列号是否已存在
        if Equipment.query.filter_by(serial_number=serial_number).first():
            flash('该序列号已存在')
            return render_template('main/add_equipment.html', 
                                 title='添加设备', 
                                 departments=departments,
                                 equipment_types=equipment_types)
        
        # 获取部门信息
        department = Department.query.get(department_id)
        if not department:
            flash('请选择有效的部门')
            return render_template('main/add_equipment.html', 
                                 title='添加设备', 
                                 departments=departments,
                                 equipment_types=equipment_types)
        
        # 获取设备类型信息
        equipment_type = EquipmentType.query.get(type_id)
        if not equipment_type:
            flash('请选择有效的设备类型')
            return render_template('main/add_equipment.html', 
                                 title='添加设备', 
                                 departments=departments,
                                 equipment_types=equipment_types)
        
        # 处理购买日期
        purchase_date = None
        if purchase_date_raw:
            purchase_date = _parse_flexible_date(purchase_date_raw)
            if not purchase_date:
                flash('购买日期格式不正确，请使用 YYYY-MM-DD')
                return render_template('main/add_equipment.html', 
                                     title='添加设备', 
                                     departments=departments,
                                     equipment_types=equipment_types)
        
        # 创建新设备
        # 处理 price 字段（允许为空，默认 0.0）
        try:
            price_val = float(price_raw) if price_raw != '' else 0.0
        except Exception:
            price_val = 0.0

        equipment = Equipment(
            name=name,
            type_id=type_id,
            type=equipment_type.name,  # 兼容旧字段
            brand=brand,
            model=model,
            serial_number=serial_number,
            purchase_date=purchase_date,
            price=price_val,
            department_id=department_id,
            department=department.name,
            location=location if location else None
        )
        
        db.session.add(equipment)
        db.session.commit()
        _log_activity('添加设备', f'添加设备 {equipment.name}#{equipment.id}')
        
        flash('设备添加成功')
        return redirect(url_for('main.equipment_list'))
        
    return render_template('main/add_equipment.html', 
                         title='添加设备', 
                         departments=departments,
                         equipment_types=equipment_types)


@bp.route('/equipment/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_equipment(id):
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限编辑设备')
        return redirect(url_for('main.equipment_list'))
        
    equipment = Equipment.query.get_or_404(id)
    
    # 获取所有部门和设备类型
    departments = Department.query.all()
    equipment_types = EquipmentType.query.all()
    # 关联摘要（避免删除时懒加载）
    apps_count = EquipmentApplication.query.filter_by(equipment_id=equipment.id).count()
    loans_count = EquipmentLoan.query.filter_by(equipment_id=equipment.id).count()
    transfers_count = EquipmentTransfer.query.filter_by(equipment_id=equipment.id).count()
    
    if request.method == 'POST':
        name = request.form.get('name')
        type_id = request.form.get('type_id', type=int)
        brand = request.form.get('brand')
        model = request.form.get('model')
        serial_number = request.form.get('serial_number')
        purchase_date_raw = (request.form.get('purchase_date') or '').strip()
        department_id = request.form.get('department_id')
        location = request.form.get('location', '').strip()
        status = request.form.get('status')
        is_public_pool = request.form.get('is_public_pool') == 'on'
        
        # 验证必填字段
        if not name or not type_id or not serial_number or not department_id:
            flash('请填写所有必填字段')
            return render_template('main/edit_equipment.html', 
                                 title='编辑设备', 
                                 equipment=equipment,
                                 departments=departments,
                                 equipment_types=equipment_types)
        
        # 检查序列号是否已被其他设备使用
        existing_equipment = Equipment.query.filter_by(serial_number=serial_number).first()
        if existing_equipment and existing_equipment.id != id:
            flash('该序列号已被其他设备使用')
            return render_template('main/edit_equipment.html', 
                                 title='编辑设备', 
                                 equipment=equipment,
                                 departments=departments,
                                 equipment_types=equipment_types)
        
        # 获取部门信息
        department = Department.query.get(department_id)
        if not department:
            flash('请选择有效的部门')
            return render_template('main/edit_equipment.html', 
                                 title='编辑设备', 
                                 equipment=equipment,
                                 departments=departments,
                                 equipment_types=equipment_types)
        
        # 获取设备类型信息
        equipment_type = EquipmentType.query.get(type_id)
        if not equipment_type:
            flash('请选择有效的设备类型')
            return render_template('main/edit_equipment.html', 
                                 title='编辑设备', 
                                 equipment=equipment,
                                 departments=departments,
                                 equipment_types=equipment_types)
        
        # 处理购买日期
        purchase_date = None
        if purchase_date_raw:
            purchase_date = _parse_flexible_date(purchase_date_raw)
            if not purchase_date:
                flash('购买日期格式不正确，请使用 YYYY-MM-DD')
                return render_template('main/edit_equipment.html', 
                                     title='编辑设备', 
                                     equipment=equipment,
                                     departments=departments,
                                     equipment_types=equipment_types)
        price_raw = (request.form.get('price') or '').strip()
        
        # 更新设备信息
        equipment.name = name
        equipment.type_id = type_id
        equipment.type = equipment_type.name  # 兼容旧字段
        equipment.brand = brand
        equipment.model = model
        equipment.serial_number = serial_number
        equipment.purchase_date = purchase_date
        equipment.department_id = department_id
        equipment.department = department.name
        equipment.location = location if location else None
        equipment.status = status
        equipment.is_public_pool = is_public_pool
        # 处理并保存 price 字段
        try:
            equipment.price = float(price_raw) if price_raw != '' else 0.0
        except Exception:
            equipment.price = 0.0
        
        db.session.commit()
        _log_activity('更新设备', f'更新设备 {equipment.name}#{equipment.id}')
        
        flash('设备信息更新成功')
        return redirect(url_for('main.equipment_list'))
        
    return render_template('main/edit_equipment.html', title='编辑设备', equipment=equipment, departments=departments, equipment_types=equipment_types, apps_count=apps_count, loans_count=loans_count, transfers_count=transfers_count)


@bp.route('/equipment/delete/<int:id>', methods=['POST'])
@login_required
def delete_equipment(id):
    if current_user.role not in ['admin']:
        return jsonify({'success': False, 'message': '权限不足'}), 403
        
    equipment = Equipment.query.get_or_404(id)
    equipment_name = equipment.name
    serial_number = equipment.serial_number
    
    db.session.delete(equipment)
    db.session.commit()
    _log_activity('删除设备', f'删除设备 {equipment_name} SN:{serial_number}')
    
    return jsonify({'success': True, 'message': '设备删除成功'})


@bp.route('/equipment/import', methods=['POST'])
@login_required
def import_equipment():
    """从CSV文件导入设备数据"""
    if current_user.role not in ['admin', 'technician']:
        return jsonify({'success': False, 'message': '权限不足'}), 403

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '请选择文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '请选择文件'}), 400

    if file and file.filename.endswith('.csv'):
        try:
            import csv
            import io
            raw = file.stream.read()
            text = None
            for enc in ('utf-8', 'utf-8-sig', 'gbk'):
                try:
                    text = raw.decode(enc)
                    break
                except Exception:
                    continue
            if text is None:
                raise Exception('文件编码不支持，请使用 UTF-8 或 GBK')
            stream = io.StringIO(text)
            # 先读取第一行判断是否为表头（包含中文/英文列名）
            reader = csv.reader(stream)
            try:
                first_row = next(reader)
            except StopIteration:
                first_row = []

            # 定义可能的列名集合（中英混合）
            name_keys = {'名称', '设备名称', 'name'}
            type_keys = {'类型', 'type', '设备类型'}
            brand_keys = {'品牌', 'brand'}
            model_keys = {'型号', 'model'}
            serial_keys = {'序列号', 'serial', 'serial_number', 'SN'}
            dept_keys = {'所属部门', '部门', 'department'}
            price_keys = {'价格', 'price'}
            purchase_keys = {'购买日期', 'purchase_date', 'purchase date', 'purchaseDate'}
            status_keys = {'状态', 'status'}

            # 如果第一行包含已知列名，使用 DictReader；否则回退到位置解析（保持向后兼容）
            use_dict = any(cell.strip() in (name_keys | type_keys | brand_keys | model_keys | serial_keys | purchase_keys | price_keys) for cell in first_row)

            imported_count = 0
            skipped = 0

            if use_dict:
                # 重建 StringIO 并使用 DictReader
                stream.seek(0)
                dict_reader = csv.DictReader(stream)
                for row in dict_reader:
                    if not row:
                        continue
                    def pick(*keys):
                        for k in keys:
                            if k in row and row[k] is not None:
                                v = row[k].strip()
                                if v != '':
                                    return v
                        return None

                    name = pick('名称', '设备名称', 'name') or ''
                    type_name = pick('类型', 'type', '设备类型') or ''
                    brand = pick('品牌', 'brand')
                    model = pick('型号', 'model')
                    serial_number = pick('序列号', 'serial', 'serial_number', 'SN') or ''
                    department = pick('所属部门', '部门', 'department') or current_user.department
                    status_raw = pick('状态', 'status') or ''

                    price_raw = pick('价格', 'price')
                    try:
                        price_val = float(price_raw) if price_raw else None
                    except Exception:
                        price_val = None

                    purchase_raw = pick('购买日期', 'purchase_date', 'purchase date', 'purchaseDate')
                    purchase_date = _parse_flexible_date(purchase_raw) if purchase_raw else None

                    if not name or not serial_number:
                        # 名称或序列号缺失则跳过
                        continue

                    # 跳过已有的序列号
                    if Equipment.query.filter_by(serial_number=serial_number).first():
                        skipped += 1
                        continue

                    equipment_type = EquipmentType.query.filter_by(name=type_name).first() if type_name else None
                    type_id = equipment_type.id if equipment_type else None
                    department_obj = Department.query.filter_by(name=department).first() if department else None
                    department_id = department_obj.id if department_obj else None

                    equipment = Equipment(
                        name=name,
                        type_id=type_id,
                        type=type_name if type_name else None,
                        brand=brand,
                        model=model,
                        serial_number=serial_number,
                        purchase_date=purchase_date,
                        department=department,
                        department_id=department_id,
                        status=_status_key('equipment', status_raw) or 'active'
                    )
                    # 如果 price 存在且可解析则保存
                    if price_val is not None:
                        try:
                            equipment.price = float(price_val)
                        except Exception:
                            pass

                    db.session.add(equipment)
                    imported_count += 1
            else:
                # 回退到原有的按列位置解析逻辑
                # 已经读取了第一行，且它不是表头，因此把它当作数据行处理
                all_rows = [first_row] + list(reader) if first_row else list(reader)
                for row in all_rows:
                    if not row or len(row) < 5:
                        continue
                    name = row[0].strip()
                    type_name = row[1].strip()
                    brand = row[2].strip() if row[2].strip() else None
                    model = row[3].strip() if row[3].strip() else None
                    serial_number = row[4].strip()
                    department = row[5].strip() if len(row) > 5 and row[5].strip() else current_user.department
                    status_raw = ''
                    purchase_date = None
                    # 旧逻辑未包含 price 字段，因此无法解析 price；建议升级为带表头的 CSV
                    if len(row) > 7:
                        status_raw = row[6].strip()
                        if row[7].strip():
                            purchase_date = _parse_flexible_date(row[7])
                    elif len(row) > 6:
                        possible = row[6].strip()
                        parsed = _parse_flexible_date(possible)
                        if parsed:
                            purchase_date = parsed
                        else:
                            status_raw = possible

                    # 跳过已有的序列号
                    if Equipment.query.filter_by(serial_number=serial_number).first():
                        skipped += 1
                        continue

                    equipment_type = EquipmentType.query.filter_by(name=type_name).first() if type_name else None
                    type_id = equipment_type.id if equipment_type else None
                    department_obj = Department.query.filter_by(name=department).first() if department else None
                    department_id = department_obj.id if department_obj else None

                    equipment = Equipment(
                        name=name,
                        type_id=type_id,
                        type=type_name if type_name else None,
                        brand=brand,
                        model=model,
                        serial_number=serial_number,
                        purchase_date=purchase_date,
                        department=department,
                        department_id=department_id,
                        status=_status_key('equipment', status_raw) or 'active'
                    )
                    db.session.add(equipment)
                    imported_count += 1

            db.session.commit()
            _log_activity('导入设备', f'导入 {imported_count} 台，跳过 {skipped} 台')
            return jsonify({'success': True, 'message': f'成功导入 {imported_count} 台设备，跳过 {skipped} 台已存在'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'导入失败: {str(e)}'}), 500
    else:
        return jsonify({'success': False, 'message': '请上传CSV文件'}), 400



@bp.route('/equipment/types')
@login_required
def equipment_types():
    """设备类型管理"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    types = EquipmentType.query.all()
    _log_activity('访问页面', '设备类型管理')
    return render_template('main/equipment_types.html', title='设备类型管理', types=types)


@bp.route('/equipment/types/add', methods=['POST'])
@login_required
def add_equipment_type():
    """添加设备类型"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    name = request.form.get('name')
    description = request.form.get('description')
    
    # 验证必填字段
    if not name:
        return jsonify({'success': False, 'message': '类型名称为必填项'})
    
    # 检查是否已存在
    if EquipmentType.query.filter_by(name=name).first():
        return jsonify({'success': False, 'message': '该类型名称已存在'})
    
    # 创建新类型
    equipment_type = EquipmentType(name=name, description=description)
    db.session.add(equipment_type)
    db.session.commit()
    _log_activity('添加设备类型', f'添加类型 {equipment_type.name}')
    
    return jsonify({'success': True, 'message': '设备类型添加成功', 'id': equipment_type.id, 'name': equipment_type.name})


@bp.route('/equipment/types/delete/<int:id>', methods=['POST'])
@login_required
def delete_equipment_type(id):
    """删除设备类型"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    equipment_type = EquipmentType.query.get_or_404(id)
    
    equipment_count = Equipment.query.filter_by(type_id=id).count()
    force = request.args.get('force') == '1'
    if equipment_count > 0 and not force:
        return jsonify({'success': False, 'message': '该类型下还有设备，无法删除。可选择强制删除以解绑设备类型引用'})
    if force and equipment_count > 0:
        for eq in Equipment.query.filter_by(type_id=id).all():
            eq.type_id = None
            # 保留旧字符串类型名称以便显示，不清空 eq.type
        db.session.flush()
    db.session.delete(equipment_type)
    db.session.commit()
    _log_activity('删除设备类型', f'删除类型 {equipment_type.name}')
    return jsonify({'success': True, 'message': '设备类型删除成功'})


@bp.route('/equipment/types/export', methods=['GET'])
@login_required
def export_equipment_types():
    """导出设备类型数据为CSV格式"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    types = EquipmentType.query.order_by(EquipmentType.created_date.desc()).all()
    
    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    
    # CSV表头使用中文
    writer.writerow(['类型名称', '描述', '创建时间'])
    for t in types:
        writer.writerow([
            t.name,
            t.description or '',
            t.created_date.strftime('%Y-%m-%d %H:%M:%S') if t.created_date else ''
        ])
    
    from flask import Response
    csv_data = output.getvalue()
    output.close()
    
    filename = f'设备类型_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    _log_activity('导出设备类型', f'导出设备类型数据 共 {len(types)} 条')
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': content_disposition(filename, 'equipment_types.csv')}
    )


@bp.route('/equipment/types/import', methods=['POST'])
@login_required
def import_equipment_types():
    """从CSV文件导入设备类型数据"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '请选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '请选择文件'}), 400
    
    if file and file.filename.endswith('.csv'):
        try:
            import csv
            import io
            raw = file.stream.read()
            text = None
            for enc in ('utf-8', 'utf-8-sig', 'gbk'):
                try:
                    text = raw.decode(enc)
                    break
                except Exception:
                    continue
            if text is None:
                raise Exception('文件编码不支持，请使用 UTF-8 或 GBK')
            
            stream = io.StringIO(text)
            reader = csv.reader(stream)
            
            # 跳过表头
            try:
                next(reader)
            except StopIteration:
                pass
            
            imported_count = 0
            skipped = 0
            updated = 0
            
            for row in reader:
                if not row or len(row) < 1:
                    continue
                
                name = row[0].strip()
                if not name:
                    continue
                
                description = row[1].strip() if len(row) > 1 else ''
                
                # 检查是否已存在
                existing = EquipmentType.query.filter_by(name=name).first()
                if existing:
                    # 更新描述
                    existing.description = description
                    updated += 1
                else:
                    # 创建新类型
                    new_type = EquipmentType(
                        name=name,
                        description=description
                    )
                    db.session.add(new_type)
                    imported_count += 1
            
            db.session.commit()
            _log_activity('导入设备类型', f'导入设备类型 新增{imported_count}条 更新{updated}条')
            
            return jsonify({
                'success': True,
                'message': f'导入成功！新增 {imported_count} 条，更新 {updated} 条',
                'imported': imported_count,
                'updated': updated
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'导入失败：{str(e)}'}), 500
    
    return jsonify({'success': False, 'message': '只支持CSV文件'}), 400


@bp.route('/spare_parts/types', methods=['GET'])
@login_required
def spare_part_types():
    """配件类型管理"""
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    from app.models import SparePartType
    types = SparePartType.query.order_by(SparePartType.created_date.desc()).all()
    _log_activity('访问页面', '配件类型管理')
    return render_template('main/spare_part_types.html', title='配件类型管理', types=types)


@bp.route('/spare_parts/types/add', methods=['POST'])
@login_required
def add_spare_part_type():
    """添加配件类型"""
    if current_user.role not in ['admin', 'technician']:
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    from app.models import SparePartType
    name = request.form.get('name')
    description = request.form.get('description')
    
    # 验证必填字段
    if not name:
        return jsonify({'success': False, 'message': '类型名称为必填项'})
    
    # 检查是否已存在
    if SparePartType.query.filter_by(name=name).first():
        return jsonify({'success': False, 'message': '该类型名称已存在'})
    
    # 创建新类型
    spare_part_type = SparePartType(name=name, description=description)
    db.session.add(spare_part_type)
    db.session.commit()
    _log_activity('添加配件类型', f'添加类型 {spare_part_type.name}')
    
    return jsonify({
        'success': True,
        'message': '配件类型添加成功',
        'id': spare_part_type.id,
        'name': spare_part_type.name
    })


@bp.route('/spare_parts/types/delete/<int:id>', methods=['POST'])
@login_required
def delete_spare_part_type(id):
    """删除配件类型"""
    if current_user.role not in ['admin', 'technician']:
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    from app.models import SparePartType
    spare_part_type = SparePartType.query.get_or_404(id)
    
    spare_part_count = SparePart.query.filter_by(type_id=id).count()
    force = request.args.get('force') == '1'
    
    if spare_part_count > 0 and not force:
        return jsonify({
            'success': False,
            'message': f'该类型下还有 {spare_part_count} 个配件，无法删除。可选择强制删除以解绑配件类型引用'
        })
    
    if force and spare_part_count > 0:
        for part in SparePart.query.filter_by(type_id=id).all():
            part.type_id = None
        db.session.flush()
    
    db.session.delete(spare_part_type)
    db.session.commit()
    _log_activity('删除配件类型', f'删除类型 {spare_part_type.name}')
    
    return jsonify({'success': True, 'message': '配件类型删除成功'})


@bp.route('/spare_parts/types/export', methods=['GET'])
@login_required
def export_spare_part_types():
    """导出配件类型数据为CSV格式"""
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    from app.models import SparePartType
    types = SparePartType.query.order_by(SparePartType.created_date.desc()).all()
    
    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    
    # CSV表头使用中文
    writer.writerow(['类型名称', '描述', '创建时间'])
    for t in types:
        writer.writerow([
            t.name,
            t.description or '',
            t.created_date.strftime('%Y-%m-%d %H:%M:%S') if t.created_date else ''
        ])
    
    from flask import Response
    csv_data = output.getvalue()
    output.close()
    
    filename = f'配件类型_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    _log_activity('导出配件类型', f'导出配件类型数据 共 {len(types)} 条')
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': content_disposition(filename, 'spare_part_types.csv')}
    )


@bp.route('/spare_parts/types/import', methods=['POST'])
@login_required
def import_spare_part_types():
    """从CSV文件导入配件类型数据"""
    if current_user.role not in ['admin', 'technician']:
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '请选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '请选择文件'}), 400
    
    if file and file.filename.endswith('.csv'):
        try:
            import csv
            import io
            from app.models import SparePartType
            
            raw = file.stream.read()
            text = None
            for enc in ('utf-8', 'utf-8-sig', 'gbk'):
                try:
                    text = raw.decode(enc)
                    break
                except Exception:
                    continue
            if text is None:
                raise Exception('文件编码不支持，请使用 UTF-8 或 GBK')
            
            stream = io.StringIO(text)
            reader = csv.reader(stream)
            
            # 跳过表头
            try:
                next(reader)
            except StopIteration:
                pass
            
            imported_count = 0
            updated = 0
            
            for row in reader:
                if not row or len(row) < 1:
                    continue
                
                name = row[0].strip()
                if not name:
                    continue
                
                description = row[1].strip() if len(row) > 1 else ''
                
                # 检查是否已存在
                existing = SparePartType.query.filter_by(name=name).first()
                if existing:
                    # 更新描述
                    existing.description = description
                    updated += 1
                else:
                    # 创建新类型
                    new_type = SparePartType(
                        name=name,
                        description=description
                    )
                    db.session.add(new_type)
                    imported_count += 1
            
            db.session.commit()
            _log_activity('导入配件类型', f'导入配件类型 新增{imported_count}条 更新{updated}条')
            
            return jsonify({
                'success': True,
                'message': f'导入成功！新增 {imported_count} 条，更新 {updated} 条',
                'imported': imported_count,
                'updated': updated
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'导入失败：{str(e)}'}), 500
    
    return jsonify({'success': False, 'message': '只支持CSV文件'}), 400


@bp.route('/equipment/bulk_public', methods=['POST'])
@login_required
def bulk_public_equipment():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    ids = request.form.getlist('ids[]') or request.form.getlist('ids')
    if not ids and request.is_json:
        ids = (request.get_json() or {}).get('ids', [])
    ids = [int(i) for i in ids if str(i).isdigit()]
    updated = 0
    for eq in Equipment.query.filter(Equipment.id.in_(ids)).all():
        if not eq.is_public_pool:
            eq.is_public_pool = True
            _log_activity('加入公开仓库', f'设备 {eq.name}#{eq.id} 加入信息部公开仓库')
            updated += 1
    db.session.commit()
    return jsonify({'success': True, 'updated': updated})


@bp.route('/equipment/bulk_unpublic', methods=['POST'])
@login_required
def bulk_unpublic_equipment():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    ids = request.form.getlist('ids[]') or request.form.getlist('ids')
    if not ids and request.is_json:
        ids = (request.get_json() or {}).get('ids', [])
    ids = [int(i) for i in ids if str(i).isdigit()]
    updated = 0
    for eq in Equipment.query.filter(Equipment.id.in_(ids)).all():
        if eq.is_public_pool:
            eq.is_public_pool = False
            _log_activity('移出公开仓库', f'设备 {eq.name}#{eq.id} 从信息部公开仓库移出')
            updated += 1
    db.session.commit()
    return jsonify({'success': True, 'updated': updated})


@bp.route('/equipment/bulk_delete', methods=['POST'])
@login_required
def bulk_delete_equipment():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    ids = request.form.getlist('ids[]') or request.form.getlist('ids')
    if not ids and request.is_json:
        ids = (request.get_json() or {}).get('ids', [])
    ids = [int(i) for i in ids if str(i).isdigit()]
    if not ids:
        return jsonify({'success': False, 'message': '请选择要删除的设备'})
    equipments = Equipment.query.filter(Equipment.id.in_(ids)).all()
    deleted = 0
    for eq in equipments:
        _log_activity('删除设备', f'批量删除设备 {eq.name}#{eq.id}')
        db.session.delete(eq)
        deleted += 1
    db.session.commit()
    return jsonify({'success': True, 'deleted': deleted})


@bp.route('/equipment/bulk_set_available', methods=['POST'])
@login_required
def bulk_set_available_equipment():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    ids = request.form.getlist('ids[]') or request.form.getlist('ids')
    if not ids and request.is_json:
        ids = (request.get_json() or {}).get('ids', [])
    ids = [int(i) for i in ids if str(i).isdigit()]
    updated = 0
    for eq in Equipment.query.filter(Equipment.id.in_(ids)).all():
        if eq.status != 'available':
            eq.status = 'available'
            _log_activity('设为可申请', f'设备 {eq.name}#{eq.id} 设为可申请')
            updated += 1
    db.session.commit()
    return jsonify({'success': True, 'updated': updated})


@bp.route('/equipment/bulk_cancel_available', methods=['POST'])
@login_required
def bulk_cancel_available_equipment():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    ids = request.form.getlist('ids[]') or request.form.getlist('ids')
    if not ids and request.is_json:
        ids = (request.get_json() or {}).get('ids', [])
    ids = [int(i) for i in ids if str(i).isdigit()]
    updated = 0
    for eq in Equipment.query.filter(Equipment.id.in_(ids)).all():
        if eq.status == 'available':
            eq.status = 'active'
            _log_activity('取消可申请', f'设备 {eq.name}#{eq.id} 取消可申请状态')
            updated += 1
    db.session.commit()
    return jsonify({'success': True, 'updated': updated})

@bp.route('/spare_parts')
@login_required
def spare_parts():
    department_id = request.args.get('department_id', type=int)
    min_stock = request.args.get('min_stock', type=int)
    max_stock = request.args.get('max_stock', type=int)
    search_query = (request.args.get('search') or '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('SPARE_PARTS_PER_PAGE', 10)
    
    query = SparePart.query
    # admin不受部门限制,可以查看所有配件
    if current_user.role != 'admin' and current_user.department:
        query = query.filter_by(department=current_user.department)
    
    if department_id:
        department = Department.query.get(department_id)
        if department:
            query = query.filter(
                or_(
                    SparePart.department_id == department.id,
                    SparePart.department == department.name
                )
            )
    if min_stock is not None:
        query = query.filter(SparePart.stock_quantity >= min_stock)
    if max_stock is not None:
        query = query.filter(SparePart.stock_quantity <= max_stock)
    if search_query:
        like = f"%{search_query}%"
        query = query.filter(
            or_(
                SparePart.name.ilike(like),
                SparePart.part_number.ilike(like),
                SparePart.location.ilike(like)
            )
        )
    
    pagination = query.order_by(SparePart.name.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    spare_parts = pagination.items
    
    departments = Department.query.order_by(Department.name).all()
        
    _log_activity('访问页面', '配件列表')
    return render_template(
        'main/spare_parts.html',
                         title='配件列表', 
                         spare_parts=spare_parts,
                         departments=departments,
                         selected_department_id=department_id,
                         selected_min_stock=min_stock,
        selected_max_stock=max_stock,
        search_query=search_query,
        pagination=pagination,
        per_page=per_page
    )


@bp.route('/spare_parts/add', methods=['GET', 'POST'])
@login_required
def add_spare_part():
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限添加配件')
        return redirect(url_for('main.spare_parts'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        part_number = request.form.get('part_number')
        type_id = request.form.get('type_id')  # 配件类型
        price = request.form.get('price')
        stock_quantity = request.form.get('stock_quantity')
        purchase_date = request.form.get('purchase_date')
        department = request.form.get('department', current_user.department)  # 默认为当前用户部门
        location = request.form.get('location')
        
        # 检查配件编号是否已存在
        if SparePart.query.filter_by(part_number=part_number).first():
            flash('该配件编号已存在')
            return redirect(url_for('main.add_spare_part'))
            
        spare_part = SparePart(
            name=name,
            part_number=part_number,
            type_id=int(type_id) if type_id else None,
            price=float(price) if price else 0.0,
            stock_quantity=int(stock_quantity) if stock_quantity else 0,
            department=department,
            location=location
        )
        
        if purchase_date:
            try:
                spare_part.purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
            except ValueError:
                flash('日期格式不正确')
                return redirect(url_for('main.add_spare_part'))
        
        db.session.add(spare_part)
        db.session.commit()
        _log_activity('添加配件', f'添加配件 {spare_part.name}#{spare_part.part_number}')
        
        flash('配件添加成功')
        return redirect(url_for('main.spare_parts'))
        
    # 获取所有部门供选择
    departments = Department.query.order_by(Department.name).all()
    department_list = [dept.name for dept in departments]
    
    # 获取所有配件类型供选择
    spare_part_types = SparePartType.query.order_by(SparePartType.name).all()
        
    return render_template('main/add_spare_part.html', title='添加配件', departments=department_list, spare_part_types=spare_part_types)


@bp.route('/spare_parts/export')
@login_required
def export_spare_parts():
    """导出配件数据为CSV格式（支持筛选）"""
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))

    # 获取筛选参数
    department_id = request.args.get('department_id', type=int)
    min_stock = request.args.get('min_stock', type=int)
    max_stock = request.args.get('max_stock', type=int)
    
    # 构建查询
    query = SparePart.query
    
    if department_id:
        query = query.filter_by(department_id=department_id)
    if min_stock is not None:
        query = query.filter(SparePart.stock_quantity >= min_stock)
    if max_stock is not None:
        query = query.filter(SparePart.stock_quantity <= max_stock)
    
    parts = query.all()

    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['配件名称', '配件编号', '配件类型', '价格', '库存数量', '最低库存', '入库日期', '所属部门', '位置'])
    for p in parts:
        writer.writerow([
            p.name,
            p.part_number,
            p.spare_part_type.name if p.spare_part_type else '',
            p.price,
            p.stock_quantity,
            p.min_stock_level,
            p.purchase_date.strftime('%Y-%m-%d') if p.purchase_date else '',
            p.department,
            p.location or ''
        ])

    from flask import Response
    csv_data = output.getvalue()
    output.close()
    
    filename = f'配件数据_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    _log_activity('导出配件', f'导出配件数据 共 {len(parts)} 条')
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': content_disposition(filename, 'spare_parts.csv')}
    )


@bp.route('/spare_parts/import', methods=['POST'])
@login_required
def import_spare_parts():
    """从CSV文件导入配件数据"""
    if current_user.role not in ['admin', 'technician']:
        return jsonify({'success': False, 'message': '权限不足'}), 403

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '请选择文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '请选择文件'}), 400

    if file and file.filename.endswith('.csv'):
        try:
            import csv
            import io
            raw = file.stream.read()
            text = None
            for enc in ('utf-8', 'utf-8-sig', 'gbk'):
                try:
                    text = raw.decode(enc)
                    break
                except Exception:
                    continue
            if text is None:
                raise Exception('文件编码不支持，请使用 UTF-8 或 GBK')
            stream = io.StringIO(text)
            reader = csv.reader(stream)
            # 跳过表头
            try:
                next(reader)
            except StopIteration:
                pass

            imported_count = 0
            skipped = 0
            for row in reader:
                if not row or len(row) < 2:
                    continue
                name = row[0].strip()
                part_number = row[1].strip()
                type_name = row[2].strip() if len(row) > 2 and row[2].strip() else None
                price = float(row[3]) if len(row) > 3 and row[3].strip() else 0.0
                stock_quantity = int(row[4]) if len(row) > 4 and row[4].strip() else 0
                
                # 根据类型名称查找类型ID
                type_id = None
                if type_name:
                    spare_type = SparePartType.query.filter_by(name=type_name).first()
                    if spare_type:
                        type_id = spare_type.id

                min_stock_level = 0
                purchase_date = None
                purchase_idx = None
                dept_idx = None
                loc_idx = None

                if len(row) > 5:
                    candidate = row[5].strip()
                    parsed_candidate = _parse_flexible_date(candidate)
                    if parsed_candidate:
                        purchase_date = parsed_candidate
                        dept_idx = 6 if len(row) > 6 else None
                        loc_idx = 7 if len(row) > 7 else None
                    else:
                        if candidate:
                            try:
                                min_stock_level = int(candidate)
                            except ValueError:
                                min_stock_level = 0
                        purchase_idx = 6 if len(row) > 6 else None
                        dept_idx = 7 if len(row) > 7 else None
                        loc_idx = 8 if len(row) > 8 else None
                else:
                    dept_idx = 6 if len(row) > 6 else None
                    loc_idx = 7 if len(row) > 7 else None

                if purchase_date is None and purchase_idx is not None and len(row) > purchase_idx:
                    purchase_raw = row[purchase_idx].strip()
                    if purchase_raw:
                        purchase_date = _parse_flexible_date(purchase_raw)

                department = row[dept_idx].strip() if dept_idx is not None and len(row) > dept_idx and row[dept_idx].strip() else current_user.department
                location = row[loc_idx].strip() if loc_idx is not None and len(row) > loc_idx and row[loc_idx].strip() else None

                # 跳过已有的配件编号
                if SparePart.query.filter_by(part_number=part_number).first():
                    skipped += 1
                    continue

                spare_part = SparePart(
                    name=name,
                    part_number=part_number,
                    type_id=type_id,
                    price=price,
                    stock_quantity=stock_quantity,
                    min_stock_level=min_stock_level,
                    department=department,
                    location=location
                )
                if purchase_date:
                    spare_part.purchase_date = purchase_date
                db.session.add(spare_part)
                imported_count += 1

            db.session.commit()
            _log_activity('导入配件', f'导入 {imported_count} 个，跳过 {skipped} 个')
            return jsonify({'success': True, 'message': f'成功导入 {imported_count} 个配件，跳过 {skipped} 个已存在'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'导入失败: {str(e)}'}), 500
    else:
        return jsonify({'success': False, 'message': '请上传CSV文件'}), 400


@bp.route('/spare_parts/bulk_delete', methods=['POST'])
@login_required
def bulk_delete_spare_parts():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    ids = request.form.getlist('ids[]') or request.form.getlist('ids')
    if not ids and request.is_json:
        ids = (request.get_json() or {}).get('ids', [])
    ids = [int(i) for i in ids if str(i).isdigit()]
    if not ids:
        return jsonify({'success': False, 'message': '请选择要删除的配件'})
    parts = SparePart.query.filter(SparePart.id.in_(ids)).all()
    deleted = 0
    for part in parts:
        _log_activity('删除配件', f'批量删除配件 {part.name}#{part.part_number}')
        db.session.delete(part)
        deleted += 1
    db.session.commit()
    return jsonify({'success': True, 'deleted': deleted})


@bp.route('/spare_parts/bulk_public', methods=['POST'])
@login_required
def bulk_public_spare_parts():
    """批量将配件设为公开"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    ids = request.form.getlist('ids[]') or request.form.getlist('ids')
    if not ids and request.is_json:
        ids = (request.get_json() or {}).get('ids', [])
    ids = [int(i) for i in ids if str(i).isdigit()]
    if not ids:
        return jsonify({'success': False, 'message': '请选择要公开的配件'})
    
    parts = SparePart.query.filter(SparePart.id.in_(ids)).all()
    updated = 0
    for part in parts:
        if not part.is_public:
            part.is_public = True
            _log_activity('配件公开', f'将配件 {part.name}#{part.part_number} 设置为公开')
            updated += 1
    
    db.session.commit()
    return jsonify({'success': True, 'updated': updated})


@bp.route('/spare_parts/bulk_unpublic', methods=['POST'])
@login_required
def bulk_unpublic_spare_parts():
    """批量取消配件公开"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    ids = request.form.getlist('ids[]') or request.form.getlist('ids')
    if not ids and request.is_json:
        ids = (request.get_json() or {}).get('ids', [])
    ids = [int(i) for i in ids if str(i).isdigit()]
    if not ids:
        return jsonify({'success': False, 'message': '请选择要取消公开的配件'})
    
    parts = SparePart.query.filter(SparePart.id.in_(ids)).all()
    updated = 0
    for part in parts:
        if part.is_public:
            part.is_public = False
            _log_activity('配件取消公开', f'将配件 {part.name}#{part.part_number} 取消公开')
            updated += 1
    
    db.session.commit()
    return jsonify({'success': True, 'updated': updated})


@bp.route('/spare_parts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_spare_part(id):
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限编辑配件')
        return redirect(url_for('main.spare_parts'))
        
    spare_part = SparePart.query.get_or_404(id)
    
    if request.method == 'POST':
        spare_part.name = request.form.get('name')
        spare_part.part_number = request.form.get('part_number')
        type_id = request.form.get('type_id')  # 配件类型
        price = request.form.get('price')
        stock_quantity = request.form.get('stock_quantity')
        purchase_date = request.form.get('purchase_date')
        department = request.form.get('department', current_user.department)
        location = request.form.get('location')
        
        # 检查配件编号是否已存在（排除当前配件）
        existing = SparePart.query.filter_by(part_number=spare_part.part_number).first()
        if existing and existing.id != spare_part.id:
            flash('该配件编号已存在')
            return redirect(url_for('main.edit_spare_part', id=id))
        
        spare_part.type_id = int(type_id) if type_id else None
        spare_part.price = float(price) if price else 0.0
        spare_part.stock_quantity = int(stock_quantity) if stock_quantity else 0
        spare_part.department = department
        spare_part.location = location
        
        if purchase_date:
            try:
                spare_part.purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
            except ValueError:
                flash('日期格式不正确')
                return redirect(url_for('main.edit_spare_part', id=id))
        else:
            spare_part.purchase_date = None
        
        db.session.commit()
        _log_activity('更新配件', f'更新配件 {spare_part.name}#{spare_part.part_number}')
        
        flash('配件更新成功')
        return redirect(url_for('main.spare_parts'))
        
    # 获取所有部门供选择
    departments = Department.query.order_by(Department.name).all()
    department_list = [dept.name for dept in departments]
    
    # 获取所有配件类型供选择
    spare_part_types = SparePartType.query.order_by(SparePartType.name).all()
        
    return render_template('main/edit_spare_part.html', title='编辑配件', spare_part=spare_part, departments=department_list, spare_part_types=spare_part_types)


@bp.route('/spare_parts/delete/<int:id>', methods=['POST'])
@login_required
def delete_spare_part(id):
    if current_user.role not in ['admin']:
        return jsonify({'success': False, 'message': '权限不足'}), 403
        
    spare_part = SparePart.query.get_or_404(id)
    part_name = spare_part.name
    part_number = spare_part.part_number
    
    db.session.delete(spare_part)
    db.session.commit()
    _log_activity('删除配件', f'删除配件 {part_name}#{part_number}')
    
    return jsonify({'success': True, 'message': '配件删除成功'})


@bp.route('/repair_orders/<int:id>')
@login_required
def repair_order_detail(id):
    order = RepairOrder.query.get_or_404(id)
    
    # 检查权限
    if current_user.role == 'user' and order.requester_id != current_user.id:
        flash('您没有权限查看此工单')
        return redirect(url_for('main.repair_orders'))
        
    return render_template('main/repair_order_detail.html', title='工单详情', order=order)


@bp.route('/create_repair_order', methods=['GET', 'POST'])
@login_required
def create_repair_order():
    # 获取当前用户所属部门的设备
    # admin可以选择所有设备,其他用户只能选择本部门设备
    if current_user.role == 'admin':
        equipments = Equipment.query.all()
    elif current_user.department:
        equipments = Equipment.query.filter_by(department=current_user.department).all()
    else:
        equipments = []
    
    if request.method == 'POST':
        equipment_id = request.form.get('equipment_id', type=int)
        description = request.form.get('description')
        
        # 验证数据
        if not equipment_id or not description:
            flash('请填写所有必填字段')
            if current_user.role == 'admin':
                equipments = Equipment.query.all()
            elif current_user.department:
                equipments = Equipment.query.filter_by(department=current_user.department).all()
            else:
                equipments = []
            return render_template('main/create_repair_order.html', title='创建维修工单', equipments=equipments)
        
        # 检查设备是否存在
        # admin可以为任何设备创建工单,其他用户只能为本部门设备创建
        if current_user.role == 'admin':
            equipment = Equipment.query.filter_by(id=equipment_id).first()
        elif current_user.department:
            equipment = Equipment.query.filter_by(id=equipment_id, department=current_user.department).first()
        else:
            equipment = None
        if not equipment:
            flash('请选择有效的设备')
            return redirect(url_for('main.create_repair_order'))
        
        # 创建维修工单
        repair_order = RepairOrder(
            equipment_id=equipment_id,
            requester_id=current_user.id,
            description=description
        )
        
        db.session.add(repair_order)
        db.session.flush()  # 获取repair_order.id
        
        # 更新设备状态为维修中
        equipment.status = 'repair'
        _log_activity('设备进入维修', f'设备 {equipment.name} 状态变更为维修中 (维修工单 #{repair_order.id})')
        
        # 获取第一个审批节点
        first_node = WorkflowNode.query.join(WorkflowTemplate).filter(
            WorkflowTemplate.order_type == 'repair_order',
            WorkflowNode.is_active == True
        ).order_by(WorkflowNode.sequence).first()
        
        if first_node:
            # 创建第一个审批流程
            approval = ApprovalWorkflow(
                order_type='repair_order',
                order_id=repair_order.id,
                approver_id=get_approver_id(first_node, current_user.department),
                approval_level=first_node.role_required,
                node_id=first_node.id,
                status='pending'
            )
            db.session.add(approval)
        else:
            # 如果没有配置审批流程，则直接设置为待处理状态
            repair_order.status = 'pending'
        
        # 记录用户创建工单活动
        activity_log = UserActivityLog(
            user_id=current_user.id,
            action='创建维修工单',
            description=f'用户 {current_user.username} 创建了维修工单 #{repair_order.id}'
        )
        db.session.add(activity_log)
        
        # 创建通知给管理员和部门领导
        admins = User.query.filter_by(role='admin').all()
        # 只有用户有部门时才查找部门负责人
        if current_user.department:
            department_heads = User.query.filter_by(role='department_head', department=current_user.department).all()
        else:
            department_heads = []
        
        # 给所有管理员发送通知
        for admin in admins:
            notification = Notification(
                user_id=admin.id,
                title='新维修工单',
                message=f'用户 {current_user.username} 提交了新的维修工单 #{repair_order.id}'
            )
            db.session.add(notification)
            
        # 给部门领导发送通知
        for department_head in department_heads:
            notification = Notification(
                user_id=department_head.id,
                title='新维修工单',
                message=f'用户 {current_user.username} 提交了新的维修工单 #{repair_order.id}'
            )
            db.session.add(notification)
        
        db.session.commit()
        
        flash('维修工单创建成功')
        return redirect(url_for('main.repair_orders'))
        
    return render_template('main/create_repair_order.html', 
                         title='创建维修工单', 
                         equipments=equipments)


@bp.route('/repair_orders/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_repair_order(id):
    """编辑维修工单"""
    order = RepairOrder.query.get_or_404(id)
    
    # 权限检查：只有工单创建者、管理员可以编辑
    if current_user.role != 'admin' and order.requester_id != current_user.id:
        flash('您没有权限编辑此工单', 'danger')
        return redirect(url_for('main.repair_orders'))
    
    # 获取可选设备
    if current_user.role == 'admin':
        equipments = Equipment.query.all()
    elif current_user.department:
        equipments = Equipment.query.filter_by(department=current_user.department).all()
    else:
        equipments = []
    
    if request.method == 'POST':
        equipment_id = request.form.get('equipment_id', type=int)
        description = request.form.get('description')
        new_status = request.form.get('status')
        repair_description = request.form.get('repair_description')
        
        if not equipment_id or not description:
            flash('请填写所有必填字段', 'danger')
            return render_template('main/edit_repair_order.html', 
                                 title='编辑维修工单', 
                                 order=order,
                                 equipments=equipments)
        
        # 如果状态改为已完成，需要填写维修说明
        if new_status == 'completed' and not repair_description:
            flash('完成工单时必须填写维修说明', 'danger')
            return render_template('main/edit_repair_order.html', 
                                 title='编辑维修工单', 
                                 order=order,
                                 equipments=equipments)
        
        # 检查设备权限
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            flash('设备不存在', 'danger')
            return render_template('main/edit_repair_order.html', 
                                 title='编辑维修工单', 
                                 order=order,
                                 equipments=equipments)
        
        if current_user.role != 'admin' and equipment.department != current_user.department:
            flash('您只能选择本部门的设备', 'danger')
            return render_template('main/edit_repair_order.html', 
                                 title='编辑维修工单', 
                                 order=order,
                                 equipments=equipments)
        
        # 更新工单信息
        old_equipment_name = order.equipment.name if order.equipment else ''
        old_status = order.status
        
        order.equipment_id = equipment_id
        order.description = description
        order.status = new_status
        order.updated_date = get_beijing_now()
        
        # 更新维修说明
        if repair_description:
            order.repair_description = repair_description
        
        # 如果状态变为已完成，记录完成时间并恢复设备状态
        if new_status == 'completed' and old_status != 'completed':
            order.completed_date = get_beijing_now()
            if order.equipment:
                order.equipment.status = 'available'
                _log_activity('维修完成', f'设备 {order.equipment.name} 维修完成,状态恢复为可用 (维修工单 #{order.id})')
        
        # 如果从已完成改为其他状态，清除完成时间
        if old_status == 'completed' and new_status != 'completed':
            order.completed_date = None
        
        db.session.commit()
        
        status_text = {
            'submitted': '已提交',
            'in_progress': '处理中',
            'completed': '已完成',
            'cancelled': '已取消'
        }
        
        _log_activity('编辑维修工单', 
                     f'编辑维修工单 #{order.id} - {old_equipment_name} -> {equipment.name}, '
                     f'状态: {status_text.get(old_status, old_status)} -> {status_text.get(new_status, new_status)}')
        
        flash('维修工单更新成功', 'success')
        return redirect(url_for('main.repair_order_detail', id=id))
    
    return render_template('main/edit_repair_order.html', 
                         title='编辑维修工单', 
                         order=order,
                         equipments=equipments)


@bp.route('/repair_orders/<int:id>/delete', methods=['POST'])
@login_required
def delete_repair_order(id):
    """删除维修工单"""
    order = RepairOrder.query.get_or_404(id)
    
    # 权限检查：只有工单创建者、管理员可以删除
    if current_user.role != 'admin' and order.requester_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限删除此工单'})
    
    # 只允许删除已提交状态的工单
    if order.status not in ['submitted', 'cancelled']:
        return jsonify({'success': False, 'message': '只能删除已提交或已取消状态的工单'})
    
    equipment_name = order.equipment.name if order.equipment else ''
    order_id = order.id
    
    db.session.delete(order)
    db.session.commit()
    
    _log_activity('删除维修工单', f'删除维修工单 #{order_id} - {equipment_name}')
    
    return jsonify({'success': True, 'message': '维修工单删除成功'})


@bp.route('/repair_orders/<int:id>/update_status', methods=['GET', 'POST'])
@login_required
def update_repair_order_status(id):
    repair_order = RepairOrder.query.get_or_404(id)
    
    # 检查权限（只有技术员和管理员可以更新状态）
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限执行此操作')
        return redirect(url_for('main.repair_orders'))
    
    if request.method == 'GET':
        # 获取所有技术员用于分配
        technicians = User.query.filter_by(role='technician').all()
        return render_template('main/update_repair_order_status.html', 
                             title='更新工单状态',
                             repair_order=repair_order,
                             technicians=technicians)
    
    # POST 请求处理
    new_status = request.form.get('status')
    repair_description = request.form.get('repair_description')
    technician_id = request.form.get('technician_id')
    
    # 更新工单状态
    old_status = repair_order.status
    repair_order.status = new_status
    
    if repair_description:
        repair_order.repair_description = repair_description
        
    if technician_id:
        repair_order.technician_id = technician_id
        
    if new_status == 'completed' and not repair_order.completed_date:
        repair_order.completed_date = get_beijing_now()
        
        # 维修完成时恢复设备状态为可用
        if repair_order.equipment:
            repair_order.equipment.status = 'available'
            _log_activity('维修完成', f'设备 {repair_order.equipment.name} 维修完成,状态恢复为可用 (维修工单 #{repair_order.id})')
    
    repair_order.updated_date = get_beijing_now()
    db.session.commit()
    
    flash('工单状态更新成功')
    return redirect(url_for('main.repair_order_detail', id=id))


@bp.route('/notifications')
@login_required
def notifications():
    # 支持筛选、关键字、日期范围与分页
    filter_type = request.args.get('filter', 'all')  # all, unread, read
    q = request.args.get('q', '').strip()
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Notification.query.filter_by(user_id=current_user.id)

    # 读/未读过滤
    if filter_type == 'unread':
        query = query.filter_by(is_read=False)
    elif filter_type == 'read':
        query = query.filter_by(is_read=True)

    # 关键字过滤（标题或内容）
    if q:
        like_q = f"%{q}%"
        query = query.filter((Notification.title.ilike(like_q)) | (Notification.message.ilike(like_q)))

    # 日期范围过滤（created_date 为 datetime）
    try:
        if from_date:
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(Notification.created_date >= from_dt)
        if to_date:
            to_dt = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Notification.created_date < to_dt)
    except Exception:
        # 忽略解析错误，按无日期过滤处理
        pass

    pagination = query.order_by(Notification.created_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    notifications = pagination.items

    return render_template('main/notifications.html', 
                         title='通知消息', 
                         notifications=notifications,
                         pagination=pagination,
                         filter_type=filter_type,
                         q=q,
                         from_date=from_date,
                         to_date=to_date)


@bp.route('/mark_notification_as_read/<int:id>', methods=['POST'])
@login_required
def mark_notification_as_read(id):
    """将通知标记为已读，AJAX 优先返回 JSON。前端应保留该通知在列表中，只做状态更新和计数更新。"""
    notification = Notification.query.get_or_404(id)

    # 检查权限
    if notification.user_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限操作此通知'}), 403

    if not notification.is_read:
        notification.is_read = True
        db.session.commit()

    # 返回简单的通知状态，前端根据此结果更新界面
    return jsonify({'success': True, 'message': '已标记为已读', 'id': notification.id, 'is_read': notification.is_read})


@bp.route('/mark_all_notifications_as_read', methods=['POST'])
@login_required
def mark_all_notifications_as_read():
    """将当前用户的所有未读通知标记为已读"""
    try:
        unread_notifications = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).all()
        
        count = 0
        for notification in unread_notifications:
            notification.is_read = True
            count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'已标记 {count} 条通知为已读',
            'count': count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500


@bp.route('/notifications/export')
@login_required
def export_notifications():
    """导出当前筛选条件下的通知为 CSV。"""
    # 与列表查询共享相同的筛选逻辑
    filter_type = request.args.get('filter', 'all')
    q = request.args.get('q', '').strip()
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    query = Notification.query.filter_by(user_id=current_user.id)
    if filter_type == 'unread':
        query = query.filter_by(is_read=False)
    elif filter_type == 'read':
        query = query.filter_by(is_read=True)

    if q:
        like_q = f"%{q}%"
        query = query.filter((Notification.title.ilike(like_q)) | (Notification.message.ilike(like_q)))

    try:
        if from_date:
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(Notification.created_date >= from_dt)
        if to_date:
            to_dt = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Notification.created_date < to_dt)
    except Exception:
        pass

    notes = query.order_by(Notification.created_date.desc()).all()

    import csv, io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', '标题', '内容', '创建时间', '已读'])
    for n in notes:
        writer.writerow([
            n.id,
            n.title,
            n.message,
            n.created_date.strftime('%Y-%m-%d %H:%M:%S') if n.created_date else '',
            '是' if n.is_read else '否'
        ])

    from flask import Response
    csv_data = output.getvalue()
    output.close()
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': content_disposition('通知消息.csv', 'notifications.csv')}
    )


@bp.route('/approvals')
@login_required
def approvals():
    """查看需要我审批的工单"""
    # 获取需要当前用户审批的工单
    pending_approvals = ApprovalWorkflow.query.filter_by(
        approver_id=current_user.id,
        status='pending'
    ).all()
    
    # 获取相关工单信息
    repair_orders = []
    part_orders = []
    transfer_orders = []
    scrap_orders = []
    application_orders = []
    loan_orders = []
    
    for approval in pending_approvals:
        if approval.order_type == 'repair_order':
            order = RepairOrder.query.get(approval.order_id)
            if order:
                repair_orders.append({
                    'order': order,
                    'approval': approval
                })
        elif approval.order_type == 'part_request_order':
            order = PartRequestOrder.query.get(approval.order_id)
            if order:
                part_orders.append({
                    'order': order,
                    'approval': approval
                })
        elif approval.order_type == 'equipment_transfer':
            order = EquipmentTransfer.query.get(approval.order_id)
            if order:
                transfer_orders.append({
                    'order': order,
                    'approval': approval
                })
        elif approval.order_type == 'equipment_scrap':
            order = EquipmentScrap.query.get(approval.order_id)
            if order:
                scrap_orders.append({
                    'order': order,
                    'approval': approval
                })
        elif approval.order_type == 'equipment_application':
            order = EquipmentApplication.query.get(approval.order_id)
            if order:
                application_orders.append({
                    'order': order,
                    'approval': approval,
                    'type': 'application'
                })
        elif approval.order_type == 'equipment_loan':
            order = EquipmentLoan.query.get(approval.order_id)
            if order:
                loan_orders.append({
                    'order': order,
                    'approval': approval
                })
    
    return render_template('main/approvals.html', title='待审批工单', repair_orders=repair_orders, part_orders=part_orders, transfer_orders=transfer_orders, scrap_orders=scrap_orders, application_orders=application_orders, loan_orders=loan_orders)


# 注意: approval_history 路由已移至 approval_history_routes.py,避免重复定义
# 该文件包含了更完整的审批历史功能,包括分页、过滤和管理员干预等


@bp.route('/approvals/repair_order/<int:order_id>/<action>', methods=['POST'])
@login_required
def approve_repair_order(order_id, action):
    """审批维修工单"""
    # 获取审批记录 - 管理员可以审批任何待审批的工单
    if current_user.role in ['admin', 'super_admin']:
        # 管理员:找到任何待审批的记录
        approval = ApprovalWorkflow.query.filter_by(
            order_type='repair_order',
            order_id=order_id,
            status='pending'
        ).first_or_404()
    else:
        # 普通用户:只能审批分配给自己的
        approval = ApprovalWorkflow.query.filter_by(
            order_type='repair_order',
            order_id=order_id,
            approver_id=current_user.id,
            status='pending'
        ).first_or_404()
    
    # 获取工单
    repair_order = RepairOrder.query.get_or_404(order_id)
    
    if action == 'approve':
        # 更新审批状态
        approval.status = 'approved'
        approval.approved_date = datetime.now(timezone.utc)
        approval.comments = request.form.get('comments', '')
        
        # 处理维修金额(管理员评估金额节点)
        repair_cost = request.form.get('repair_cost')
        if repair_cost:
            try:
                repair_order.repair_cost = float(repair_cost)
            except (ValueError, TypeError):
                flash('维修金额格式错误', 'danger')
                db.session.rollback()
                return redirect(url_for('main.approvals'))
        
        # 根据审批级别更新工单状态
        if approval.approval_level == 'department_head':
            repair_order.department_head_approved = True
            repair_order.department_head_id = current_user.id
            repair_order.status = 'department_head_approved'
                
        elif approval.approval_level == 'admin':
            repair_order.admin_approved = True
            repair_order.admin_id = current_user.id
            repair_order.status = 'admin_approved'
            
        # 检查是否还有后续审批节点
        next_node = get_next_approval_node('repair_order', repair_order.id)
        if next_node:
            # 创建下一个审批节点
            next_approver_id = get_approver_id(next_node, repair_order.requester.department)
            if not next_approver_id:
                flash(f'错误: 无法找到 {next_node.name} 的审批人 (角色: {next_node.role_required}, 部门: {repair_order.requester.department})', 'danger')
                db.session.rollback()
                return redirect(url_for('main.approvals'))
                
            next_approval = ApprovalWorkflow(
                order_type='repair_order',
                order_id=repair_order.id,
                approver_id=next_approver_id,
                approval_level=next_node.role_required,
                node_id=next_node.id,  # 添加 node_id
                status='pending'
            )
            db.session.add(next_approval)
            
            # 发送通知给下一个审批人
            next_approver = User.query.get(next_approver_id)
            if next_approver:
                # 使用新的通知工具(包含实时推送)
                from app.notification_utils import notify_approval_needed
                notify_approval_needed(
                    approver_id=next_approver.id,
                    order_type='repair_order',
                    order_id=repair_order.id,
                    order_description=f'维修工单 - {repair_order.description}',
                    node_name=next_node.name
                )
            
            # 审批进行中，发送进度通知给申请人
            from app.notification_utils import notify_approval_progress
            notify_approval_progress(
                requester_id=repair_order.requester_id,
                order_type='repair_order',
                order_id=repair_order.id,
                approver_name=current_user.username,
                next_node_name=next_node.name
            )
        else:
            # 所有审批完成，更新工单状态为已批准（归档）
            repair_order.status = 'approved'
            
            # 发送审批完成通知给申请人
            from app.notification_utils import notify_approval_completed
            notify_approval_completed(
                requester_id=repair_order.requester_id,
                order_type='repair_order',
                order_id=repair_order.id,
                order_description='维修工单'
            )
            
            # 发送通知给管理员和技术员
            from app.notification_utils import create_notification
            admins = User.query.filter_by(role='admin').all()
            technicians = User.query.filter_by(role='technician').all()
            for user in admins + technicians:
                if user.id != current_user.id:
                    create_notification(
                        user_id=user.id,
                        title='维修工单已批准',
                        message=f'维修工单 #{repair_order.id} 已通过审批，等待处理',
                        order_type='repair_order',
                        order_id=repair_order.id,
                        notification_type='info',
                        link='/repair_orders'
                    )
            
            # 记录审批活动
            _log_activity('审批维修工单', f'用户 {current_user.username} 批准了维修工单 #{repair_order.id}')
            
        flash('维修工单审批成功')
        
    elif action == 'reject':
        # 拒绝工单
        approval.status = 'rejected'
        approval.approved_date = datetime.now(timezone.utc)
        approval.comments = request.form.get('comments', '')
        
        # 更新工单状态
        repair_order.status = 'cancelled'
        
        # 记录审批活动
        _log_activity('审批维修工单', f'用户 {current_user.username} 拒绝了维修工单 #{repair_order.id}')
        
        # 创建通知给申请人
        from app.notification_utils import notify_approval_rejected
        notify_approval_rejected(
            requester_id=repair_order.requester_id,
            order_type='repair_order',
            order_id=repair_order.id,
            approver_name=current_user.username,
            reason=approval.comments
        )
        
        flash('维修工单已拒绝')
        
    db.session.commit()
    return redirect(url_for('main.approvals'))


def get_next_approval_node(order_type, order_id):
    """获取下一个审批节点"""
    # 延迟导入以避免循环依赖
    from app.approval_models import WorkflowNode, WorkflowTemplate

    # 获取当前已完成的审批节点
    current_approvals = ApprovalWorkflow.query.filter_by(
        order_type=order_type,
        order_id=order_id
    ).filter(ApprovalWorkflow.status.in_(['approved', 'rejected'])).all()
    
    # 获取所有审批节点
    all_nodes = WorkflowNode.query.join(WorkflowTemplate).filter(
        WorkflowTemplate.order_type == order_type,
        WorkflowNode.is_active == True
    ).order_by(WorkflowNode.sequence).all()
    
    # 找到下一个未处理的节点
    approved_node_ids = [approval.node_id for approval in current_approvals if approval.node_id]
    for node in all_nodes:
        if node.id not in approved_node_ids:
            return node
    
    return None


def get_approver_id(node, department_name):
    """根据节点和部门获取审批人ID
    
    优先使用新的审批角色系统，如果角色未分配用户则fallback到旧的role_required逻辑
    """
    # 1. 尝试从审批角色获取审批人
    if node.approval_role_id:
        from app.approval_roles import UserApprovalRole
        
        # 查找该角色的活跃用户
        assignments = UserApprovalRole.query.filter_by(
            role_id=node.approval_role_id,
            is_active=True
        ).all()
        
        # 如果有多个用户，优先选择同部门的
        eligible_users = [a.user for a in assignments if a.user and a.user.is_active]
        
        if eligible_users:
            # 如果提供了部门，尝试匹配部门
            if department_name:
                same_dept_users = [u for u in eligible_users if u.department == department_name]
                if same_dept_users:
                    return same_dept_users[0].id
            
            # 返回第一个可用用户
            return eligible_users[0].id
    
    # 2. Fallback到旧的role_required逻辑（兼容性）
    if node.role_required == 'department_head' or node.role_required == '部门负责人':
        user = User.query.filter_by(
            role='department_head',
            department=department_name
        ).first()
        if user:
            return user.id
        # 如果没有找到部门负责人，尝试查找该部门的任何管理员
        user = User.query.filter_by(
            role='admin',
            department=department_name
        ).first()
        return user.id if user else None
    elif node.role_required == 'admin' or node.role_required == '系统管理员':
        user = User.query.filter_by(role='admin').first()
        return user.id if user else None
    elif node.role_required == 'technician' or node.role_required == '技术员':
        user = User.query.filter_by(
            role='technician',
            department=department_name
        ).first()
        return user.id if user else None
    
    return None


@bp.route('/approvals/part_order/<int:order_id>/<action>', methods=['POST'])
@login_required
def approve_part_order(order_id, action):
    """审批配件申请工单"""
    try:
        # 获取审批记录 - 管理员可以审批任何待审批的工单
        if current_user.role in ['admin', 'super_admin']:
            approval = ApprovalWorkflow.query.filter_by(
                order_type='part_request_order',
                order_id=order_id,
                status='pending'
            ).first_or_404()
        else:
            approval = ApprovalWorkflow.query.filter_by(
                order_type='part_request_order',
                order_id=order_id,
                approver_id=current_user.id,
                status='pending'
            ).first_or_404()
        
        # 获取工单
        part_order = PartRequestOrder.query.get_or_404(order_id)
        
        if action == 'approve':
            # 更新审批状态
            approval.status = 'approved'
            approval.approved_date = datetime.now(timezone.utc)
            approval.comments = request.form.get('comments', '')
            
            # 根据审批级别更新工单状态
            if approval.approval_level == 'department_head':
                part_order.department_head_approved = True
                part_order.department_head_id = current_user.id
                part_order.status = 'department_head_approved'
                    
            elif approval.approval_level == 'admin':
                part_order.admin_approved = True
                part_order.admin_id = current_user.id
                part_order.status = 'admin_approved'
            
            # 检查是否还有后续审批节点
            next_node = get_next_approval_node('part_request_order', part_order.id)
            if next_node:
                next_approval = ApprovalWorkflow(
                    order_type='part_request_order',
                    order_id=part_order.id,
                    approver_id=get_approver_id(next_node, part_order.requester.department if part_order.requester else None),
                    approval_level=next_node.role_required,
                    node_id=next_node.id,
                    status='pending'
                )
                db.session.add(next_approval)
            else:
                # 所有审批完成 - 使用悲观锁扣减库存
                part_order.status = 'approved'
                part_order.completed_date = get_beijing_now()
                
                # 查找配件并使用 SELECT FOR UPDATE 锁定
                spare_part = None
                if part_order.part_number:
                    spare_part = db.session.query(SparePart).with_for_update().filter_by(
                        part_number=part_order.part_number
                    ).first()
                if not spare_part and part_order.part_name:
                    spare_part = db.session.query(SparePart).with_for_update().filter_by(
                        name=part_order.part_name
                    ).first()
                
                if spare_part:
                    # 检查库存是否充足
                    if spare_part.stock_quantity < part_order.quantity:
                        raise ValueError(f'库存不足! 配件 {spare_part.name} 当前库存: {spare_part.stock_quantity}, 需求: {part_order.quantity}')
                    
                    # 扣减库存
                    spare_part.stock_quantity -= part_order.quantity
                    _log_activity('减少配件库存', f'配件申请 #{part_order.id} 审批完成，减少 {spare_part.name} 库存 {part_order.quantity} 个')
                    
                    # 检查低库存预警
                    if hasattr(spare_part, 'low_stock_threshold') and spare_part.low_stock_threshold:
                        if spare_part.stock_quantity <= spare_part.low_stock_threshold:
                            admins = User.query.filter_by(role='admin').all()
                            for admin in admins:
                                warning_notification = Notification(
                                    user_id=admin.id,
                                    title='配件库存预警',
                                    message=f'配件 {spare_part.name} 库存不足,当前库存: {spare_part.stock_quantity}'
                                )
                                db.session.add(warning_notification)
                
            _log_activity('审批配件申请', f'用户 {current_user.username} 批准了配件申请 #{part_order.id} (配件: {part_order.part_name}, 数量: {part_order.quantity})')
                
            # 创建通知给申请人
            notification = Notification(
                user_id=part_order.requester_id,
                title='配件申请审批完成' if part_order.status == 'approved' else '配件申请审批状态更新',
                message=f'您的配件申请 #{part_order.id} 已被 {current_user.username} 批准' + ('，库存已减少' if part_order.status == 'approved' else ''),
                order_type='part_request_order',
                order_id=part_order.id
            )
            db.session.add(notification)
                
            db.session.commit()
            flash('配件申请审批成功', 'success')
            
        elif action == 'reject':
            # 拒绝工单
            approval.status = 'rejected'
            approval.approved_date = datetime.now(timezone.utc)
            approval.comments = request.form.get('comments', '')
            
            # 更新工单状态
            part_order.status = 'cancelled'
            
            _log_activity('审批配件申请', f'用户 {current_user.username} 拒绝了配件申请 #{part_order.id} (配件: {part_order.part_name}, 数量: {part_order.quantity})')
            
            # 创建通知给申请人
            notification = Notification(
                user_id=part_order.requester_id,
                title='配件申请被拒绝',
                message=f'您的配件申请 #{part_order.id} 已被 {current_user.username} 拒绝',
                order_type='part_request_order',
                order_id=part_order.id
            )
            db.session.add(notification)
            
            db.session.commit()
            flash('配件申请已拒绝', 'info')
    
    except ValueError as e:
        # 业务逻辑错误 (如库存不足)
        db.session.rollback()
        flash(str(e), 'danger')
        return redirect(url_for('main.approvals'))
    
    except Exception as e:
        # 其他未知错误
        db.session.rollback()
        current_app.logger.error(f'配件申请审批失败: {e}', exc_info=True)
        flash('操作失败,请联系管理员', 'danger')
        return redirect(url_for('main.approvals'))
        
    return redirect(url_for('main.approvals'))


@bp.route('/admin/workflow_nodes')
@login_required
def admin_workflow_nodes():
    """审批流程节点管理 - 重定向到按类型配置"""
    return redirect(url_for('main.workflow_config_by_type'))


@bp.route('/admin/workflow_config', defaults={'order_type': None})
@bp.route('/admin/workflow_config/<order_type>')
@login_required
def workflow_config_by_type(order_type=None):
    """按工单类型配置审批流程"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    # 工单类型定义
    order_types = {
        'repair_order': {
            'name': '维修工单',
            'icon': 'fa-wrench',
            'description': '设备故障维修申请'
        },
        'part_request_order': {
            'name': '配件申请',
            'icon': 'fa-box',
            'description': '配件领用申请'
        },
        'equipment_application': {
            'name': '设备申请',
            'icon': 'fa-laptop',
            'description': '新设备申请'
        },
        'equipment_loan': {
            'name': '设备借用',
            'icon': 'fa-handshake',
            'description': '设备临时借用'
        },
        'equipment_transfer': {
            'name': '设备调拨',
            'icon': 'fa-truck',
            'description': '设备部门间调拨'
        },
        'equipment_scrap': {
            'name': '设备报废',
            'icon': 'fa-trash-alt',
            'description': '设备报废处理'
        }
    }
    
    # 统计每个工单类型的审批节点数量
    workflow_stats = {}
    for type_key in order_types.keys():
        count = WorkflowNode.query.join(WorkflowTemplate).filter(
            WorkflowTemplate.order_type == type_key,
            WorkflowNode.is_active == True
        ).count()
        workflow_stats[type_key] = count
    
    # 如果指定了工单类型，获取该类型的审批节点
    nodes = []
    next_sequence = 1
    if order_type and order_type in order_types:
        nodes = WorkflowNode.query.join(WorkflowTemplate).filter(
            WorkflowTemplate.order_type == order_type,
            WorkflowNode.is_active == True
        ).order_by(WorkflowNode.sequence).all()
        
        # 计算下一个序号
        if nodes:
            next_sequence = max([n.sequence for n in nodes]) + 1
    
    # 获取所有用户（用于指定审批人）
    users = User.query.order_by(User.username).all()
    
    # 角色名称映射
    def get_role_name(role):
        role_map = {
            'user': '普通用户',
            'employee': '普通员工',
            'department_head': '部门负责人',
            'admin': '管理员',
            'technician': '技术员',
            'procurement': '采购专员',
            'warehouse': '仓库管理员',
            'security': '信息安全员',
            'finance': '财务审批人',
            'executive': '高层管理者',
            'auditor': '审计员'
        }
        return role_map.get(role, role)
    
    return render_template('main/workflow_config_by_type.html',
                         title='审批流程配置',
                         order_types=order_types,
                         workflow_stats=workflow_stats,
                         selected_type=order_type,
                         nodes=nodes,
                         users=users,
                         next_sequence=next_sequence,
                         get_role_name=get_role_name)


@bp.route('/admin/workflow_help')
@login_required
def admin_workflow_help():
    """工作流配置帮助页面"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    return render_template('main/admin_workflow_help.html', title='工作流配置帮助')


@bp.route('/part_request_orders')
@login_required
def part_request_orders():
    # 获取筛选参数
    filter_type = request.args.get('filter', 'all')
    
    # 根据用户角色和筛选条件确定查询条件
    # 准备不同视图所需的数据结构，模板期望 orders.pending / orders.my / orders.all
    orders_data = {
        'pending': [],
        'my': [],
        'all': []
    }
    
    # 待审批（管理员或部门领导可见）——使用 status='submitted' 作为待审批标识
    if current_user.role in ['admin', 'department_head']:
        if filter_type == 'all' or not filter_type:
            orders_data['pending'] = PartRequestOrder.query.filter_by(status='submitted').order_by(PartRequestOrder.created_date.desc()).all()
        else:
            orders_data['pending'] = PartRequestOrder.query.filter_by(status=filter_type).order_by(PartRequestOrder.created_date.desc()).all()
    
    # 我的申请
    orders_data['my'] = PartRequestOrder.query.filter_by(requester_id=current_user.id).order_by(PartRequestOrder.created_date.desc()).all()
    
    # 所有申请（仅管理员可见）
    if current_user.role == 'admin':
        orders_data['all'] = PartRequestOrder.query.order_by(PartRequestOrder.created_date.desc()).all()
    
    # 如果是Ajax请求，只返回表格部分（兼容旧的局部刷新）
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('main/part_request_orders_table.html', orders=orders_data)
    
    return render_template('main/part_request_orders.html', title='配件申请工单', orders=orders_data)


@bp.route('/part_request_orders/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_part_request_order(id):
    """编辑配件申请工单"""
    order = PartRequestOrder.query.get_or_404(id)
    
    # 权限检查：只有申请人或管理员可以编辑
    if current_user.role != 'admin' and order.requester_id != current_user.id:
        flash('您没有权限编辑此申请', 'danger')
        return redirect(url_for('main.part_request_orders'))
    
    if request.method == 'POST':
        part_name = request.form.get('part_name')
        part_number = request.form.get('part_number')
        quantity = request.form.get('quantity', type=int)
        reason = request.form.get('reason')
        new_status = request.form.get('status')
        
        if not all([part_name, part_number, quantity, reason]):
            flash('请填写所有必填字段', 'danger')
            return render_template('main/edit_part_request_order.html', 
                                 title='编辑配件申请', 
                                 order=order)
        
        if quantity <= 0:
            flash('数量必须大于0', 'danger')
            return render_template('main/edit_part_request_order.html', 
                                 title='编辑配件申请', 
                                 order=order)
        
        # 更新申请信息
        old_status = order.status
        order.part_name = part_name
        order.part_number = part_number
        order.quantity = quantity
        order.reason = reason
        order.status = new_status
        order.updated_date = get_beijing_now()
        
        # 如果状态变为已完成，记录完成时间
        if new_status in ['completed', 'approved'] and old_status not in ['completed', 'approved']:
            order.completed_date = get_beijing_now()
        
        # 如果从已完成改为其他状态，清除完成时间
        if old_status in ['completed', 'approved'] and new_status not in ['completed', 'approved']:
            order.completed_date = None
        
        db.session.commit()
        
        status_text = {
            'submitted': '待审批',
            'department_head_approved': '部门领导已批准',
            'admin_approved': '管理员已批准',
            'completed': '已完成',
            'approved': '已完成',
            'cancelled': '已取消'
        }
        
        _log_activity('编辑配件申请', 
                     f'编辑配件申请 #{order.id} - {part_name}, '
                     f'状态: {status_text.get(old_status, old_status)} -> {status_text.get(new_status, new_status)}')
        
        flash('配件申请更新成功', 'success')
        return redirect(url_for('main.part_request_order_detail', id=id))
    
    return render_template('main/edit_part_request_order.html', 
                         title='编辑配件申请', 
                         order=order)


@bp.route('/part_request_orders/<int:id>/delete', methods=['POST'])
@login_required
def delete_part_request_order(id):
    """删除配件申请工单"""
    order = PartRequestOrder.query.get_or_404(id)
    
    # 权限检查：只有申请人或管理员可以删除
    if current_user.role != 'admin' and order.requester_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限删除此申请'})
    
    # 只允许删除已提交或已取消状态的申请
    if order.status not in ['submitted', 'cancelled']:
        return jsonify({'success': False, 'message': '只能删除待审批或已取消状态的申请'})
    
    part_name = order.part_name
    order_id = order.id
    
    db.session.delete(order)
    db.session.commit()
    
    _log_activity('删除配件申请', f'删除配件申请 #{order_id} - {part_name}')
    
    return jsonify({'success': True, 'message': '配件申请删除成功'})


@bp.route('/admin/transfers')
@login_required
def admin_transfers():
    """管理员查看所有设备调拨申请"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))

    status = request.args.get('status', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = EquipmentTransfer.query
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(EquipmentTransfer.created_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        'main/admin_transfers.html',
        title='设备调拨管理',
        transfers=pagination,
        selected_status=status
    )

@bp.route('/admin/scraps')
@login_required
def admin_scraps():
    """管理员查看所有设备报废申请"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))

    scraps = EquipmentScrap.query.order_by(EquipmentScrap.created_date.desc()).all()
    
    # 为每个报废申请加载审批流程
    for scrap in scraps:
        scrap.approvals = ApprovalWorkflow.query.filter_by(
            order_type='equipment_scrap',
            order_id=scrap.id
        ).order_by(ApprovalWorkflow.created_date).all()
    
    return render_template('main/admin_scraps.html', title='设备报废管理', scraps=scraps)


@bp.route('/admin/workflow_nodes/add', methods=['GET', 'POST'])
@login_required
def add_workflow_node():
    """添加审批流程节点"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '您没有权限执行此操作'}), 403
    
    if request.method == 'POST':
        name = request.form.get('name')
        order_type = request.form.get('order_type')
        role_required = request.form.get('role_required')
        sequence = request.form.get('sequence')
        
        # 定义支持的角色类型
        supported_roles = ['admin', 'department_head', 'technician']
        
        # 验证数据
        if not name or not order_type or not role_required or not sequence:
            return jsonify({'success': False, 'message': '请填写所有必填字段'})
            
        # 验证角色是否为支持的角色类型
        if role_required not in supported_roles:
            return jsonify({'success': False, 'message': '请选择有效的审批角色'})
        
        try:
            sequence = int(sequence)
        except ValueError:
            return jsonify({'success': False, 'message': '顺序必须是数字'})
        
        # 处理可选的指定审批人（多选）
        approver_ids = request.form.getlist('approver_user_ids') or []
        # 过滤空值并转换为 int
        approver_ids = [int(i) for i in approver_ids if i]

        # 创建节点
        node = WorkflowNode(name=name, order_type=order_type, role_required=role_required, sequence=sequence)

        if approver_ids:
            import json
            node.approver_user_ids = json.dumps(approver_ids)
            node.is_parallel = True if len(approver_ids) > 1 else False
            node.required_approvals = len(approver_ids)
            # 若只指定了一个审批人，也设置 approver_user_id 以兼容旧逻辑
            if len(approver_ids) == 1:
                node.approver_user_id = approver_ids[0]

        db.session.add(node)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '审批节点添加成功'})
    
    return render_template('main/add_workflow_node.html', title='添加审批节点')


@bp.route('/admin/workflow_nodes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_workflow_node(id):
    """编辑审批流程节点"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '您没有权限执行此操作'}), 403
    
    node = WorkflowNode.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        order_type = request.form.get('order_type')
        role_required = request.form.get('role_required')
        sequence = request.form.get('sequence')
        
        # 验证数据
        if not name or not order_type or not role_required or not sequence:
            return jsonify({'success': False, 'message': '请填写所有必填字段'})
        
        try:
            sequence = int(sequence)
        except ValueError:
            return jsonify({'success': False, 'message': '顺序必须是数字'})
        
        # 处理可选的指定审批人（多选）
        approver_ids = request.form.getlist('approver_user_ids') or []
        approver_ids = [int(i) for i in approver_ids if i]

        # 更新节点
        node.name = name
        # order_type 通过 template 管理，不能直接修改
        # node.order_type = order_type
        node.role_required = role_required
        node.sequence = sequence

        if approver_ids:
            import json
            node.approver_user_ids = json.dumps(approver_ids)
            node.is_parallel = True if len(approver_ids) > 1 else False
            node.required_approvals = len(approver_ids)
            node.approver_user_id = approver_ids[0] if len(approver_ids) >= 1 else None
        else:
            node.approver_user_ids = None
            node.is_parallel = False
            node.required_approvals = 1
            node.approver_user_id = None

        db.session.commit()
        
        return jsonify({'success': True, 'message': '审批节点更新成功'})
    
    return render_template('main/edit_workflow_node.html', title='编辑审批节点', node=node)


@bp.route('/admin/workflow_nodes/delete/<int:id>', methods=['POST'])
@login_required
def delete_workflow_node(id):
    """删除审批流程节点"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '您没有权限执行此操作'}), 403
    
    node = WorkflowNode.query.get_or_404(id)
    
    db.session.delete(node)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '审批节点删除成功'})


@bp.route('/user_activity_logs')
@login_required
def user_activity_logs():
    if current_user.role != 'admin' and not getattr(current_user, 'can_view_logs', False):
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    # 获取筛选参数
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    
    # 构建查询
    query = UserActivityLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if action:
        query = query.filter(UserActivityLog.action.like(f'%{action}%'))
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(UserActivityLog.timestamp >= start_dt)
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            # 包含结束日期当天的所有记录
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(UserActivityLog.timestamp <= end_dt)
        except ValueError:
            pass
    
    # 分页查询
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    logs = query.order_by(UserActivityLog.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    def _build_link(desc):
        if not desc:
            return None
        try:
            import re
            m = re.search(r"(维修工单|配件申请|设备申请)\s*#(\d+)", desc)
            if not m:
                return None
            typ = m.group(1)
            oid = int(m.group(2))
            if typ == '维修工单':
                return url_for('main.repair_order_detail', id=oid)
            elif typ == '配件申请':
                return url_for('main.part_request_order_detail', id=oid)
            elif typ == '设备申请':
                return url_for('main.approvals')
        except Exception:
            return None
        return None
    log_links = {l.id: _build_link(l.description or '') for l in logs.items}
    
    # 获取所有用户用于筛选下拉框
    users = User.query.order_by(User.username).all()
    
    # 获取所有操作类型用于筛选
    actions = db.session.query(UserActivityLog.action).distinct().order_by(UserActivityLog.action).all()
    action_list = [a[0] for a in actions if a[0]]
    
    return render_template('main/user_activity_logs.html', title='用户活动日志', logs=logs, users=users, action_list=action_list, selected_user_id=user_id, selected_action=action, start_date=start_date, end_date=end_date, log_links=log_links)


@bp.route('/user_activity_logs/export')
@login_required
def export_user_activity_logs():
    """导出用户活动日志为CSV格式"""
    if current_user.role != 'admin' and not getattr(current_user, 'can_view_logs', False):
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    # 获取筛选参数（与列表页面相同）
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    
    # 构建查询（与列表页面相同）
    query = UserActivityLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if action:
        query = query.filter(UserActivityLog.action.like(f'%{action}%'))
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(UserActivityLog.timestamp >= start_dt)
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(UserActivityLog.timestamp <= end_dt)
        except ValueError:
            pass
    
    logs = query.order_by(UserActivityLog.timestamp.desc()).all()
    
    # 创建CSV数据
    import csv
    import io
    from flask import Response
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow(['用户名', '操作', '描述', '时间'])
    
    # 写入数据
    for log in logs:
        writer.writerow([
            log.user.username if log.user else '未知用户',
            log.action,
            log.description or '',
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    
    # 生成文件名
    filename = f'用户活动日志_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': content_disposition(filename, 'user_activity_logs.csv')}
    )


@bp.route('/workflow_nodes')
@login_required
def workflow_nodes():
    if current_user.role != 'admin' and not getattr(current_user, 'can_view_workflow', False):
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    # 按序号排序，不再按order_type排序（WorkflowNode没有此字段）
    nodes = WorkflowNode.query.join(WorkflowTemplate).order_by(
        WorkflowTemplate.order_type, 
        WorkflowNode.sequence
    ).all()
    # 为了让非管理员入口也能在编辑/添加时选择指定审批人，传入 users 列表
    users = []
    try:
        users = User.query.order_by(User.username).all()
    except Exception:
        users = []

    # 计算同步对（与 WorkflowTemplate 中的步骤对比），和管理员入口保持一致
    synced_pairs = set()
    try:
        templates = WorkflowTemplate.query.filter_by(is_active=True).all()
        for tpl in templates:
            for step in tpl.steps:
                synced_pairs.add((tpl.order_type, step.step_name))
    except Exception:
        synced_pairs = set()

    return render_template('main/workflow_nodes.html', title='审批流程管理', nodes=nodes, users=users, synced_pairs=synced_pairs)


@bp.route('/user_history')
@login_required
def user_history():
    # 获取当前用户的历史记录
    user_id = current_user.id
    
    # 分页查询用户相关的历史工单
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 查询用户创建的工单
    created_orders = RepairOrder.query.filter_by(requester_id=user_id)\
        .order_by(RepairOrder.created_date.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('main/user_history.html', 
                          title='我的历史记录',
                          orders=created_orders)


@bp.route('/part_request_orders/<int:id>')
@login_required
def part_request_order_detail(id):
    order = PartRequestOrder.query.get_or_404(id)
    
    # 检查权限
    if current_user.role == 'user' and order.requester_id != current_user.id:
        flash('您没有权限查看此工单')
        return redirect(url_for('main.part_request_orders'))
    
    # 获取当前订单的下一个待处理审批（如果有）
    next_approval = _get_next_pending_approval('part_request_order', order.id)
    approval_for_user = None
    can_approve = False
    if next_approval:
        # 如果当前用户是该审批的处理人，则允许在详情页审批
        if next_approval.approver_id == current_user.id:
            approval_for_user = next_approval
            # 确保这是最早的待审批节点（防止并发绕过顺序）
            can_approve = _is_earliest_pending(next_approval)

    return render_template('main/part_request_order_detail.html', title='工单详情', order=order, approval=approval_for_user, can_approve=can_approve)


@bp.route('/create_part_request_order', methods=['GET', 'POST'])
@login_required
def create_part_request_order():
    """创建配件申请工单"""
    # 管理员和具有配件申请权限的用户都可以创建
    if current_user.role != 'admin' and not getattr(current_user, 'can_manage_part_requests', False):
        flash('您没有权限创建配件申请')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        part_name = request.form.get('part_name')
        part_number = request.form.get('part_number')
        quantity = int(request.form.get('quantity', 1))
        reason = request.form.get('reason')
        
        # 验证数据
        if not part_name or not reason:
            flash('请填写所有必填字段')
            # 根据用户权限获取可申请的配件列表
            if current_user.role == 'admin':
                spare_parts = SparePart.query.order_by(SparePart.name).all()
            elif current_user.department_id:
                spare_parts = SparePart.query.filter(
                    or_(
                        SparePart.department_id == current_user.department_id,
                        SparePart.is_public == True
                    )
                ).order_by(SparePart.name).all()
            else:
                spare_parts = SparePart.query.filter_by(is_public=True).order_by(SparePart.name).all()
            
            return render_template('main/create_part_request_order.html', 
                                 title='创建配件申请', 
                                 spare_parts=spare_parts)
        
        # 创建新的配件申请工单
        try:
            part_request_order = PartRequestOrder(
                requester_id=current_user.id,
                part_name=part_name,
                part_number=part_number,
                quantity=quantity,
                reason=reason
            )

            db.session.add(part_request_order)
            db.session.flush()

            # 创建审批链:优先使用配置的 WorkflowNode;如果未配置,则使用回退流程(部门负责人 -> 管理员)
            nodes = WorkflowNode.query.join(WorkflowTemplate).filter(
                WorkflowTemplate.order_type == 'part_request_order',
                WorkflowNode.is_active == True
            ).order_by(WorkflowNode.sequence).all()
            if nodes:
                steps = []
                for node in nodes:
                    dept_specific = getattr(node, 'department_specific', False)
                    dept_name = current_user.department if (dept_specific and current_user.department) else None
                    steps.append((node.role_required, dept_name))
            else:
                # 回退流程,如果用户有部门则需要部门负责人审批
                if current_user.department:
                    steps = [
                        ('department_head', current_user.department),
                        ('admin', None)
                    ]
                else:
                    # 无部门用户直接由admin审批
                    steps = [('admin', None)]

            _create_sequenced_approvals('part_request_order', part_request_order.id, steps)

            db.session.commit()

            # 记录用户创建配件申请活动
            activity_log = UserActivityLog(
                user_id=current_user.id,
                action='创建配件申请',
                description=f'用户 {current_user.username} 创建了配件申请 #{part_request_order.id}'
            )
            db.session.add(activity_log)

            # 创建通知给管理员和部门领导
            admins = User.query.filter_by(role='admin').all()
            # 只有用户有部门时才查找部门负责人
            if current_user.department:
                department_heads = User.query.filter_by(role='department_head', department=current_user.department).all()
            else:
                department_heads = []

            # 给所有管理员发送通知
            for admin in admins:
                notification = Notification(
                    user_id=admin.id,
                    title='新配件申请',
                    message=f'用户 {current_user.username} 提交了新的配件申请 #{part_request_order.id}'
                )
                db.session.add(notification)

            # 给部门领导发送通知
            for department_head in department_heads:
                notification = Notification(
                    user_id=department_head.id,
                    title='新配件申请',
                    message=f'用户 {current_user.username} 提交了新的配件申请 #{part_request_order.id}'
                )
                db.session.add(notification)

            db.session.commit()

            flash('配件申请提交成功')
            return redirect(url_for('main.part_request_orders'))
        except Exception as e:
            db.session.rollback()
            flash('提交申请失败：' + str(e))

    # GET请求或失败后显示配件选择
    # 根据用户权限显示不同的配件:
    # - admin: 所有配件
    # - 本部门用户: 本部门配件 + 公开配件
    # - 其他用户: 仅公开配件
    if current_user.role == 'admin':
        # 管理员可以看到所有配件
        spare_parts = SparePart.query.order_by(SparePart.name).all()
    elif current_user.department_id:
        # 本部门用户可以看到本部门的配件和公开配件
        spare_parts = SparePart.query.filter(
            or_(
                SparePart.department_id == current_user.department_id,
                SparePart.is_public == True
            )
        ).order_by(SparePart.name).all()
    else:
        # 其他用户只能看到公开配件
        spare_parts = SparePart.query.filter_by(is_public=True).order_by(SparePart.name).all()
    
    return render_template('main/create_part_request_order.html', 
              title='提交配件申请', 
              spare_parts=spare_parts)


@bp.route('/part_request_history')
@login_required
def part_request_history():
    # 获取当前用户的历史配件申请
    user_id = current_user.id
    
    # 分页查询用户相关的配件申请单
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 查询用户创建的配件申请单（使用 PartRequestOrder）
    requests = PartRequestOrder.query.filter_by(requester_id=user_id)\
        .order_by(PartRequestOrder.created_date.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('main/part_request_history.html', 
                          title='配件申请历史',
                          requests=requests)


@bp.route('/reports')
@login_required
def reports():
    if current_user.role != 'admin' and not getattr(current_user, 'can_view_reports', False):
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    # 获取统计信息
    total_users = User.query.count()
    total_equipment = Equipment.query.count()
    total_repair_orders = RepairOrder.query.count()
    total_spare_parts = SparePart.query.count()
    
    # 按状态统计设备
    equipment_by_status = db.session.query(
        Equipment.status,
        func.count(Equipment.id).label('count')
    ).group_by(Equipment.status).all()
    
    # 按类型统计设备
    equipment_by_type = db.session.query(
        Equipment.type,
        func.count(Equipment.id).label('count')
    ).group_by(Equipment.type).all()
    
    # 按部门统计设备
    equipment_by_department = db.session.query(
        Equipment.department,
        func.count(Equipment.id).label('count')
    ).group_by(Equipment.department).all()
    
    # 按状态统计维修工单
    repair_orders_by_status = db.session.query(
        RepairOrder.status,
        func.count(RepairOrder.id).label('count')
    ).group_by(RepairOrder.status).all()
    
    # 按描述关键词统计维修工单（替换原来的优先级统计）
    repair_orders_by_description = db.session.query(
        func.substr(RepairOrder.description, 1, 20).label('description'),
        func.count(RepairOrder.id).label('count')
    ).group_by(func.substr(RepairOrder.description, 1, 20)).all()
    
    # 设备调拨统计
    from app.models import EquipmentTransfer
    total_transfers = EquipmentTransfer.query.count()
    transfers_by_status = db.session.query(
        EquipmentTransfer.status,
        func.count(EquipmentTransfer.id).label('count')
    ).group_by(EquipmentTransfer.status).all()
    
    # 设备报废统计
    from app.models import EquipmentScrap
    total_scraps = EquipmentScrap.query.count()
    scraps_by_status = db.session.query(
        EquipmentScrap.status,
        func.count(EquipmentScrap.id).label('count')
    ).group_by(EquipmentScrap.status).all()
    
    # 设备借用统计
    from app.models import EquipmentLoan
    total_loans = EquipmentLoan.query.count()
    loans_by_status = db.session.query(
        EquipmentLoan.status,
        func.count(EquipmentLoan.id).label('count')
    ).group_by(EquipmentLoan.status).all()
    
    # 配件申请统计
    total_part_requests = PartRequestOrder.query.count()
    part_requests_by_status = db.session.query(
        PartRequestOrder.status,
        func.count(PartRequestOrder.id).label('count')
    ).group_by(PartRequestOrder.status).all()
    
    return render_template('main/reports.html', 
                          title='统计报表',
                          total_users=total_users,
                          total_equipment=total_equipment,
                          total_repair_orders=total_repair_orders,
                          total_spare_parts=total_spare_parts,
                          equipment_by_status=equipment_by_status,
                          equipment_by_type=equipment_by_type,
                          equipment_by_department=equipment_by_department,
                          repair_orders_by_status=repair_orders_by_status,
                          repair_orders_by_description=repair_orders_by_description,
                          total_transfers=total_transfers,
                          transfers_by_status=transfers_by_status,
                          total_scraps=total_scraps,
                          scraps_by_status=scraps_by_status,
                          total_loans=total_loans,
                          loans_by_status=loans_by_status,
                          total_part_requests=total_part_requests,
                          part_requests_by_status=part_requests_by_status)


@bp.route('/reports/export')
@login_required
def export_report():
    report_type = request.args.get('type', 'summary')
    if report_type == 'equipment':
        if current_user.role not in ['admin', 'technician']:
            flash('您没有权限访问此页面')
            return redirect(url_for('main.index'))
    else:
        if current_user.role != 'admin':
            flash('您没有权限访问此页面')
            return redirect(url_for('main.index'))
    
    
    # 创建CSV数据
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    if report_type == 'equipment':
        # 获取筛选参数
        type_id = request.args.get('type_id', type=int)
        department_id = request.args.get('department_id', type=int)
        status = request.args.get('status', '').strip()
        
        # 构建查询
        query = Equipment.query
        if type_id:
            query = query.filter_by(type_id=type_id)
        if department_id:
            query = query.filter_by(department_id=department_id)
        if status:
            query = query.filter_by(status=status)
        
        # 导出设备报表
        writer.writerow(['设备名称', '类型', '品牌', '型号', '序列号', '所属部门', '状态', '价格', '购买日期'])
        equipments = query.all()
        for eq in equipments:
            writer.writerow([
                eq.name, 
                eq.type or (eq.equipment_type.name if eq.equipment_type else ''), 
                eq.brand or '', 
                eq.model or '', 
                eq.serial_number, 
                eq.department or '', 
                _status_label('equipment', eq.status or 'active'),
                # include price and purchase_date
                (float(eq.price) if getattr(eq, 'price', None) is not None else 0.0),
                eq.purchase_date.strftime('%Y-%m-%d') if eq.purchase_date else ''
            ])
        filename = f'设备报表_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    elif report_type == 'users':
        # 导出用户报表
        writer.writerow(['用户名', '邮箱', '角色', '所属部门'])
        users = User.query.all()
        for user in users:
            writer.writerow([user.username, user.email, user.role, user.department])
        filename = f'用户报表_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    elif report_type == 'repair_orders':
        # 获取筛选参数
        filter_type = request.args.get('filter', '').strip()
        user_id = request.args.get('user_id', type=int)
        
        # 构建查询
        query = RepairOrder.query
        if filter_type and filter_type != 'all':
            query = query.filter_by(status=filter_type)
        if user_id:
            query = query.filter_by(requester_id=user_id)
        
        # 导出维修工单报表
        writer.writerow(['工单ID', '设备名称', '申请人', '技术员', '故障描述', '状态', '创建日期', '完成日期'])
        orders = query.order_by(RepairOrder.created_date.desc()).all()
        for order in orders:
            writer.writerow([
                order.id, 
                order.equipment.name if order.equipment else '',
                order.requester.username if order.requester else '',
                order.technician.username if order.technician else '',
                order.description or '',
                _status_label('repair_order', order.status or 'submitted'),
                order.created_date.strftime('%Y-%m-%d %H:%M:%S') if order.created_date else '',
                order.completed_date.strftime('%Y-%m-%d %H:%M:%S') if order.completed_date else ''
            ])
        filename = f'维修工单报表_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    elif report_type == 'transfers':
        # 导出设备调拨报表
        from app.models import EquipmentTransfer
        writer.writerow(['调拨ID', '设备名称', '调出部门', '调入部门', '申请人', '状态', '创建日期'])
        transfers = EquipmentTransfer.query.order_by(EquipmentTransfer.created_date.desc()).all()
        for transfer in transfers:
            writer.writerow([
                transfer.id,
                transfer.equipment.name if transfer.equipment else '',
                transfer.from_department or '',
                transfer.to_department or '',
                transfer.requester.username if transfer.requester else '',
                _status_label('transfer', transfer.status or 'submitted'),
                transfer.created_date.strftime('%Y-%m-%d %H:%M:%S') if transfer.created_date else ''
            ])
        filename = f'设备调拨报表_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    elif report_type == 'scraps':
        # 导出设备报废报表
        from app.models import EquipmentScrap
        writer.writerow(['报废ID', '设备名称', '申请部门', '申请人', '状态', '创建日期'])
        scraps = EquipmentScrap.query.order_by(EquipmentScrap.created_date.desc()).all()
        for scrap in scraps:
            writer.writerow([
                scrap.id,
                scrap.equipment.name if scrap.equipment else '',
                scrap.requester.department if scrap.requester else (scrap.equipment.department if scrap.equipment else ''),
                scrap.requester.username if scrap.requester else '',
                _status_label('scrap', scrap.status or 'submitted'),
                scrap.created_date.strftime('%Y-%m-%d %H:%M:%S') if scrap.created_date else ''
            ])
        filename = f'设备报废报表_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    elif report_type == 'loans':
        # 导出设备借用报表
        from app.models import EquipmentLoan
        writer.writerow(['借用ID', '设备名称', '借用人', '借用人部门', '开始日期', '结束日期', '状态', '创建日期'])
        loans = EquipmentLoan.query.order_by(EquipmentLoan.created_date.desc()).all()
        for loan in loans:
            writer.writerow([
                loan.id,
                loan.equipment.name if loan.equipment else '',
                loan.requester.username if loan.requester else '',
                loan.requester_dept or '',
                loan.start_date.strftime('%Y-%m-%d %H:%M:%S') if loan.start_date else '',
                loan.end_date.strftime('%Y-%m-%d %H:%M:%S') if loan.end_date else '',
                _status_label('loan', loan.status or 'submitted'),
                loan.created_date.strftime('%Y-%m-%d %H:%M:%S') if loan.created_date else ''
            ])
        filename = f'设备借用报表_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    elif report_type == 'part_requests':
        # 导出配件申请报表
        writer.writerow(['申请ID', '配件名称', '配件编号', '数量', '申请人', '状态', '创建日期'])
        part_requests = PartRequestOrder.query.order_by(PartRequestOrder.created_date.desc()).all()
        for pr in part_requests:
            writer.writerow([
                pr.id,
                pr.part_name or '',
                pr.part_number or '',
                pr.quantity or 0,
                pr.requester.username if pr.requester else '',
                _status_label('part_request', pr.status or 'submitted'),
                pr.created_date.strftime('%Y-%m-%d %H:%M:%S') if pr.created_date else ''
            ])
        filename = f'配件申请报表_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    else:
        # 导出汇总报表
        from app.models import EquipmentTransfer, EquipmentScrap, EquipmentLoan
        writer.writerow(['统计项', '数量'])
        writer.writerow(['用户总数', User.query.count()])
        writer.writerow(['设备总数', Equipment.query.count()])
        writer.writerow(['维修工单总数', RepairOrder.query.count()])
        writer.writerow(['配件总数', SparePart.query.count()])
        writer.writerow(['设备调拨总数', EquipmentTransfer.query.count()])
        writer.writerow(['设备报废总数', EquipmentScrap.query.count()])
        writer.writerow(['设备借用总数', EquipmentLoan.query.count()])
        writer.writerow(['配件申请总数', PartRequestOrder.query.count()])
        filename = f'汇总报表_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    # 返回CSV文件
    from flask import Response
    csv_data = output.getvalue()
    output.close()
    
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': content_disposition(filename, 'report.csv')}
    )


# ------------------------- 设备调拨 / 报废 流程支持 -------------------------
def _get_user_for_role(role, department_name=None):
    """Return a user id for given role and optional department (first match) or None."""
    if role == 'admin':
        user = User.query.filter_by(role='admin').first()
        return user.id if user else None
    elif role == 'department_head' and department_name:
        user = User.query.filter_by(role='department_head', department=department_name).first()
        return user.id if user else None
    elif role == 'technician' and department_name:
        user = User.query.filter_by(role='technician', department=department_name).first()
        return user.id if user else None
    return None


def _create_sequenced_approvals(order_type, order_id, steps):
    """Create ApprovalWorkflow entries in order. steps is list of (approval_level, department_name_or_None).
    We set created_date offsets to preserve ordering.
    """
    now = get_beijing_now()
    approvals = []
    for i, (level, dept) in enumerate(steps):
        approver = _get_user_for_role(level, dept)
        auto_assigned = False
        # 如果未找到匹配的 approver，尝试使用 config 中配置的回退管理员邮箱；否则使用第一个 admin
        if approver is None:
            fallback_email = current_app.config.get('FALLBACK_ADMIN_EMAIL')
            admin_user = None
            if fallback_email:
                admin_user = User.query.filter_by(email=fallback_email).first()
            if not admin_user:
                admin_user = User.query.filter_by(role='admin').first()
            if admin_user:
                approver = admin_user.id
                auto_assigned = True

        # 尝试找到匹配的流程节点以写入 node_id，便于顺序推进
        # 延迟导入以避免模块导入时的循环依赖
        from app.approval_models import WorkflowNode, WorkflowTemplate
        from app.approval_roles import ApprovalRole

        node = WorkflowNode.query.join(
            WorkflowTemplate
        ).join(
            ApprovalRole, WorkflowNode.approval_role_id == ApprovalRole.id
        ).filter(
            WorkflowTemplate.order_type == order_type,
            ApprovalRole.name == level,
            WorkflowNode.is_active == True
        ).order_by(WorkflowNode.sequence).first()
        a = ApprovalWorkflow(
            order_type=order_type,
            order_id=order_id,
            approver_id=approver,
            approval_level=level,
            node_id=(node.id if node else None),
            status='pending',
            created_date=now + timedelta(seconds=i),
            auto_assigned=auto_assigned
        )
        db.session.add(a)
        approvals.append(a)

        # 如果发生了自动分配，记录一条用户活动日志并通知管理员
        if auto_assigned and approver:
            try:
                # 中英文映射
                _type_map = {
                    'repair_order': '维修工单',
                    'part_request_order': '配件申请',
                    'equipment_transfer': '设备调拨',
                    'equipment_scrap': '设备报废',
                    'equipment_loan': '设备借用',
                    'equipment_application': '设备申请'
                }
                _level_map = {
                    'department_head': '部门领导',
                    'admin': '管理员',
                    'technician': '技术员'
                }
                order_type_cn = _type_map.get(order_type, order_type)
                level_cn = _level_map.get(level, level)
                activity_log = UserActivityLog(
                    user_id=approver,
                    action='自动分配审批',
                    description=f'对于 {order_type_cn}#{order_id} 的审批节点 {level_cn}，系统自动分配给管理员用户ID {approver}。'
                )
                db.session.add(activity_log)

                notif = Notification(
                    user_id=approver,
                    title='自动分配审批',
                    message=f'系统将 {order_type_cn}#{order_id} 的审批节点 {level_cn} 自动分配给您，请尽快处理。'
                )
                db.session.add(notif)
            except Exception:
                # 在记录失败时不阻塞整体流程
                pass
    return approvals


@bp.route('/create_loan_request', methods=['GET', 'POST'])
@login_required
def create_loan_request():
    # 可选设备范围：
    # - 管理员：所有未报废设备
    # - 非管理员：本部门未报废 + 信息部公开仓库（可申请）
    if current_user.role == 'admin':
        equipments = Equipment.query.filter(Equipment.status != 'retired').all()
    elif current_user.department:
        own = Equipment.query.filter(Equipment.department == current_user.department, Equipment.status != 'retired').all()
        pool = Equipment.query.filter(Equipment.is_public_pool == True, Equipment.status == 'available').all()
        eq_map = {e.id: e for e in own + pool}
        equipments = list(eq_map.values())
    else:
        # 用户无部门时,只能申请公开仓库的设备
        equipments = Equipment.query.filter(Equipment.is_public_pool == True, Equipment.status == 'available').all()

    if request.method == 'POST':
        equipment_id = request.form.get('equipment_id', type=int)
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        notes = request.form.get('notes')

        if not equipment_id or not start_date or not end_date:
            flash('请选择设备并填写借用起止日期')
            return render_template('main/create_loan_request.html', title='申请借用设备', equipments=equipments)

        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            flash('设备不存在')
            return redirect(url_for('main.create_loan_request'))

        # Python 3.6 兼容的日期解析
        def _parse_dt(s):
            fmts = ['%Y-%m-%d', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']
            for f in fmts:
                try:
                    return datetime.strptime(s, f)
                except Exception:
                    pass
            raise ValueError('日期格式不支持，请使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM')

        loan = EquipmentLoan(
            equipment_id=equipment_id,
            requester_id=current_user.id,
            requester_dept=current_user.department,
            start_date=_parse_dt(start_date),
            end_date=_parse_dt(end_date),
            notes=notes,
            status='submitted'
        )
        db.session.add(loan)
        db.session.flush()

        # 创建审批链： 部门负责人 -> 系统管理员
        steps = [
            ('department_head', current_user.department),
            ('admin', None)
        ]
        _create_sequenced_approvals('equipment_loan', loan.id, steps)

        note = Notification(user_id=current_user.id, title='借用申请已提交', message=f'您已提交设备借用申请 #{loan.id}，等待审批。')
        db.session.add(note)
        db.session.commit()

        flash('借用申请已提交')
        return redirect(url_for('main.index'))

    return render_template('main/create_loan_request.html', title='申请借用设备', equipments=equipments)


@bp.route('/create_equipment_application', methods=['GET', 'POST'])
@login_required
def create_equipment_application():
    if current_user.role not in ['admin', 'department_head', 'technician', 'user']:
        flash('您没有权限提交设备申请')
        return redirect(url_for('main.index'))

    # 可申请设备：公开仓库且未报废/未维修/未借出（含正常与可申请）
    equipments = Equipment.query.filter(
        Equipment.is_public_pool == True,
        ~Equipment.status.in_(['retired', 'repair', 'loaned'])
    ).all()

    if request.method == 'POST':
        equipment_id = request.form.get('equipment_id', type=int)
        reason = request.form.get('reason', '').strip()
        if not equipment_id:
            flash('请选择设备')
            return render_template('main/create_equipment_application.html', title='设备申请', equipments=equipments)
        eq = Equipment.query.get(equipment_id)
        if not eq:
            flash('设备不存在')
            return render_template('main/create_equipment_application.html', title='设备申请', equipments=equipments)
        if not eq.is_public_pool or eq.status in ('retired', 'repair', 'loaned'):
            flash('该设备不在公开仓库或当前不可申请')
            return render_template('main/create_equipment_application.html', title='设备申请', equipments=equipments)
        app_order = EquipmentApplication(
            equipment_id=equipment_id,
            applicant_id=current_user.id,
            applicant_dept=current_user.department,
            reason=reason,
            status='submitted'
        )
        db.session.add(app_order)
        db.session.flush()

        # 审批链：部门领导 -> 系统管理员
        steps = [('department_head', current_user.department), ('admin', None)]
        _create_sequenced_approvals('equipment_application', app_order.id, steps)
        db.session.commit()
        flash('设备申请已提交')
        return redirect(url_for('main.index'))

    return render_template('main/create_equipment_application.html', title='设备申请', equipments=equipments)


@bp.route('/approvals/equipment_application/<int:order_id>/<action>', methods=['POST'])
@login_required
def approve_equipment_application(order_id, action):
    # 管理员可以审批任何待审批的工单
    if current_user.role in ['admin', 'super_admin']:
        approval = ApprovalWorkflow.query.filter_by(
            order_type='equipment_application', order_id=order_id,
            status='pending'
        ).first_or_404()
    else:
        approval = ApprovalWorkflow.query.filter_by(
            order_type='equipment_application', order_id=order_id,
            approver_id=current_user.id, status='pending'
        ).first_or_404()
    app_order = EquipmentApplication.query.get_or_404(order_id)
    if action == 'approve':
        approval.status = 'approved'
        approval.approved_date = get_beijing_now()
        approval.comments = request.form.get('comments', '')
        next_node = get_next_approval_node('equipment_application', app_order.id)
        if next_node:
            next_approval = ApprovalWorkflow(
                order_type='equipment_application', order_id=app_order.id,
                approver_id=get_approver_id(next_node, app_order.applicant_dept),
                approval_level=next_node.role_required, node_id=next_node.id, status='pending'
            )
            db.session.add(next_approval)
            notification = Notification(
                user_id=app_order.applicant_id,
                title='设备申请审批进度',
                message=f'您的设备申请 #{app_order.id} 节点已通过，进入下一节点：{next_node.name}',
                order_type='equipment_application',
                order_id=app_order.id
            )
            db.session.add(notification)
        else:
            app_order.status = 'approved'
            app_order.approved_date = get_beijing_now()
            # 创建调拨记录：从当前设备部门调往申请人部门
            eq = app_order.equipment
            # 更新设备状态为已分配（不再可用）
            if eq.status == 'available':
                eq.status = 'active'
                eq.department = app_order.applicant_dept
                _log_activity('设备状态更新', f'设备申请 #{app_order.id} 审批完成，设备 {eq.name} 已分配给 {app_order.applicant_dept}')
            
            transfer = EquipmentTransfer(
                equipment_id=eq.id,
                from_department=eq.department,
                to_department=app_order.applicant_dept,
                requester_id=app_order.applicant_id,
                description=f'设备申请通过，调拨设备 {eq.name} 至 {app_order.applicant_dept}',
                status='submitted'
            )
            db.session.add(transfer)
            
            # 发送通知给申请人
            notification = Notification(
                user_id=app_order.applicant_id,
                title='设备申请审批完成',
                message=f'您的设备申请 #{app_order.id} 已审批通过，设备 {eq.name} 已分配给您',
                order_type='equipment_application',
                order_id=app_order.id
            )
            db.session.add(notification)
            
            # 发送通知给管理员
            admins = User.query.filter_by(role='admin').all()
            for admin in admins:
                admin_notification = Notification(
                    user_id=admin.id,
                    title='设备申请已完成',
                    message=f'设备申请 #{app_order.id} 已审批完成，设备 {eq.name} 已分配给 {app_order.applicant_dept}',
                    order_type='equipment_application',
                    order_id=app_order.id
                )
                db.session.add(admin_notification)
        db.session.commit()
        _log_activity('审批设备申请', f'用户 {current_user.username} 批准了设备申请 #{app_order.id} (设备: {app_order.equipment.name})')
        flash('设备申请审批成功')
    elif action == 'reject':
        approval.status = 'rejected'
        approval.approved_date = get_beijing_now()
        approval.comments = request.form.get('comments', '')
        app_order.status = 'cancelled'
        notification = Notification(
            user_id=app_order.applicant_id,
            title='设备申请被拒绝',
            message=f'您的设备申请 #{app_order.id} 被拒绝',
            order_type='equipment_application',
            order_id=app_order.id
        )
        db.session.add(notification)
        db.session.commit()
        _log_activity('审批设备申请', f'用户 {current_user.username} 拒绝了设备申请 #{app_order.id} (设备: {app_order.equipment.name})')
        flash('设备申请已拒绝')
    return redirect(url_for('main.approvals'))


@bp.route('/loan_requests')
@login_required
def loan_requests():
    # 列出当前用户的借用申请；管理员可查看全部
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    q = request.args.get('q', '')

    query = EquipmentLoan.query
    if current_user.role != 'admin':
        query = query.filter_by(requester_id=current_user.id)

    if q:
        query = query.join(Equipment).filter(Equipment.name.ilike(f'%{q}%'))

    pagination = query.order_by(EquipmentLoan.created_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    loans = pagination.items
    
    # 计算待验收归还数量(仅管理员可见)
    pending_count = 0
    if current_user.role == 'admin':
        pending_count = EquipmentLoan.query.filter_by(status='return_pending').count()
    
    return render_template('main/loan_requests.html', title='借用申请', loans=loans, pagination=pagination, q=q, pending_count=pending_count)


@bp.route('/loans/export')
@login_required
def export_loans():
    # 导出符合当前筛选（管理员可导出全部，普通用户仅导出自己的）
    q = request.args.get('q', '')
    query = EquipmentLoan.query
    if current_user.role != 'admin':
        query = query.filter_by(requester_id=current_user.id)
    if q:
        query = query.join(Equipment).filter(Equipment.name.ilike(f'%{q}%'))

    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', '设备', '申请人', '部门', '开始', '结束', '状态', '备注', '创建时间'])
    for l in query.order_by(EquipmentLoan.created_date.desc()).all():
        writer.writerow([
            l.id,
            l.equipment.name if l.equipment else '',
            l.requester.username if l.requester else '',
            l.requester_dept,
            l.start_date.isoformat() if l.start_date else '',
            l.end_date.isoformat() if l.end_date else '',
            l.status,
            (l.notes or '').replace('\n',' '),
            l.created_date.isoformat() if l.created_date else ''
        ])

    from flask import Response
    csv_data = output.getvalue()
    output.close()
    filename = f'设备借用_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition': content_disposition(filename, 'equipment_loans.csv')})


@bp.route('/approvals/loan/<int:order_id>/<action>', methods=['POST'])
@login_required
def approve_loan(order_id, action):
    # 管理员可以审批任何待审批的工单
    if current_user.role in ['admin', 'super_admin']:
        approval = ApprovalWorkflow.query.filter_by(order_type='equipment_loan', order_id=order_id, status='pending').first()
    else:
        # 尝试找到当前用户对应的待审批记录;若未按用户匹配,尝试找到最早的 pending 节点并校验权限
        approval = ApprovalWorkflow.query.filter_by(order_type='equipment_loan', order_id=order_id, approver_id=current_user.id, status='pending').first()
    if not approval:
        # 没有直接分配给当前用户的节点，尝试取最早的 pending 节点
        approval = _get_next_pending_approval('equipment_loan', order_id)
        if not approval:
            # 无待审批节点
            flash('没有找到待处理的审批')
            return redirect(url_for('main.approvals'))
        # 如果该节点不是分配给当前用户，只有管理员可以代为审批
        if approval.approver_id and approval.approver_id != current_user.id and current_user.role != 'admin':
            flash('您无权审批此节点')
            return redirect(url_for('main.approvals'))

    if not _is_earliest_pending(approval):
        flash('请按流程顺序审批')
        return redirect(url_for('main.approvals'))

    loan = EquipmentLoan.query.get_or_404(order_id)

    if action == 'approve':
        approval.status = 'approved'
        approval.approved_date = get_beijing_now()
        approval.comments = request.form.get('comments', '')

        next_ = _get_next_pending_approval('equipment_loan', order_id)
        if not next_:
            # 流程结束，标记借用申请为已通过
            loan.status = 'approved'
            
            # 更新设备状态为已借出
            if loan.equipment:
                loan.equipment.status = 'loaned'
                _log_activity('设备借出', f'设备 {loan.equipment.name} 已借出给 {loan.requester.username if loan.requester else "用户"} (借用申请 #{loan.id})')
            
            note = Notification(user_id=loan.requester_id, title='借用申请通过', message=f'您的借用申请 #{loan.id} 已审批通过')
            db.session.add(note)
        db.session.add(approval)
        db.session.commit()
        flash('审批成功')

    elif action == 'reject':
        approval.status = 'rejected'
        approval.approved_date = get_beijing_now()
        approval.comments = request.form.get('comments', '')
        loan.status = 'rejected'
        note = Notification(user_id=loan.requester_id, title='借用申请被拒绝', message=f'您的借用申请 #{loan.id} 已被拒绝')
        db.session.add(note)
        db.session.add(approval)
        db.session.commit()
        flash('已拒绝')

    return redirect(url_for('main.approvals'))


@bp.route('/loans/<int:loan_id>/mark_borrowed', methods=['POST'])
@login_required
def mark_loan_borrowed(loan_id):
    loan = EquipmentLoan.query.get_or_404(loan_id)
    # 仅 admin 可以执行借出确认（可调整为特定角色）
    if current_user.role != 'admin':
        flash('您没有权限执行此操作')
        return redirect(url_for('main.loan_requests'))

    # 允许管理员在已通过或仍为 submitted 状态下标记为借出（兼容自动分配多节点情况）
    # proceed with marking borrowed
    if loan.status not in ('approved', 'submitted'):
        flash('只能对已通过或待转交的申请标记借出')
        return redirect(url_for('main.loan_requests'))

    loan.status = 'borrowed'
    loan.borrowed_date = get_beijing_now()
    if loan.equipment:
        loan.equipment.status = 'loaned'

    note = Notification(user_id=loan.requester_id, title='设备已借出', message=f'您的借用申请 #{loan.id} 对应设备已借出')
    db.session.add(note)
    db.session.commit()
    flash('已标记为借出')
    return redirect(url_for('main.loan_requests'))


@bp.route('/loans/<int:loan_id>/mark_returned', methods=['POST'])
@login_required
def mark_loan_returned(loan_id):
    loan = EquipmentLoan.query.get_or_404(loan_id)
    if current_user.role != 'admin':
        flash('您没有权限执行此操作')
        return redirect(url_for('main.loan_requests'))

    if loan.status != 'borrowed':
        flash('只能对已借出的申请标记归还')
        return redirect(url_for('main.loan_requests'))

    loan.status = 'returned'
    loan.returned_date = get_beijing_now()
    if loan.equipment:
        loan.equipment.status = 'active'

    note = Notification(user_id=loan.requester_id, title='设备已归还', message=f'借用申请 #{loan.id} 的设备已归还')
    db.session.add(note)
    db.session.commit()
    flash('已标记为归还')
    return redirect(url_for('main.loan_requests'))


@bp.route('/equipment/loan/<int:id>/return', methods=['POST'])
@login_required
def return_equipment(id):
    """
    归还借用设备
    
    借用人或管理员可以归还设备
    """
    try:
        loan = EquipmentLoan.query.get_or_404(id)
        
        # 权限检查: 只有借用人或管理员可以归还
        if current_user.role not in ['admin', 'super_admin']:
            if loan.requester_id != current_user.id:
                flash('您没有权限归还此设备', 'danger')
                return redirect(url_for('main.index'))
        
        # 检查是否已归还
        if loan.status == 'returned':
            flash('该设备已归还', 'warning')
            return redirect(url_for('main.my_loans'))
        
        # 检查是否已批准或已借出
        if loan.status not in ['approved', 'borrowed']:
            flash('只能归还已批准或已借出的设备', 'warning')
            return redirect(url_for('main.my_loans'))
        
        # 更新借用记录
        loan.actual_return_date = get_beijing_now()
        loan.returned_date = get_beijing_now()
        loan.status = 'returned'
        
        # 更新设备状态为可用
        equipment = loan.equipment
        if equipment:
            equipment.status = 'available'
            _log_activity('归还设备', f'用户 {current_user.username} 归还了设备 {equipment.name} (借用申请 #{loan.id})')
        
        # 通知管理员
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            notification = Notification(
                user_id=admin.id,
                title='设备已归还',
                message=f'用户 {current_user.username} 已归还设备: {equipment.name if equipment else "未知设备"}'
            )
            db.session.add(notification)
        
        db.session.commit()
        flash('设备归还成功', 'success')
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'归还设备失败: {e}', exc_info=True)
        flash('归还失败,请联系管理员', 'danger')
    
    return redirect(url_for('main.my_loans'))


@bp.route('/my_loans')
@login_required
def my_loans():
    """
    查看我的借用记录
    """
    # 我申请的借用
    my_loan_list = EquipmentLoan.query.filter_by(
        requester_id=current_user.id
    ).order_by(EquipmentLoan.created_date.desc()).all()
    
    return render_template('main/my_loans.html', 
                         title='我的借用记录',
                         loans=my_loan_list,
                         now=datetime.now)


@bp.route('/admin/users/<int:user_id>/permissions', methods=['POST'])
@login_required
def update_user_permissions(user_id):
    """更新用户模块权限"""
    if current_user.role != 'admin':
        flash('您没有权限执行此操作')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)

    # 防止管理员在界面上误改自己权限（保持简单：不允许修改自己的模块权限）
    if user.id == current_user.id:
        flash('不能通过此页面修改自己的权限')
        return redirect(url_for('main.user_management'))

    # 普通/经理等用户：根据勾选更新模块权限
    user.can_manage_equipment = request.form.get('can_manage_equipment') == 'on'
    user.can_manage_spare_parts = request.form.get('can_manage_spare_parts') == 'on'
    user.can_manage_repairs = request.form.get('can_manage_repairs') == 'on'
    user.can_manage_part_requests = request.form.get('can_manage_part_requests') == 'on'
    user.can_view_workflow = request.form.get('can_view_workflow') == 'on'
    user.can_view_reports = request.form.get('can_view_reports') == 'on'
    user.can_view_logs = request.form.get('can_view_logs') == 'on'

    # 管理员账号默认拥有全部模块权限，避免被误关掉后无法访问
    if user.role == 'admin':
        user.can_manage_equipment = True
        user.can_manage_spare_parts = True
        user.can_manage_repairs = True
        user.can_manage_part_requests = True
        user.can_view_workflow = True
        user.can_view_reports = True
        user.can_view_logs = True
    
    db.session.commit()
    flash(f'用户 {user.username} 的权限已更新')
    return redirect(url_for('main.user_management'))


@bp.route('/admin/database')
@login_required
def database_management():
    """数据库管理页面"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    # 获取数据库信息
    db_info_result = get_database_info()
    db_info = db_info_result.get('info', {}) if db_info_result.get('success') else {}
    
    # 获取筛选参数
    filter_date = request.args.get('filter', 'all')  # today, yesterday, week, month, all
    page = request.args.get('page', 1, type=int)
    per_page = 5  # 每页显示5条
    
    # 获取备份列表
    backups_result = list_backups(filter_date if filter_date != 'all' else None)
    all_backups = backups_result.get('backups', []) if backups_result.get('success') else []
    total_backups = backups_result.get('total', 0)
    
    # 分页处理
    total_pages = (len(all_backups) + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    backups = all_backups[start_idx:end_idx]
    
    return render_template('main/database_management.html',
                         title='数据库管理',
                         db_info=db_info,
                         backups=backups,
                         total_backups=total_backups,
                         filter_date=filter_date,
                         page=page,
                         total_pages=total_pages,
                         per_page=per_page)


@bp.route('/admin/database/backup', methods=['POST'])
@login_required
def backup_database_route():
    """备份数据库"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '您没有权限执行此操作'}), 403
    
    result = backup_database()
    if result.get('success'):
        flash(f"数据库备份成功: {result.get('backup_filename')}")
        _log_activity('数据库备份', f'用户 {current_user.username} 备份了数据库: {result.get("backup_filename")}')
    else:
        flash(f"备份失败: {result.get('message')}", 'error')
    
    return jsonify(result)


@bp.route('/admin/database/export_mysql', methods=['POST'])
@login_required
def export_mysql_route():
    """导出为 MySQL 兼容的 SQL 文件并返回下载信息"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '您没有权限执行此操作'}), 403

    db_info = get_database_info().get('info', {})
    if not db_info:
        return jsonify({'success': False, 'message': '无法获取数据库信息'})

    # SQLite 导出路径已被移除；通知用户使用 PostgreSQL 备份/导出流程
    return jsonify({'success': False, 'message': 'SQLite 导出已不再支持；请使用 PostgreSQL 备份或导出 SQL 文件。'})

    # 获取自定义路径
    custom_path = None
    if request.is_json:
        data = request.get_json()
        custom_path = data.get('custom_path', '').strip() if data else None
    
    # 验证和处理自定义路径
    out_dir = None
    if custom_path:
        # 如果是相对路径,转换为绝对路径
        if not os.path.isabs(custom_path):
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            out_dir = os.path.join(project_root, custom_path)
        else:
            # 支持绝对路径: C:\, D:\, \\server\share\ 等
            out_dir = custom_path
        
        # 规范化路径,处理反斜杠
        out_dir = os.path.normpath(out_dir)
        
        # 检查目录是否存在,不存在则尝试创建
        try:
            os.makedirs(out_dir, exist_ok=True)
            # 验证是否可写
            if not os.access(out_dir, os.W_OK):
                return jsonify({'success': False, 'message': f'目录不可写: {out_dir}\n请检查权限设置'})
        except PermissionError:
            return jsonify({'success': False, 'message': f'权限不足,无法创建目录: {out_dir}\n请以管理员身份运行或选择其他目录'})
        except OSError as e:
            return jsonify({'success': False, 'message': f'无法访问路径 {out_dir}: {str(e)}\n请检查:\n1. 磁盘是否存在\n2. 网络路径是否可访问\n3. 路径格式是否正确'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'创建目录失败: {str(e)}'})

    result = export_database_to_mysql(sqlite_path, out_dir=out_dir)
    if result.get('success'):
        # 返回实际保存路径
        actual_path = os.path.dirname(result.get('dump_path', ''))
        if actual_path:
            result['save_path'] = actual_path
        _log_activity('导出数据库(MySQL)', f'用户 {current_user.username} 导出了数据库到 MySQL 转储: {result.get("dump_filename")}')
    return jsonify(result)


@bp.route('/admin/database/export_mssql', methods=['POST'])
@login_required
def export_mssql_route():
    """导出为 SQL Server 兼容的 SQL 文件并返回下载信息
    注：已移除对 SQLite 的自动导出支持；请使用 PostgreSQL 的导出工具（pg_dump）或专业迁移工具。"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '您没有权限执行此操作'}), 403

    # SQLite 导出已不再支持
    return jsonify({'success': False, 'message': 'SQLite 导出已不再支持；请使用 PostgreSQL (pg_dump) 进行导出。'})

    # 获取自定义路径
    custom_path = None
    if request.is_json:
        data = request.get_json()
        custom_path = data.get('custom_path', '').strip() if data else None
    
    # 验证和处理自定义路径
    out_dir = None
    if custom_path:
        # 如果是相对路径,转换为绝对路径
        if not os.path.isabs(custom_path):
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            out_dir = os.path.join(project_root, custom_path)
        else:
            # 支持绝对路径: C:\, D:\, \\server\share\ 等
            out_dir = custom_path
        
        # 规范化路径,处理反斜杠
        out_dir = os.path.normpath(out_dir)
        
        # 检查目录是否存在,不存在则尝试创建
        try:
            os.makedirs(out_dir, exist_ok=True)
            # 验证是否可写
            if not os.access(out_dir, os.W_OK):
                return jsonify({'success': False, 'message': f'目录不可写: {out_dir}\n请检查权限设置'})
        except PermissionError:
            return jsonify({'success': False, 'message': f'权限不足,无法创建目录: {out_dir}\n请以管理员身份运行或选择其他目录'})
        except OSError as e:
            return jsonify({'success': False, 'message': f'无法访问路径 {out_dir}: {str(e)}\n请检查:\n1. 磁盘是否存在\n2. 网络路径是否可访问\n3. 路径格式是否正确'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'创建目录失败: {str(e)}'})

    result = export_database_to_mssql(sqlite_path, out_dir=out_dir)
    if result.get('success'):
        # 返回实际保存路径
        actual_path = os.path.dirname(result.get('dump_path', ''))
        if actual_path:
            result['save_path'] = actual_path
        _log_activity('导出数据库(MSSQL)', f'用户 {current_user.username} 导出了数据库到 MSSQL 转储: {result.get("dump_filename")}')
    return jsonify(result)


@bp.route('/admin/database/export_postgresql', methods=['POST'])
@login_required
def export_postgresql_route():
    """导出为 PostgreSQL 兼容的 SQL 文件并返回下载信息
    注：该接口原本用于把 SQLite 导出为 PostgreSQL；现在已不再支持 SQLite 自动导出。"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '您没有权限执行此操作'}), 403

    # 不再支持从 SQLite 导出 - 对于 PostgreSQL 直接使用 pg_dump
    return jsonify({'success': False, 'message': '此接口已废弃：请直接使用 PostgreSQL 的备份工具 (pg_dump) 导出数据库。'})

    # 获取自定义路径
    custom_path = None
    if request.is_json:
        data = request.get_json()
        custom_path = data.get('custom_path', '').strip() if data else None
    
    # 验证和处理自定义路径
    out_dir = None
    if custom_path:
        # 如果是相对路径,转换为绝对路径
        if not os.path.isabs(custom_path):
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            out_dir = os.path.join(project_root, custom_path)
        else:
            # 支持绝对路径: C:\, D:\, \\server\share\ 等
            out_dir = custom_path
        
        # 规范化路径,处理反斜杠
        out_dir = os.path.normpath(out_dir)
        
        # 检查目录是否存在,不存在则尝试创建
        try:
            os.makedirs(out_dir, exist_ok=True)
            # 验证是否可写
            if not os.access(out_dir, os.W_OK):
                return jsonify({'success': False, 'message': f'目录不可写: {out_dir}\n请检查权限设置'})
        except PermissionError:
            return jsonify({'success': False, 'message': f'权限不足,无法创建目录: {out_dir}\n请以管理员身份运行或选择其他目录'})
        except OSError as e:
            return jsonify({'success': False, 'message': f'无法访问路径 {out_dir}: {str(e)}\n请检查:\n1. 磁盘是否存在\n2. 网络路径是否可访问\n3. 路径格式是否正确'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'创建目录失败: {str(e)}'})

    result = export_database_to_postgresql(sqlite_path, out_dir=out_dir)
    if result.get('success'):
        # 返回实际保存路径
        actual_path = os.path.dirname(result.get('dump_path', ''))
        if actual_path:
            result['save_path'] = actual_path
        _log_activity('导出数据库(PostgreSQL)', f'用户 {current_user.username} 导出了数据库到 PostgreSQL 转储: {result.get("dump_filename")}')
    return jsonify(result)


@bp.route('/admin/database/download/<path:filename>')
@login_required
def download_database_dump(filename):
    """提供导出/备份文件的下载入口（仅限 admin）"""
    if current_user.role != 'admin':
        flash('您没有权限下载该文件')
        return redirect(url_for('main.database_management'))
    # 限制路径到 migrations 或 backups 目录
    base_dirs = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'migrations'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'backups')
    ]
    # normalize
    import os as _os
    for base in base_dirs:
        base_abs = _os.path.abspath(base)
        candidate = _os.path.abspath(_os.path.join(base_abs, filename))
        if candidate.startswith(base_abs) and _os.path.exists(candidate):
            from flask import send_file
            return send_file(candidate, as_attachment=True, download_name=_os.path.basename(candidate))

    flash('文件不存在或无权限')
    return redirect(url_for('main.database_management'))


@bp.route('/admin/database/restore', methods=['POST'])
@login_required
def restore_database_route():
    """恢复数据库"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '您没有权限执行此操作'}), 403
    
    backup_filename = request.form.get('backup_filename')
    if not backup_filename:
        return jsonify({'success': False, 'message': '请选择要恢复的备份文件'})
    
    result = restore_database(backup_filename)
    if result.get('success'):
        flash(f"数据库恢复成功: {backup_filename}")
        _log_activity('数据库恢复', f'用户 {current_user.username} 恢复了数据库: {backup_filename}')
    else:
        flash(f"恢复失败: {result.get('message')}", 'error')
    
    return jsonify(result)


@bp.route('/admin/database/restore_latest', methods=['POST'])
@login_required
def restore_latest_route():
    """快速恢复：使用最近一次备份进行恢复（仅 admin）。"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '您没有权限执行此操作'}), 403

    # 获取备份列表（按时间倒序），选择第一个
    backups_result = list_backups()
    if not backups_result.get('success'):
        return jsonify({'success': False, 'message': '无法获取备份列表'})
    backups = backups_result.get('backups', [])
    if not backups:
        return jsonify({'success': False, 'message': '没有找到可用的备份文件'})

    latest = backups[0]['filename']
    result = restore_database(latest)
    if result.get('success'):
        flash(f"数据库恢复成功: {latest}")
        _log_activity('数据库恢复', f'用户 {current_user.username} 使用最近备份恢复数据库: {latest}')
    else:
        flash(f"恢复失败: {result.get('message')}", 'error')

    return jsonify(result)


@bp.route('/admin/database/import', methods=['POST'])
@login_required
def import_database_route():
    """通过上传的数据库文件导入/恢复（支持 .db, .sql, .sql.gz 文件）"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '您没有权限执行此操作'}), 403

    if 'db_file' not in request.files:
        return jsonify({'success': False, 'message': '未检测到上传文件 (字段名: db_file)'}), 400

    file = request.files['db_file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '请选择要上传的文件'}), 400

    filename = secure_filename(file.filename)
    
    # 仅支持 PostgreSQL SQL 转储文件（.sql 或 .sql.gz），不再支持 SQLite .db 文件
    valid_extensions = ['.sql', '.sql.gz']
    is_valid = any(filename.lower().endswith(ext) for ext in valid_extensions)
    
    if not is_valid:
        return jsonify({
            'success': False,
            'message': f'仅支持上传 PostgreSQL SQL 转储文件 (.sql, .sql.gz)；SQLite (.db) 不再受支持'
        }), 400

    # 保存到备份目录，然后调用 restore_database
    backup_dir = get_backup_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 根据文件类型生成目标名称
    if filename.lower().endswith('.db'):
        target_name = f'imported_{timestamp}_{filename}'
    elif filename.lower().endswith('.sql.gz'):
        target_name = f'postgresql_backup_{timestamp}.sql.gz'
    elif filename.lower().endswith('.sql'):
        target_name = f'postgresql_backup_{timestamp}.sql'
    else:
        target_name = f'imported_{timestamp}_{filename}'
    
    target_path = os.path.join(backup_dir, target_name)
    try:
        file.save(target_path)
    except Exception as e:
        return jsonify({'success': False, 'message': f'保存上传文件失败: {str(e)}'})

    # 验证文件
    validation_result = validate_database_file(target_path)
    if not validation_result.get('success'):
        # 删除无效文件
        try:
            os.remove(target_path)
        except:
            pass
        return jsonify({
            'success': False,
            'message': f'文件验证失败: {validation_result.get("message")}'
        })

    # 使用已有恢复逻辑恢复
    result = restore_database(target_name, auto_backup=True)
    if result.get('success'):
        _log_activity('导入/恢复数据库', f'用户 {current_user.username} 上传并恢复了数据库: {target_name}')
    else:
        # 恢复失败，保留文件供后续排查
        flash(f'恢复失败，文件已保存至: {target_name}', 'warning')
    
    return jsonify(result)


@bp.route('/admin/database/reset', methods=['POST'])
@login_required
def reset_database_route():
    """重置数据库"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '您没有权限执行此操作'}), 403
    
    # 确认操作
    confirm = request.form.get('confirm')
    if confirm != 'RESET':
        return jsonify({'success': False, 'message': '请确认操作：在确认框中输入 RESET'})
    
    result = reset_database()
    if result.get('success'):
        flash(f"数据库重置成功，默认管理员账号: {result.get('admin_username')} / {result.get('admin_password')}")
        _log_activity('数据库重置', f'用户 {current_user.username} 重置了数据库')
    else:
        flash(f"重置失败: {result.get('message')}", 'error')
    
    return jsonify(result)


@bp.route('/admin/database/initialize', methods=['POST'])
@login_required
def initialize_system_route():
    """初始化系统（仅保留管理员、设备类型、配件类型、部门、地点、审批流程）"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '您没有权限执行此操作'}), 403
    
    # 确认操作 - 需要三步确认
    confirm = request.form.get('confirm')
    if confirm != 'INITIALIZE_SYSTEM':
        return jsonify({'success': False, 'message': '请确认操作：在确认框中输入 INITIALIZE_SYSTEM'})
    
    try:
        from app.utils.db_management import initialize_system
        result = initialize_system()
        
        if result.get('success'):
            flash(f"系统初始化成功！\n管理员账号: {result.get('admin_username')} / {result.get('admin_password')}\n\n初始化统计:\n- 删除用户: {result.get('users_cleared', 0)} 人\n- 删除设备: {result.get('equipment_cleared', 0)} 台\n- 创建备份: {result.get('backup_file', 'N/A')}", 'success')
            _log_activity('系统初始化', f'用户 {current_user.username} 执行了系统初始化操作')
        else:
            flash(f"初始化失败: {result.get('message')}", 'error')
            _log_activity('系统初始化失败', f'用户 {current_user.username} 系统初始化失败: {result.get("message")}')
    except Exception as e:
        result = {'success': False, 'message': f'系统初始化异常: {str(e)}'}
        flash(f"初始化异常: {str(e)}", 'error')
        _log_activity('系统初始化异常', f'用户 {current_user.username} 系统初始化异常: {str(e)}')
    
    return jsonify(result)


@bp.route('/admin/database/tables', methods=['GET'])
@login_required
def database_tables():
    """查看数据库表信息"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    result = get_database_tables_info()
    if result.get('success'):
        tables_info = result.get('tables', [])
        total_records = result.get('total_records', 0)
    else:
        tables_info = []
        total_records = 0
        flash(f"获取表信息失败: {result.get('message')}", 'error')
    
    return render_template('main/database_tables.html',
                         title='数据库表查看',
                         tables=tables_info,
                         total_records=total_records)


@bp.route('/admin/database/table/<table_name>', methods=['GET'])
@login_required
def view_table_data(table_name):
    """查看指定表的数据"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    result = get_table_data(table_name, page, per_page)
    
    if not result.get('success'):
        flash(f"获取表数据失败: {result.get('message')}", 'error')
        return redirect(url_for('main.database_tables'))
    
    return render_template('main/table_data.html',
                         title=f'数据表: {table_name}',
                         table_name=table_name,
                         columns=result.get('columns', []),
                         column_info=result.get('column_info', []),
                         data=result.get('data', []),
                         total_count=result.get('total_count', 0),
                         page=page,
                         per_page=per_page,
                         total_pages=result.get('total_pages', 1))


@bp.route('/admin/database/migration_guide', methods=['GET'])
@login_required
def migration_guide():
    """查看数据库迁移指南页面"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    return render_template('main/migration_guide.html')

@bp.route('/admin/database/download_migration_guide', methods=['GET'])
@login_required
def download_migration_guide():
    """下载数据库迁移指南"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    import os
    from flask import send_file
    
    guide_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'DATABASE_MIGRATION_GUIDE.md')
    
    if os.path.exists(guide_path):
        return send_file(guide_path, as_attachment=True, download_name='DATABASE_MIGRATION_GUIDE.md')
    else:
        flash('迁移指南文件不存在', 'error')
        return redirect(url_for('main.database_management'))


@bp.route('/admin/database/backup/delete', methods=['POST'])
@login_required
def delete_backup_route():
    """删除备份文件"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '您没有权限执行此操作'}), 403
    
    backup_filename = request.form.get('backup_filename')
    if not backup_filename:
        return jsonify({'success': False, 'message': '请指定要删除的备份文件'})
    
    result = delete_backup(backup_filename)
    if result.get('success'):
        flash(f"备份文件删除成功: {backup_filename}")
        _log_activity('删除备份', f'用户 {current_user.username} 删除了备份文件: {backup_filename}')
    else:
        flash(f"删除失败: {result.get('message')}", 'error')
    
    return jsonify(result)


@bp.route('/admin/users/<int:user_id>/reset_password', methods=['POST'])
@login_required
def reset_user_password(user_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    if not new_password or new_password != confirm_password:
        return jsonify({'success': False, 'message': '密码不一致'})
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    from werkzeug.security import generate_password_hash
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    _log_activity('重置密码', f'管理员为用户 {user.username} 重置密码')
    return jsonify({'success': True, 'message': '密码已更新'})


def _get_next_pending_approval(order_type, order_id):
    return ApprovalWorkflow.query.filter_by(order_type=order_type, order_id=order_id, status='pending')\
        .order_by(ApprovalWorkflow.created_date).first()


def _is_earliest_pending(approval):
    # check if there exists any pending approval with an earlier created_date
    earlier = ApprovalWorkflow.query.filter(
        ApprovalWorkflow.order_type == approval.order_type,
        ApprovalWorkflow.order_id == approval.order_id,
        ApprovalWorkflow.status == 'pending',
        ApprovalWorkflow.created_date < approval.created_date
    ).count()
    return earlier == 0


@bp.route('/create_transfer', methods=['GET', 'POST'])
@login_required
def create_transfer():
    # 只能对当前用户部门的设备发起调拨（admin 可以发起任意）
    if current_user.role == 'admin':
        equipments = Equipment.query.all()
    elif current_user.department:
        equipments = Equipment.query.filter_by(department=current_user.department).all()
    else:
        equipments = []

    departments = Department.query.all()

    if request.method == 'POST':
        equipment_id = request.form.get('equipment_id', type=int)
        to_department = request.form.get('to_department')
        description = request.form.get('description')

        if not equipment_id or not to_department:
            flash('请选择设备并填写目标部门')
            return render_template('main/create_transfer.html', title='调拨设备', equipments=equipments, departments=departments)

        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            flash('设备不存在')
            return redirect(url_for('main.create_transfer'))

        # 验证属于发起人部门（非 admin）
        if current_user.role != 'admin' and equipment.department != current_user.department:
            flash('只能调拨本部门设备')
            return redirect(url_for('main.create_transfer'))

        transfer = EquipmentTransfer(
            equipment_id=equipment_id,
            from_department=equipment.department,
            to_department=to_department,
            requester_id=current_user.id,
            description=description
        )
        db.session.add(transfer)
        db.session.flush()

        # 创建审批链： 发起部门负责人 -> 系统管理员 -> 接收部门负责人 -> 系统管理员
        steps = [
            ('department_head', equipment.department),
            ('admin', None),
            ('department_head', to_department),
            ('admin', None)
        ]
        _create_sequenced_approvals('equipment_transfer', transfer.id, steps)

        # 抄送发起人通知（说明流程已创建）
        notification = Notification(
            user_id=current_user.id,
            title='设备调拨已提交',
            message=f'您已提交设备调拨申请 #{transfer.id}，等待审批流程。'
        )
        db.session.add(notification)

        db.session.commit()

        flash('设备调拨申请已提交')
        return redirect(url_for('main.index'))

    return render_template('main/create_transfer.html', title='调拨设备', equipments=equipments, departments=departments)


@bp.route('/create_scrap', methods=['GET', 'POST'])
@login_required
def create_scrap():
    # admin 可操作所有，普通用户仅限所属部门设备
    if current_user.role == 'admin':
        equipments = Equipment.query.all()
    elif current_user.department:
        equipments = Equipment.query.filter_by(department=current_user.department).all()
    else:
        equipments = []

    if request.method == 'POST':
        equipment_id = request.form.get('equipment_id', type=int)
        description = request.form.get('description')

        if not equipment_id:
            flash('请选择设备')
            return render_template('main/create_scrap.html', title='报废设备', equipments=equipments)

        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            flash('设备不存在')
            return redirect(url_for('main.create_scrap'))

        if current_user.role != 'admin' and equipment.department != current_user.department:
            flash('只能报废本部门设备')
            return redirect(url_for('main.create_scrap'))

        scrap = EquipmentScrap(
            equipment_id=equipment_id,
            requester_id=current_user.id,
            description=description
        )
        db.session.add(scrap)
        db.session.flush()

        # 报废审批链： 部门负责人 -> 系统管理员
        steps = [
            ('department_head', equipment.department),
            ('admin', None)
        ]
        _create_sequenced_approvals('equipment_scrap', scrap.id, steps)

        notification = Notification(
            user_id=current_user.id,
            title='设备报废已提交',
            message=f'您已提交设备报废申请 #{scrap.id}，等待审批流程。'
        )
        db.session.add(notification)

        db.session.commit()

        flash('设备报废申请已提交')
        return redirect(url_for('main.index'))

    return render_template('main/create_scrap.html', title='报废设备', equipments=equipments)


@bp.route('/approvals/transfer/<int:order_id>/<action>', methods=['POST'])
@login_required
def approve_transfer(order_id, action):
    # 管理员可以审批任何待审批的工单
    if current_user.role in ['admin', 'super_admin']:
        approval = ApprovalWorkflow.query.filter_by(order_type='equipment_transfer', order_id=order_id, status='pending').first_or_404()
    else:
        approval = ApprovalWorkflow.query.filter_by(order_type='equipment_transfer', order_id=order_id, approver_id=current_user.id, status='pending').first_or_404()
    # ensure it's the earliest pending
    if not _is_earliest_pending(approval):
        flash('请按流程顺序审批')
        return redirect(url_for('main.approvals'))

    transfer = EquipmentTransfer.query.get_or_404(order_id)

    if action == 'approve':
        approval.status = 'approved'
        approval.approved_date = get_beijing_now()
        approval.comments = request.form.get('comments', '')

        # check for next pending approval
        next_ = _get_next_pending_approval('equipment_transfer', order_id)
        if not next_:
            # 流程结束，执行调拨：变更设备所属部门
            eq = transfer.equipment
            eq.department = transfer.to_department
            transfer.status = 'approved'
            # 通知发起人
            note = Notification(user_id=transfer.requester_id, title='设备调拨完成', message=f'您的设备调拨申请 #{transfer.id} 已完成')
            db.session.add(note)
        db.session.add(approval)
        db.session.commit()
        _log_activity('审批设备调拨', f'用户 {current_user.username} 批准了设备调拨申请 #{transfer.id}')
        flash('审批成功')

    elif action == 'reject':
        approval.status = 'rejected'
        approval.approved_date = get_beijing_now()
        approval.comments = request.form.get('comments', '')
        transfer.status = 'cancelled'
        note = Notification(user_id=transfer.requester_id, title='设备调拨被拒绝', message=f'您的设备调拨申请 #{transfer.id} 已被拒绝')
        db.session.add(note)
        db.session.add(approval)
        db.session.commit()
        _log_activity('审批设备调拨', f'用户 {current_user.username} 拒绝了设备调拨申请 #{transfer.id}')
        flash('已拒绝')

    return redirect(url_for('main.approvals'))


@bp.route('/approvals/scrap/<int:order_id>/<action>', methods=['POST'])
@login_required
def approve_scrap(order_id, action):
    # 管理员可以审批任何待审批的工单
    if current_user.role in ['admin', 'super_admin']:
        approval = ApprovalWorkflow.query.filter_by(order_type='equipment_scrap', order_id=order_id, status='pending').first_or_404()
    else:
        approval = ApprovalWorkflow.query.filter_by(order_type='equipment_scrap', order_id=order_id, approver_id=current_user.id, status='pending').first_or_404()
    if not _is_earliest_pending(approval):
        flash('请按流程顺序审批')
        return redirect(url_for('main.approvals'))

    scrap = EquipmentScrap.query.get_or_404(order_id)

    if action == 'approve':
        approval.status = 'approved'
        approval.approved_date = get_beijing_now()
        approval.comments = request.form.get('comments', '')
        next_ = _get_next_pending_approval('equipment_scrap', order_id)
        if not next_:
            # 流程结束：将设备状态设为 scrapped（报废）
            eq = scrap.equipment
            old_status = eq.status
            eq.status = 'scrapped'
            scrap.status = 'approved'
            
            # 🆕 记录到资产生命周期
            lifecycle_event = AssetLifecycle(
                equipment_id=eq.id,
                event_type='scrap',
                event_date=get_beijing_now(),
                old_status=old_status,
                new_status='scrapped',
                description=f'设备报废审批通过: {scrap.description or "无说明"}',
                cost_involved=0,
                responsible_user_id=current_user.id
            )
            db.session.add(lifecycle_event)
            
            # 🆕 记录状态变更日志
            _log_activity('设备报废', f'设备 {eq.name} (ID:{eq.id}) 状态从 {old_status} 变更为 scrapped,报废申请 #{scrap.id}')
            
            # 通知申请人
            note = Notification(user_id=scrap.requester_id, title='设备报废完成', message=f'您的设备报废申请 #{scrap.id} 已完成,设备 {eq.name} 已报废')
            db.session.add(note)
        db.session.add(approval)
        db.session.commit()
        _log_activity('审批设备报废', f'用户 {current_user.username} 批准了设备报废申请 #{scrap.id}')
        flash('审批成功')

    elif action == 'reject':
        approval.status = 'rejected'
        approval.approved_date = get_beijing_now()
        approval.comments = request.form.get('comments', '')
        scrap.status = 'cancelled'
        note = Notification(user_id=scrap.requester_id, title='设备报废被拒绝', message=f'您的设备报废申请 #{scrap.id} 已被拒绝')
        db.session.add(note)
        db.session.add(approval)
        db.session.commit()
        _log_activity('审批设备报废', f'用户 {current_user.username} 拒绝了设备报废申请 #{scrap.id}')
        flash('已拒绝')

    return redirect(url_for('main.approvals'))
def _log_activity(action, description):
    import logging
    logger = logging.getLogger(__name__)
    try:
        ip = request.headers.get('X-Forwarded-For') or request.headers.get('X-Real-IP') or request.remote_addr or ''
        activity_log = UserActivityLog(user_id=current_user.id, action=action, description=f"{description} (IP: {ip})")
        db.session.add(activity_log)
        try:
            db.session.commit()
        except Exception as e:
            logger.warning('记录活动日志时提交失败: %s', e, exc_info=True)
            try:
                db.session.rollback()
            except Exception:
                logger.debug('回滚活动日志事务失败（忽略）', exc_info=True)
    except Exception as e:
        logger.warning('记录活动日志失败: %s', e, exc_info=True)
@bp.route('/workflow/status/<order_type>/<int:order_id>')
@login_required
def workflow_status(order_type, order_id):
    # 获取流程配置与审批记录
    nodes = WorkflowNode.query.join(WorkflowTemplate).filter(
        WorkflowTemplate.order_type == order_type,
        WorkflowNode.is_active == True
    ).order_by(WorkflowNode.sequence).all()
    approvals = ApprovalWorkflow.query.filter_by(order_type=order_type, order_id=order_id).order_by(ApprovalWorkflow.created_date).all()

    # 辅助：获取订单的部门信息用于候选审批人
    def _order_dept(ot, oid):
        if ot == 'repair_order':
            ro = RepairOrder.query.get(oid)
            return (ro.requester.department if ro and ro.requester else None)
        if ot == 'part_request_order':
            po = PartRequestOrder.query.get(oid)
            return (po.requester.department if po and po.requester else None)
        if ot == 'equipment_transfer':
            tr = EquipmentTransfer.query.get(oid)
            return tr.from_department if tr else None
        if ot == 'equipment_scrap':
            sc = EquipmentScrap.query.get(oid)
            # 报废以申请人部门为准
            req = User.query.get(sc.requester_id) if sc else None
            return (req.department if req else None)
        if ot == 'equipment_loan':
            ln = EquipmentLoan.query.get(oid)
            return (ln.requester_dept if ln else None)
        if ot == 'equipment_application':
            ap = EquipmentApplication.query.get(oid)
            return (ap.applicant_dept if ap else None)
        return None

    dept = _order_dept(order_type, order_id)
    current_pending = _get_next_pending_approval(order_type, order_id)
    steps = []
    for node in nodes:
        matched = None
        for a in approvals:
            if (a.node_id and a.node_id == node.id) or (not a.node_id and a.approval_level == node.role_required):
                matched = a
                break
        assigned_user = None
        if matched and matched.approver_id:
            assigned_user = User.query.get(matched.approver_id)
        else:
            uid = _get_user_for_role(node.role_required, dept)
            assigned_user = User.query.get(uid) if uid else None
        status = 'not_started'
        approved_date = None
        comments = None
        auto_assigned = False
        if matched:
            status = matched.status
            approved_date = matched.approved_date
            comments = matched.comments
            auto_assigned = bool(matched.auto_assigned)
        elif current_pending and current_pending.approval_level == node.role_required:
            status = 'pending'

        steps.append({
            'node_id': node.id,
            'name': node.name,
            'role': node.role_required,
            'status': status,
            'assigned_user': assigned_user,
            'approved_date': approved_date,
            'comments': comments,
            'auto_assigned': auto_assigned
        })

    # 订单基本信息（标题与设备名等）
    order_title = f"{order_type}#{order_id}"
    try:
        if order_type == 'repair_order':
            ro = RepairOrder.query.get(order_id)
            order_title = f"维修工单 #{ro.id} - {ro.equipment.name if ro and ro.equipment else ''}"
        elif order_type == 'part_request_order':
            po = PartRequestOrder.query.get(order_id)
            order_title = f"配件申请 #{po.id} - {po.part_name if po else ''}"
        elif order_type == 'equipment_transfer':
            tr = EquipmentTransfer.query.get(order_id)
            order_title = f"设备调拨 #{tr.id} - {tr.equipment.name if tr and tr.equipment else ''}"
        elif order_type == 'equipment_scrap':
            sc = EquipmentScrap.query.get(order_id)
            order_title = f"设备报废 #{sc.id} - {sc.equipment.name if sc and sc.equipment else ''}"
        elif order_type == 'equipment_loan':
            ln = EquipmentLoan.query.get(order_id)
            order_title = f"设备借用 #{ln.id} - {ln.equipment.name if ln and ln.equipment else ''}"
        elif order_type == 'equipment_application':
            ap = EquipmentApplication.query.get(order_id)
            order_title = f"设备申请 #{ap.id} - {ap.equipment.name if ap and ap.equipment else ''}"
    except Exception:
        pass

    return render_template('main/workflow_status.html', 
                         title='流程状态', 
                         order_type=order_type, 
                         order_id=order_id, 
                         order_title=order_title, 
                         steps=steps,
                         current_pending=current_pending)


# ============ 权限管理路由 ============

@bp.route('/admin/role_permission_management')
@login_required
def role_permission_management():
    """权限管理首页 - 角色列表"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    roles = RoleDefinition.query.order_by(RoleDefinition.created_date.desc()).all()
    return render_template('main/role_permission_management.html', title='权限管理', roles=roles)


@bp.route('/admin/role/create', methods=['GET', 'POST'])
@login_required
def create_role():
    """创建自定义角色"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            
            if not name:
                flash('角色名称不能为空', 'error')
                return redirect(url_for('main.create_role'))
            
            # 检查角色名是否已存在
            existing = RoleDefinition.query.filter_by(name=name).first()
            if existing:
                flash(f'角色"{name}"已存在', 'error')
                return redirect(url_for('main.create_role'))
            
            role = RoleDefinition(
                name=name,
                description=description,
                is_custom=True,
                created_by_id=current_user.id
            )
            db.session.add(role)
            db.session.commit()
            
            _log_activity('创建角色', f'创建自定义角色: {name}')
            flash(f'角色"{name}"创建成功')
            return redirect(url_for('main.edit_role_permissions', role_id=role.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'创建角色失败: {str(e)}', 'error')
            return redirect(url_for('main.create_role'))
    
    return render_template('main/create_role.html', title='创建角色')


@bp.route('/admin/role/<int:role_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_role(role_id):
    """编辑角色信息"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    role = RoleDefinition.query.get_or_404(role_id)
    
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            is_active = request.form.get('is_active') == 'on'
            
            if not name:
                flash('角色名称不能为空', 'error')
                return redirect(url_for('main.edit_role', role_id=role_id))
            
            # 检查角色名是否与其他角色重复
            existing = RoleDefinition.query.filter(
                RoleDefinition.name == name,
                RoleDefinition.id != role_id
            ).first()
            if existing:
                flash(f'角色名"{name}"已被使用', 'error')
                return redirect(url_for('main.edit_role', role_id=role_id))
            
            role.name = name
            role.description = description
            role.is_active = is_active
            db.session.commit()
            
            _log_activity('编辑角色', f'编辑角色: {name}')
            flash('角色信息更新成功')
            return redirect(url_for('main.role_permission_management'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'更新角色失败: {str(e)}', 'error')
    
    return render_template('main/edit_role.html', title='编辑角色', role=role)


@bp.route('/admin/role/<int:role_id>/permissions', methods=['GET', 'POST'])
@login_required
def edit_role_permissions(role_id):
    """编辑角色权限"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    role = RoleDefinition.query.get_or_404(role_id)
    
    # 定义所有可用的模块和操作
    available_modules = {
        'equipment': {'name': '设备管理', 'actions': ['view', 'create', 'edit', 'delete', 'export']},
        'spare_part': {'name': '配件管理', 'actions': ['view', 'create', 'edit', 'delete', 'export']},
        'repair': {'name': '维修工单', 'actions': ['view', 'create', 'edit', 'delete', 'approve', 'complete']},
        'part_request': {'name': '配件申请', 'actions': ['view', 'create', 'edit', 'delete', 'approve']},
        'loan': {'name': '设备借用', 'actions': ['view', 'create', 'approve', 'return']},
        'transfer': {'name': '设备调拨', 'actions': ['view', 'create', 'approve']},
        'scrap': {'name': '设备报废', 'actions': ['view', 'create', 'approve']},
        'application': {'name': '设备申领', 'actions': ['view', 'create', 'approve']},
        'report': {'name': '报表统计', 'actions': ['view', 'export']},
        'user': {'name': '用户管理', 'actions': ['view', 'create', 'edit', 'delete']},
        'department': {'name': '部门管理', 'actions': ['view', 'create', 'edit', 'delete']},
        'workflow': {'name': '审批流程', 'actions': ['view', 'edit']},
        'logs': {'name': '操作日志', 'actions': ['view', 'export']},
        'announcement': {'name': '系统公告', 'actions': ['view', 'create', 'edit', 'delete', 'publish']},
        'wework': {'name': '企业微信', 'actions': ['view', 'config', 'sync']},
    }
    
    action_names = {
        'view': '查看',
        'create': '创建',
        'edit': '编辑',
        'delete': '删除',
        'approve': '审批',
        'complete': '完成',
        'return': '归还',
        'export': '导出',
        'publish': '发布',
        'config': '配置',
        'sync': '同步',
    }
    
    if request.method == 'POST':
        try:
            # 删除现有权限
            Permission.query.filter_by(role_id=role_id).delete()
            
            # 添加新权限
            for module in available_modules:
                for action in available_modules[module]['actions']:
                    field_name = f'{module}_{action}'
                    if request.form.get(field_name) == 'on':
                        perm = Permission(
                            role_id=role_id,
                            module=module,
                            action=action,
                            is_granted=True
                        )
                        db.session.add(perm)
            
            db.session.commit()
            _log_activity('配置权限', f'配置角色"{role.name}"的权限')
            flash('权限配置成功')
            return redirect(url_for('main.role_permission_management'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'权限配置失败: {str(e)}', 'error')
    
    # 获取当前角色的权限
    current_permissions = {}
    for perm in role.permissions:
        key = f'{perm.module}_{perm.action}'
        current_permissions[key] = perm.is_granted
    
    return render_template('main/edit_role_permissions.html', 
                         title=f'配置权限 - {role.name}',
                         role=role,
                         available_modules=available_modules,
                         action_names=action_names,
                         current_permissions=current_permissions)


@bp.route('/admin/role/<int:role_id>/users', methods=['GET', 'POST'])
@login_required
def manage_role_users(role_id):
    """管理角色的用户分配"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    role = RoleDefinition.query.get_or_404(role_id)
    
    if request.method == 'POST':
        try:
            from app.models import UserCustomRole
            user_ids = request.form.getlist('user_ids')
            
            # 清除现有关联(标记为不活跃)
            UserCustomRole.query.filter_by(role_id=role_id).update({'is_active': False})
            
            # 添加新关联
            assigned_users = []
            for user_id in user_ids:
                user = User.query.get(int(user_id))
                if user:
                    # 检查是否已存在记录
                    existing = UserCustomRole.query.filter_by(
                        user_id=user_id, 
                        role_id=role_id
                    ).first()
                    
                    if existing:
                        # 重新激活现有记录
                        existing.is_active = True
                        existing.assigned_by_id = current_user.id
                        existing.assigned_date = get_beijing_now()
                    else:
                        # 创建新记录
                        assignment = UserCustomRole(
                            user_id=user_id,
                            role_id=role_id,
                            assigned_by_id=current_user.id,
                            assigned_date=get_beijing_now(),
                            is_active=True
                        )
                        db.session.add(assignment)
                    
                    assigned_users.append(user.username)
            
            db.session.commit()
            
            # 记录详细的操作日志
            if assigned_users:
                user_list = '、'.join(assigned_users)
                _log_activity('分配角色', f'为角色"{role.name}"分配了{len(user_ids)}个用户: {user_list}')
            else:
                _log_activity('分配角色', f'清空了角色"{role.name}"的所有用户分配')
            
            flash(f'成功为{len(user_ids)}个用户分配角色')
            return redirect(url_for('main.role_permission_management'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'分配角色失败: {str(e)}', 'error')
    
    # 获取所有用户
    all_users = User.query.filter_by(is_active=True).order_by(User.username).all()
    # 获取已分配该角色的用户ID列表
    assigned_user_ids = [u.id for u in role.users]
    
    return render_template('main/manage_role_users.html',
                         title=f'分配用户 - {role.name}',
                         role=role,
                         all_users=all_users,
                         assigned_user_ids=assigned_user_ids)


@bp.route('/admin/role/<int:role_id>/delete', methods=['POST'])
@login_required
def delete_role(role_id):
    """删除角色"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        from app.models import UserCustomRole
        
        role = RoleDefinition.query.get_or_404(role_id)
        
        if not role.is_custom:
            return jsonify({'success': False, 'message': '不能删除系统内置角色'}), 400
        
        role_name = role.name
        
        # 先删除所有用户角色关联记录
        UserCustomRole.query.filter_by(role_id=role_id).delete()
        
        # 删除角色本身(权限会通过级联删除自动删除)
        db.session.delete(role)
        db.session.commit()
        
        _log_activity('删除角色', f'删除角色: {role_name}')
        return jsonify({'success': True, 'message': f'角色"{role_name}"已删除'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/my-workflow-orders')
@login_required
def api_my_workflow_orders():
    """获取与当前用户相关的所有工单(我创建的+待我审批的)"""
    try:
        workflow_type = request.args.get('type', '')
        orders = []
        
        # 根据类型获取工单
        if workflow_type == 'repair_order':
            # 我创建的维修工单
            my_orders = RepairOrder.query.filter_by(requester_id=current_user.id).order_by(RepairOrder.id.desc()).limit(50).all()
            for order in my_orders:
                orders.append({
                    'id': order.id,
                    'label': f"#{order.id} - {order.equipment.name if order.equipment else '未知设备'} - {order.status_display}",
                    'status': order.status,
                    'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
                    'is_my_approval': False
                })
            
            # 待我审批的维修工单
            pending_approvals = ApprovalWorkflow.query.filter_by(
                approver_id=current_user.id,
                order_type='repair_order',
                status='pending'
            ).all()
            for approval in pending_approvals:
                order = RepairOrder.query.get(approval.order_id)
                if order and not any(o['id'] == order.id for o in orders):
                    orders.append({
                        'id': order.id,
                        'label': f"#{order.id} - {order.equipment.name if order.equipment else '未知设备'} - 待我审批",
                        'status': order.status,
                        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
                        'is_my_approval': True
                    })
        
        elif workflow_type == 'part_request_order':
            # 我创建的配件申请
            my_orders = PartRequestOrder.query.filter_by(requester_id=current_user.id).order_by(PartRequestOrder.id.desc()).limit(50).all()
            for order in my_orders:
                orders.append({
                    'id': order.id,
                    'label': f"#{order.id} - {order.reason or '配件申请'} - {order.status_display}",
                    'status': order.status,
                    'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
                    'is_my_approval': False
                })
            
            # 待我审批的配件申请
            pending_approvals = ApprovalWorkflow.query.filter_by(
                approver_id=current_user.id,
                order_type='part_request_order',
                status='pending'
            ).all()
            for approval in pending_approvals:
                order = PartRequestOrder.query.get(approval.order_id)
                if order and not any(o['id'] == order.id for o in orders):
                    orders.append({
                        'id': order.id,
                        'label': f"#{order.id} - {order.reason or '配件申请'} - 待我审批",
                        'status': order.status,
                        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
                        'is_my_approval': True
                    })
        
        elif workflow_type == 'equipment_transfer':
            # 我创建的设备调拨
            my_orders = EquipmentTransfer.query.filter_by(requester_id=current_user.id).order_by(EquipmentTransfer.id.desc()).limit(50).all()
            for order in my_orders:
                orders.append({
                    'id': order.id,
                    'label': f"#{order.id} - {order.equipment.name if order.equipment else '未知设备'} - {order.status_display}",
                    'status': order.status,
                    'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
                    'is_my_approval': False
                })
            
            # 待我审批的调拨
            pending_approvals = ApprovalWorkflow.query.filter_by(
                approver_id=current_user.id,
                order_type='equipment_transfer',
                status='pending'
            ).all()
            for approval in pending_approvals:
                order = EquipmentTransfer.query.get(approval.order_id)
                if order and not any(o['id'] == order.id for o in orders):
                    orders.append({
                        'id': order.id,
                        'label': f"#{order.id} - {order.equipment.name if order.equipment else '未知设备'} - 待我审批",
                        'status': order.status,
                        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
                        'is_my_approval': True
                    })
        
        elif workflow_type == 'equipment_scrap':
            # 我创建的报废申请
            my_orders = EquipmentScrap.query.filter_by(requester_id=current_user.id).order_by(EquipmentScrap.id.desc()).limit(50).all()
            for order in my_orders:
                orders.append({
                    'id': order.id,
                    'label': f"#{order.id} - {order.equipment.name if order.equipment else '未知设备'} - {order.status_display}",
                    'status': order.status,
                    'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
                    'is_my_approval': False
                })
            
            # 待我审批的报废
            pending_approvals = ApprovalWorkflow.query.filter_by(
                approver_id=current_user.id,
                order_type='equipment_scrap',
                status='pending'
            ).all()
            for approval in pending_approvals:
                order = EquipmentScrap.query.get(approval.order_id)
                if order and not any(o['id'] == order.id for o in orders):
                    orders.append({
                        'id': order.id,
                        'label': f"#{order.id} - {order.equipment.name if order.equipment else '未知设备'} - 待我审批",
                        'status': order.status,
                        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
                        'is_my_approval': True
                    })
        
        elif workflow_type == 'equipment_loan':
            # 我创建的借用申请
            my_orders = EquipmentLoan.query.filter_by(borrower_id=current_user.id).order_by(EquipmentLoan.id.desc()).limit(50).all()
            for order in my_orders:
                orders.append({
                    'id': order.id,
                    'label': f"#{order.id} - {order.equipment.name if order.equipment else '未知设备'} - {order.status_display}",
                    'status': order.status,
                    'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
                    'is_my_approval': False
                })
            
            # 待我审批的借用
            pending_approvals = ApprovalWorkflow.query.filter_by(
                approver_id=current_user.id,
                order_type='equipment_loan',
                status='pending'
            ).all()
            for approval in pending_approvals:
                order = EquipmentLoan.query.get(approval.order_id)
                if order and not any(o['id'] == order.id for o in orders):
                    orders.append({
                        'id': order.id,
                        'label': f"#{order.id} - {order.equipment.name if order.equipment else '未知设备'} - 待我审批",
                        'status': order.status,
                        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
                        'is_my_approval': True
                    })
        
        elif workflow_type == 'equipment_application':
            # 我创建的设备申请
            my_orders = EquipmentApplication.query.filter_by(requester_id=current_user.id).order_by(EquipmentApplication.id.desc()).limit(50).all()
            for order in my_orders:
                orders.append({
                    'id': order.id,
                    'label': f"#{order.id} - {order.equipment_name} - {order.status_display}",
                    'status': order.status,
                    'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
                    'is_my_approval': False
                })
            
            # 待我审批的设备申请
            pending_approvals = ApprovalWorkflow.query.filter_by(
                approver_id=current_user.id,
                order_type='equipment_application',
                status='pending'
            ).all()
            for approval in pending_approvals:
                order = EquipmentApplication.query.get(approval.order_id)
                if order and not any(o['id'] == order.id for o in orders):
                    orders.append({
                        'id': order.id,
                        'label': f"#{order.id} - {order.equipment_name} - 待我审批",
                        'status': order.status,
                        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
                        'is_my_approval': True
                    })
        
        return jsonify({
            'success': True,
            'data': orders
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== 审批中心路由 ====================

@bp.route('/my_pending_approvals')
@login_required
def my_pending_approvals():
    """我的待审批页面"""
    return render_template('main/my_pending_approvals.html')


@bp.route('/my_approvals_history')
@login_required  
def my_approvals_history():
    """我的审批历史"""
    from app.approval_models import ApprovalStep, ApprovalInstance
    
    # 获取我处理过的所有审批
    processed_steps = ApprovalStep.query.filter(
        ApprovalStep.approver_id == current_user.id,
        ApprovalStep.status.in_(['approved', 'rejected'])
    ).order_by(ApprovalStep.processed_at.desc()).all()
    
    return render_template('main/my_approvals_history.html', steps=processed_steps)


@bp.route('/my_initiated_approvals')
@login_required
def my_initiated_approvals():
    """我发起的审批"""
    from app.approval_models import ApprovalInstance
    
    instances = ApprovalInstance.query.filter_by(
        initiator_id=current_user.id
    ).order_by(ApprovalInstance.created_at.desc()).all()
    
    return render_template('main/my_initiated_approvals.html', instances=instances)


@bp.route('/approval_delegate_manage')
@login_required
def approval_delegate_manage():
    """审批委托管理"""
    from app.approval_models import ApprovalDelegate
    
    # 获取我的委托记录
    my_delegates = ApprovalDelegate.query.filter_by(
        delegator_id=current_user.id
    ).order_by(ApprovalDelegate.created_at.desc()).all()
    
    # 获取委托给我的记录
    delegated_to_me = ApprovalDelegate.query.filter_by(
        delegate_id=current_user.id,
        is_active=True
    ).filter(
        ApprovalDelegate.start_date <= get_beijing_now(),
        ApprovalDelegate.end_date >= get_beijing_now()
    ).all()
    
    return render_template('main/approval_delegate_manage.html',
                         my_delegates=my_delegates,
                         delegated_to_me=delegated_to_me)


# ==================== 简化审批功能 ====================

@bp.route('/simple_approvals')
@login_required
def simple_approvals():
    """简化的审批页面 - 显示所有审批流程清单"""
    if current_user.role not in ['admin', 'super_admin']:
        flash('只有管理员可以访问此页面')
        return redirect(url_for('main.index'))
    
    # 获取所有待审批的审批流程（使用 ApprovalWorkflow）
    pending_approvals = ApprovalWorkflow.query.filter_by(status='pending').order_by(
        ApprovalWorkflow.created_date.desc()
    ).all()
    
    # 按工单类型分组
    repair_pending = []
    part_pending = []
    loan_pending = []
    transfer_pending = []
    scrap_pending = []
    application_pending = []
    
    for approval in pending_approvals:
        if approval.order_type == 'repair_order':
            repair_pending.append(approval)
        elif approval.order_type == 'part_request_order':
            part_pending.append(approval)
        elif approval.order_type == 'equipment_loan':
            loan_pending.append(approval)
        elif approval.order_type == 'equipment_transfer':
            transfer_pending.append(approval)
        elif approval.order_type == 'equipment_scrap':
            scrap_pending.append(approval)
        elif approval.order_type == 'equipment_application':
            application_pending.append(approval)
    
    # 统计数据
    total_pending = len(pending_approvals)
    
    return render_template('main/simple_approval.html',
                         repair_pending=repair_pending,
                         part_pending=part_pending,
                         loan_pending=loan_pending,
                         transfer_pending=transfer_pending,
                         scrap_pending=scrap_pending,
                         application_pending=application_pending,
                         total_pending=total_pending,
                         title='快速审批')


@bp.route('/simple_approve/<order_type>/<int:order_id>', methods=['POST'])
@login_required
def simple_approve(order_type, order_id):
    """简化的审批处理（管理员一键审批各类型工单）"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '只有管理员可以审批'}), 403
    
    action = request.form.get('action')  # 'approve' or 'reject'
    comments = request.form.get('comments', '')
    
    try:
        # 兼容旧的 order_type 简写
        normalized_type = {
            'repair': 'repair_order',
            'part': 'part_request_order'
        }.get(order_type, order_type)

        # 找到对应的审批记录，便于关闭待审批状态
        pending_approval = ApprovalWorkflow.query.filter_by(
            order_type=normalized_type,
            order_id=order_id,
            status='pending'
        ).order_by(ApprovalWorkflow.created_date).first()

        now = get_beijing_now()
        success = action == 'approve'

        if normalized_type == 'repair_order':
            order = RepairOrder.query.get_or_404(order_id)
            order.status = 'approved' if success else 'rejected'
            order.admin_approved = success
            order.admin_id = current_user.id
            if success and order.equipment:
                order.equipment.status = 'repair'
            _log_activity('审批维修工单', f'管理员{"批准" if success else "拒绝"}了维修工单 #{order_id}')

        elif normalized_type == 'part_request_order':
            order = PartRequestOrder.query.get_or_404(order_id)
            order.status = 'approved' if success else 'rejected'
            order.admin_approved = success
            order.admin_id = current_user.id
            _log_activity('审批配件申请', f'管理员{ "批准" if success else "拒绝" }了配件申请 #{order_id}')

        elif normalized_type == 'equipment_loan':
            order = EquipmentLoan.query.get_or_404(order_id)
            order.status = 'approved' if success else 'rejected'
            order.approved_by = current_user.id
            order.approved_date = now
            _log_activity('审批借用申请', f'管理员{ "批准" if success else "拒绝" }了借用申请 #{order_id}')

        elif normalized_type == 'equipment_transfer':
            order = EquipmentTransfer.query.get_or_404(order_id)
            order.status = 'approved' if success else 'rejected'
            order.updated_date = now
            _log_activity('审批调拨申请', f'管理员{ "批准" if success else "拒绝" }了调拨申请 #{order_id}')

        elif normalized_type == 'equipment_scrap':
            order = EquipmentScrap.query.get_or_404(order_id)
            order.status = 'approved' if success else 'rejected'
            order.updated_date = now
            if success and order.equipment:
                order.equipment.status = 'scrapped'
            _log_activity('审批报废申请', f'管理员{ "批准" if success else "拒绝" }了报废申请 #{order_id}')

        elif normalized_type == 'equipment_application':
            order = EquipmentApplication.query.get_or_404(order_id)
            order.status = 'approved' if success else 'rejected'
            order.approved_date = now
            _log_activity('审批设备申请', f'管理员{ "批准" if success else "拒绝" }了设备申请 #{order_id}')

        else:
            return jsonify({'success': False, 'message': '不支持的工单类型'}), 400

        # 同步关闭待审批节点
        if pending_approval:
            pending_approval.status = 'approved' if success else 'rejected'
            pending_approval.approved_date = now
            pending_approval.comments = comments
            pending_approval.admin_action = 'force_approve' if success else 'force_reject'
            pending_approval.admin_operator_id = current_user.id

        db.session.commit()
        return jsonify({'success': True, 'message': '操作成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# =========================
# 定时任务手动触发路由(管理员)
# =========================

@bp.route('/admin/scheduler/trigger/<task_name>')
@login_required
def trigger_scheduled_task(task_name):
    """手动触发定时任务(仅管理员)"""
    if current_user.role != 'admin':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        from app.scheduler import check_overdue_loans, check_upcoming_return_dates, check_pending_return_inspections, check_maintenance_due, check_pending_approvals
        
        task_map = {
            'maintenance_due': ('检查保养计划', check_maintenance_due),
            'overdue_loans': ('检查逾期借用', check_overdue_loans),
            'upcoming_returns': ('检查即将到期', check_upcoming_return_dates),
            'pending_inspections': ('检查待验收', check_pending_return_inspections),
            'pending_approvals': ('检查待审批事项', check_pending_approvals)
        }
        
        if task_name not in task_map:
            flash('未知的任务名称', 'danger')
            return redirect(url_for('main.index'))
        
        task_display_name, task_func = task_map[task_name]
        task_func()
        
        flash(f'定时任务"{task_display_name}"已手动执行完成', 'success')
        _log_activity('手动触发定时任务', f'管理员手动触发了定时任务: {task_display_name}')
        
    except Exception as e:
        flash(f'任务执行失败: {str(e)}', 'danger')
        current_app.logger.error(f'手动触发定时任务失败: {str(e)}')
    
    return redirect(url_for('main.index'))


@bp.route('/admin/scheduler/status')
@login_required
def scheduler_status():
    """查看定时任务状态(仅管理员)"""
    if current_user.role != 'admin':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    tasks = [
        {
            'name': 'maintenance_due',
            'display_name': '检查保养计划',
            'schedule': '每天早上8:00',
            'description': '检查7天内到期的保养计划,发送提醒给负责人'
        },
        {
            'name': 'overdue_loans',
            'display_name': '检查逾期借用',
            'schedule': '每天早上9:00',
            'description': '检查所有借用中且已逾期的记录,发送通知给借用人和管理员'
        },
        {
            'name': 'upcoming_returns',
            'display_name': '检查即将到期',
            'schedule': '每天早上9:00',
            'description': '检查3天内到期的借用,发送提醒给借用人'
        },
        {
            'name': 'pending_inspections',
            'display_name': '检查待验收',
            'schedule': '每天早上10:00',
            'description': '检查超过2天未处理的归还验收申请,发送通知给管理员'
        },
        {
            'name': 'pending_approvals',
            'display_name': '检查待审批事项',
            'schedule': '每天上午10:30和下午15:00',
            'description': '检查所有待审批的工单,按审批人汇总统计并发送提醒通知'
        }
    ]
    
    return render_template('main/scheduler_status.html', title='定时任务状态', tasks=tasks)


# ==================== 聊天系统 ====================

@bp.route('/chat_websocket')
@login_required
def chat_websocket():
    """聊天页面(WebSocket版本)"""
    return render_template('chat.html', title='聊天')


@bp.route('/chat/admin')
@login_required
def chat_admin():
    """聊天管理页面(仅管理员)"""
    if current_user.role != 'admin':
        flash('需要管理员权限', 'error')
        return redirect(url_for('main.index'))
    return render_template('chat_admin.html', title='聊天管理')
