# -*- coding: utf-8 -*-
"""审批流程统计报表路由"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db, get_beijing_now
from app.workflow_models_new import WorkflowInstance
from app.models import ApprovalWorkflow, User, RepairOrder, PartRequestOrder
from app.models import EquipmentTransfer, EquipmentLoan, Department
from sqlalchemy import func, case, extract
from datetime import datetime, timedelta

bp = Blueprint('approval_report', __name__)


@bp.route('/reports/approval-statistics')
@login_required
def approval_statistics():
    """审批流程统计报表"""
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    # 时间范围筛选
    days = request.args.get('days', type=int, default=30)
    since_date = get_beijing_now() - timedelta(days=days)
    
    # 部门筛选
    dept_id = request.args.get('department', type=int)
    
    # 1. 审批流程状态统计（基于 WorkflowInstance）
    status_stats = db.session.query(
        WorkflowInstance.status,
        func.count(WorkflowInstance.id).label('count')
    ).filter(
        WorkflowInstance.started_at >= since_date
    ).group_by(WorkflowInstance.status).all()
    
    # 2. 按业务类型统计（基于 WorkflowInstance）
    type_stats = db.session.query(
        WorkflowInstance.order_type,
        func.count(WorkflowInstance.id).label('total_count'),
        func.sum(case((WorkflowInstance.status == 'approved', 1), else_=0)).label('approved_count'),
        func.sum(case((WorkflowInstance.status == 'rejected', 1), else_=0)).label('rejected_count'),
        func.sum(case((WorkflowInstance.status == 'pending', 1), else_=0)).label('pending_count')
    ).filter(
        WorkflowInstance.started_at >= since_date
    ).group_by(WorkflowInstance.order_type).all()
    
    # 3. 审批效率统计（平均审批时长）
    efficiency_stats = db.session.query(
        WorkflowInstance.order_type,
        func.avg(
            extract('epoch', WorkflowInstance.finished_at - WorkflowInstance.started_at) / 3600
        ).label('avg_hours'),
        func.min(
            extract('epoch', WorkflowInstance.finished_at - WorkflowInstance.started_at) / 3600
        ).label('min_hours'),
        func.max(
            extract('epoch', WorkflowInstance.finished_at - WorkflowInstance.started_at) / 3600
        ).label('max_hours')
    ).filter(
        WorkflowInstance.started_at >= since_date,
        WorkflowInstance.finished_at.isnot(None),
        WorkflowInstance.status.in_(['approved', 'rejected', 'completed'])
    ).group_by(WorkflowInstance.order_type).all()
    
    # 4. 审批人工作量统计(基于 ApprovalWorkflow)
    approver_stats = db.session.query(
        User.username,
        func.count(ApprovalWorkflow.id).label('total_approvals'),
        func.sum(case((ApprovalWorkflow.status == 'approved', 1), else_=0)).label('approved'),
        func.sum(case((ApprovalWorkflow.status == 'rejected', 1), else_=0)).label('rejected')
    ).join(
        User, ApprovalWorkflow.approver_id == User.id
    ).filter(
        ApprovalWorkflow.created_date >= since_date,
        ApprovalWorkflow.status.in_(['approved', 'rejected'])
    ).group_by(User.id, User.username).order_by(
        func.count(ApprovalWorkflow.id).desc()
    ).limit(20).all()
    
    # 5. 申请人统计（基于各类工单）
    # 维修工单申请人
    repair_requesters = db.session.query(
        User.id.label('user_id'),
        User.username,
        func.count(RepairOrder.id).label('total_requests'),
        func.sum(case((RepairOrder.status == 'approved', 1), else_=0)).label('approved'),
        func.sum(case((RepairOrder.status == 'rejected', 1), else_=0)).label('rejected'),
        func.sum(case((RepairOrder.status == 'submitted', 1), else_=0)).label('pending')
    ).join(
        User, RepairOrder.requester_id == User.id
    ).filter(
        RepairOrder.created_date >= since_date
    ).group_by(User.id, User.username).all()
    
    # 配件申请人
    part_requesters = db.session.query(
        User.id.label('user_id'),
        User.username,
        func.count(PartRequestOrder.id).label('total_requests'),
        func.sum(case((PartRequestOrder.status == 'approved', 1), else_=0)).label('approved'),
        func.sum(case((PartRequestOrder.status == 'rejected', 1), else_=0)).label('rejected'),
        func.sum(case((PartRequestOrder.status == 'submitted', 1), else_=0)).label('pending')
    ).join(
        User, PartRequestOrder.requester_id == User.id
    ).filter(
        PartRequestOrder.created_date >= since_date
    ).group_by(User.id, User.username).all()
    
    # 合并申请人统计
    requester_dict = {}
    for item in repair_requesters + part_requesters:
        uid = item[0]
        if uid not in requester_dict:
            requester_dict[uid] = {
                'username': item[1],
                'total': 0,
                'approved': 0,
                'rejected': 0,
                'pending': 0
            }
        requester_dict[uid]['total'] += item[2]
        requester_dict[uid]['approved'] += item[3]
        requester_dict[uid]['rejected'] += item[4]
        requester_dict[uid]['pending'] += item[5]
    
    requester_stats = sorted(
        [(v['username'], v['total'], v['approved'], v['rejected'], v['pending']) 
         for v in requester_dict.values()],
        key=lambda x: x[1], reverse=True
    )[:20]
    
    # 6. 每日审批趋势（最近N天）
    daily_trend = db.session.query(
        func.date(WorkflowInstance.started_at).label('date'),
        func.count(WorkflowInstance.id).label('count')
    ).filter(
        WorkflowInstance.started_at >= since_date
    ).group_by(func.date(WorkflowInstance.started_at)).order_by('date').all()
    
    departments = Department.query.all()
    
    return render_template(
        'main/approval_statistics.html',
        title='审批流程统计',
        status_stats=status_stats,
        type_stats=type_stats,
        efficiency_stats=efficiency_stats,
        approver_stats=approver_stats,
        requester_stats=requester_stats,
        daily_trend=daily_trend,
        departments=departments,
        selected_days=days,
        selected_dept=dept_id
    )
