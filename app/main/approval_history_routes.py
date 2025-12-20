"""审批历史与详情（兼容老版 ApprovalWorkflow）。"""
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from app.models import (
    User, RepairOrder, PartRequestOrder, EquipmentApplication,
    EquipmentLoan, EquipmentTransfer, EquipmentScrap, UserActivityLog,
    ApprovalWorkflow
)
from app.approval_models import ApprovalInstance, ApprovalStep
from app.main import bp

@bp.route('/approval_history')
@login_required
def approval_history():
    """审批历史/待办视图（基于老版 ApprovalWorkflow）。"""
    page = request.args.get('page', 1, type=int)
    order_type = request.args.get('order_type', '')
    status = request.args.get('status', '')

    # 使用老版 ApprovalWorkflow 模型查询
    query = ApprovalWorkflow.query

    # 权限过滤：非管理员只能看到自己审批的工单
    if current_user.role not in ['admin', 'super_admin']:
        query = query.filter(ApprovalWorkflow.approver_id == current_user.id)

    if order_type:
        query = query.filter(ApprovalWorkflow.order_type == order_type)
    if status:
        query = query.filter(ApprovalWorkflow.status == status)

    pagination = query.order_by(ApprovalWorkflow.created_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    approvals = pagination.items

    return render_template(
        'main/approval_history.html',
        title='审批历史',
        approvals=approvals,
        pagination=pagination,
        order_type=order_type,
        status=status
    )


@bp.route('/approval_detail/<int:instance_id>')
@login_required
def approval_detail(instance_id):
    """审批实例详情（新模型）。"""
    instance = ApprovalInstance.query.get_or_404(instance_id)

    if current_user.role not in ['admin', 'super_admin']:
        related = db.session.query(ApprovalStep.instance_id).filter(
            ApprovalStep.instance_id == instance.id,
            ApprovalStep.approver_id == current_user.id
        ).first()
        if instance.requester_id != current_user.id and not related:
            flash('无权查看此审批记录', 'danger')
            return redirect(url_for('main.approval_history'))

    order = _get_order_object(instance.order_type, instance.order_id)
    steps = ApprovalStep.query.filter_by(instance_id=instance.id).order_by(ApprovalStep.sequence).all()

    return render_template(
        'main/approval_detail.html',
        title='审批详情',
        instance=instance,
        order=order,
        steps=steps
    )


def _get_order_info(order_type, order_id):
    """获取工单基本信息"""
    order = _get_order_object(order_type, order_id)
    if not order:
        return None
    
    info = {
        'id': order.id,
        'status': order.status,
        'created_date': order.created_date
    }
    
    # 根据类型添加特定字段
    if order_type == 'repair_order':
        info['description'] = order.description
        info['requester_id'] = order.requester_id
        info['requester_name'] = order.requester.username if order.requester else ''
        info['repair_cost'] = float(order.repair_cost) if order.repair_cost else 0.0
    elif order_type == 'part_request_order':
        info['requester_id'] = order.requester_id
        info['requester_name'] = order.requester.username if order.requester else ''
    elif order_type == 'equipment_application':
        info['requester_id'] = order.applicant_id
        info['requester_name'] = order.applicant.username if order.applicant else ''
        info['equipment_type'] = order.equipment_type
    
    return info


def _get_order_object(order_type, order_id):
    """获取工单对象"""
    if order_type == 'repair_order':
        return RepairOrder.query.get(order_id)
    elif order_type == 'part_request_order':
        return PartRequestOrder.query.get(order_id)
    elif order_type == 'equipment_application':
        return EquipmentApplication.query.get(order_id)
    elif order_type == 'equipment_loan':
        return EquipmentLoan.query.get(order_id)
    elif order_type == 'equipment_transfer':
        return EquipmentTransfer.query.get(order_id)
    elif order_type == 'equipment_scrap':
        return EquipmentScrap.query.get(order_id)
    return None


def _log_activity(action, description):
    """记录用户活动"""
    log = UserActivityLog(
        user_id=current_user.id,
        action=action,
        description=description
    )
    db.session.add(log)
