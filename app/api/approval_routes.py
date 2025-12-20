"""
企业级审批系统 REST API 路由
提供审批流程的核心操作接口
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db, get_beijing_now
from app.models import User
from app.approval_models import (
    WorkflowTemplate, WorkflowNode, ApprovalInstance, 
    ApprovalStep, ApprovalLog, ApprovalDelegate, ApprovalReminder
)
from app.approval_engine import ApprovalEngine
from datetime import datetime, timedelta
import json


approval_api = Blueprint('approval_api', __name__)


# ========== 工作流启动 ==========

@approval_api.route('/start', methods=['POST'])
@login_required
def start_workflow():
    """
    启动工作流
    POST /api/approval/start
    Body: {
        "order_type": "repair_order",
        "order_id": 123,
        "template_code": "repair_approval_v1"  # 可选,不指定则使用默认模板
    }
    """
    try:
        data = request.get_json()
        order_type = data.get('order_type')
        order_id = data.get('order_id')
        template_code = data.get('template_code')
        
        if not order_type or not order_id:
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
        
        # 查找模板
        if template_code:
            template = WorkflowTemplate.query.filter_by(
                code=template_code, 
                is_active=True
            ).order_by(WorkflowTemplate.version.desc()).first()
        else:
            # 使用默认模板
            template = WorkflowTemplate.query.filter_by(
                order_type=order_type,
                is_active=True,
                is_default=True
            ).order_by(WorkflowTemplate.version.desc()).first()
        
        if not template:
            return jsonify({'success': False, 'message': '未找到可用的审批模板'}), 404
        
        # 启动工作流
        instance = ApprovalEngine.start_workflow(
            template_id=template.id,
            order_type=order_type,
            order_id=order_id,
            initiator_id=current_user.id
        )
        
        return jsonify({
            'success': True,
            'message': '审批流程已启动',
            'data': {
                'instance_id': instance.id,
                'status': instance.status,
                'current_node': instance.current_node.name if instance.current_node else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'启动失败: {str(e)}'}), 500


# ========== 审批操作 ==========

@approval_api.route('/approve/<int:step_id>', methods=['POST'])
@login_required
def approve_step(step_id):
    """
    审批通过
    POST /api/approval/approve/{step_id}
    Body: {
        "comments": "同意",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0..."
    }
    """
    try:
        step = ApprovalStep.query.get_or_404(step_id)
        
        # 权限验证
        effective_approver = ApprovalEngine._check_delegate(step.approver_id, step.instance.order_type)
        if effective_approver.id != current_user.id:
            return jsonify({'success': False, 'message': '无权审批此步骤'}), 403
        
        data = request.get_json() or {}
        comments = data.get('comments', '')
        ip_address = data.get('ip_address', request.remote_addr)
        user_agent = data.get('user_agent', request.headers.get('User-Agent', ''))
        
        # 执行审批
        result = ApprovalEngine.approve_step(
            step_id=step_id,
            approver_id=current_user.id,
            comments=comments,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return jsonify({
            'success': True,
            'message': '审批通过',
            'data': {
                'instance_status': result['instance'].status,
                'next_node': result['next_node'].name if result.get('next_node') else None,
                'is_completed': result['instance'].status in ['approved', 'rejected']
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'审批失败: {str(e)}'}), 500


@approval_api.route('/reject/<int:step_id>', methods=['POST'])
@login_required
def reject_step(step_id):
    """
    审批拒绝
    POST /api/approval/reject/{step_id}
    Body: {
        "comments": "不同意,理由是...",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0..."
    }
    """
    try:
        step = ApprovalStep.query.get_or_404(step_id)
        
        # 权限验证
        effective_approver = ApprovalEngine._check_delegate(step.approver_id, step.instance.order_type)
        if effective_approver.id != current_user.id:
            return jsonify({'success': False, 'message': '无权审批此步骤'}), 403
        
        data = request.get_json() or {}
        comments = data.get('comments', '')
        if not comments:
            return jsonify({'success': False, 'message': '拒绝时必须填写意见'}), 400
        
        ip_address = data.get('ip_address', request.remote_addr)
        user_agent = data.get('user_agent', request.headers.get('User-Agent', ''))
        
        # 执行拒绝
        result = ApprovalEngine.reject_step(
            step_id=step_id,
            approver_id=current_user.id,
            comments=comments,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return jsonify({
            'success': True,
            'message': '审批已拒绝',
            'data': {
                'instance_status': result['instance'].status,
                'is_completed': True
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'拒绝失败: {str(e)}'}), 500


# ========== 查询接口 ==========

@approval_api.route('/my-pending', methods=['GET'])
@login_required
def get_my_pending_approvals():
    """
    获取我的待审批列表
    GET /api/approval/my-pending?page=1&per_page=20
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 查询待审批步骤
        query = ApprovalStep.query.filter_by(
            approver_id=current_user.id,
            status='pending'
        ).order_by(ApprovalStep.deadline.asc().nullslast(), ApprovalStep.assigned_date.asc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        steps = []
        for step in pagination.items:
            instance = step.instance
            steps.append({
                'step_id': step.id,
                'instance_id': instance.id,
                'order_type': instance.order_type,
                'order_id': instance.order_id,
                'node_name': step.node.name,
                'initiator': instance.requester.username if getattr(instance, 'requester', None) else None,
                'deadline': step.deadline.isoformat() if step.deadline else None,
                'is_overdue': step.deadline < get_beijing_now() if step.deadline else False,
                'assigned_at': step.assigned_date.isoformat() if step.assigned_date else None,
                'is_parallel': getattr(step.node, 'is_parallel', False)
            })
        
        return jsonify({
            'success': True,
            'data': {
                'items': steps,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


@approval_api.route('/instance/<int:instance_id>', methods=['GET'])
@login_required
def get_instance_detail(instance_id):
    """
    获取审批实例详情
    GET /api/approval/instance/{instance_id}
    """
    try:
        instance = ApprovalInstance.query.get_or_404(instance_id)
        
        # 获取所有步骤
        steps = []
        for step in instance.steps:
            steps.append({
                'id': step.id,
                'node_name': step.node.name if step.node else None,
                'approver': step.approver.username if step.approver else '系统自动',
                'status': step.status,
                'decision': step.result,
                'comments': step.comment,
                'assigned_at': step.assigned_date.isoformat() if step.assigned_date else None,
                'processed_at': step.approved_date.isoformat() if step.approved_date else None,
                'deadline': step.deadline.isoformat() if step.deadline else None,
                'is_parallel': getattr(step.node, 'is_parallel', False)
            })
        
        # 获取操作日志
        logs = []
        from app.approval_models import ApprovalLog
        for log in ApprovalLog.query.filter_by(instance_id=instance.id).order_by(ApprovalLog.created_date.asc()).all():
            logs.append({
                'action': log.action,
                'actor': log.operator.username if log.operator else '系统',
                'comments': log.comment,
                'created_at': log.created_date.isoformat() if log.created_date else None
            })
        
        return jsonify({
            'success': True,
            'data': {
                'id': instance.id,
                'order_type': instance.order_type,
                'order_id': instance.order_id,
                'status': instance.status,
                'initiator': instance.requester.username if getattr(instance, 'requester', None) else None,
                'current_node': instance.current_node.name if instance.current_node else None,
                'started_at': instance.started_date.isoformat() if getattr(instance, 'started_date', None) else None,
                'completed_at': instance.completed_date.isoformat() if getattr(instance, 'completed_date', None) else None,
                'steps': steps,
                'logs': logs
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


# ========== 委托管理 ==========

@approval_api.route('/delegate', methods=['POST'])
@login_required
def create_delegate():
    """
    创建审批委托
    POST /api/approval/delegate
    Body: {
        "delegate_id": 5,
        "start_date": "2025-01-15T00:00:00",
        "end_date": "2025-01-20T23:59:59",
        "scope": "all",  # all 或 order_type
        "order_types": ["repair_order", "part_request"],  # 当scope=order_type时必填
        "reason": "出差期间委托"
    }
    """
    try:
        data = request.get_json()
        delegate_id = data.get('delegate_id')
        start_date = datetime.fromisoformat(data.get('start_date'))
        end_date = datetime.fromisoformat(data.get('end_date'))
        order_types = data.get('order_types', [])
        role_ids = data.get('role_ids', [])
        reason = data.get('reason', '')
        
        if not delegate_id:
            return jsonify({'success': False, 'message': '缺少被委托人'}), 400
        
        if start_date >= end_date:
            return jsonify({'success': False, 'message': '结束时间必须晚于开始时间'}), 400
        
        # 当指定工单类型时需提供列表
        if order_types and not isinstance(order_types, list):
            return jsonify({'success': False, 'message': 'order_types 必须为数组'}), 400
        
        # 创建委托
        from app.approval_models import ApprovalDelegate
        delegate = ApprovalDelegate(
            user_id=current_user.id,
            delegate_to_id=delegate_id,
            start_date=start_date,
            end_date=end_date,
            order_types=order_types if order_types else None,
            role_ids=role_ids if role_ids else None,
            reason=reason,
            is_active=True
        )
        
        db.session.add(delegate)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '委托创建成功',
            'data': {'delegate_id': delegate.id}
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500


@approval_api.route('/delegate/<int:delegate_id>', methods=['DELETE'])
@login_required
def cancel_delegate(delegate_id):
    """
    取消审批委托
    DELETE /api/approval/delegate/{delegate_id}
    """
    try:
        from app.approval_models import ApprovalDelegate
        delegate = ApprovalDelegate.query.get_or_404(delegate_id)
        
        if delegate.user_id != current_user.id:
            return jsonify({'success': False, 'message': '只能取消自己的委托'}), 403
        
        delegate.is_active = False
        db.session.commit()
        
        return jsonify({'success': True, 'message': '委托已取消'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'取消失败: {str(e)}'}), 500


@approval_api.route('/my-delegates', methods=['GET'])
@login_required
def get_my_delegates():
    """
    获取我的委托列表
    GET /api/approval/my-delegates?active_only=true
    """
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        from app.approval_models import ApprovalDelegate
        query = ApprovalDelegate.query.filter_by(user_id=current_user.id)
        if active_only:
            query = query.filter_by(is_active=True)
        delegates = query.order_by(ApprovalDelegate.created_date.desc()).all()
        items = []
        for d in delegates:
            items.append({
                'id': d.id,
                'delegate': d.delegate_to.username if d.delegate_to else None,
                'start_date': d.start_date.isoformat() if d.start_date else None,
                'end_date': d.end_date.isoformat() if d.end_date else None,
                'order_types': d.order_types if d.order_types else [],
                'role_ids': d.role_ids if d.role_ids else [],
                'reason': d.reason,
                'is_active': d.is_active
            })
        
        return jsonify({
            'success': True,
            'data': items
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


# ========== 管理员操作 ==========

@approval_api.route('/transfer/<int:step_id>', methods=['POST'])
@login_required
def transfer_step(step_id):
    """
    转交审批(仅管理员)
    POST /api/approval/transfer/{step_id}
    Body: {
        "to_user_id": 10,
        "reason": "原审批人请假"
    }
    """
    try:
        if not current_user.is_admin():
            return jsonify({'success': False, 'message': '仅管理员可以转交审批'}), 403
        
        step = ApprovalStep.query.get_or_404(step_id)
        
        if step.status != 'pending':
            return jsonify({'success': False, 'message': '只能转交待审批的步骤'}), 400
        
        data = request.get_json()
        to_user_id = data.get('to_user_id')
        reason = data.get('reason', '')
        
        if not to_user_id:
            return jsonify({'success': False, 'message': '缺少目标用户'}), 400
        
        to_user = User.query.get(to_user_id)
        if not to_user:
            return jsonify({'success': False, 'message': '目标用户不存在'}), 404
        
        # 记录原审批人
        from_user_id = step.approver_id
        
        # 更新步骤
        step.approver_id = to_user_id
        step.assigned_date = get_beijing_now()
        
        # 记录日志
        from app.approval_models import ApprovalLog
        log = ApprovalLog(
            instance_id=step.instance_id,
            step_id=step.id,
            action='transfer',
            operator_id=current_user.id,
            comment=reason,
            old_value={'from_user_id': from_user_id},
            new_value={'to_user_id': to_user_id},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '转交成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'转交失败: {str(e)}'}), 500


@approval_api.route('/cancel/<int:instance_id>', methods=['POST'])
@login_required
def cancel_instance(instance_id):
    """
    取消审批实例(仅发起人或管理员)
    POST /api/approval/cancel/{instance_id}
    Body: {
        "reason": "取消原因"
    }
    """
    try:
        instance = ApprovalInstance.query.get_or_404(instance_id)
        
        # 权限验证
        if getattr(instance, 'requester_id', None) != current_user.id and not current_user.is_admin():
            return jsonify({'success': False, 'message': '只有发起人或管理员可以取消'}), 403
        
        if instance.status != 'pending':
            return jsonify({'success': False, 'message': '只能取消进行中的审批'}), 400
        
        data = request.get_json() or {}
        reason = data.get('reason', '')
        
        # 更新状态
        instance.status = 'cancelled'
        instance.completed_date = get_beijing_now()
        
        # 取消所有待审批步骤
        for step in instance.steps:
            if step.status == 'pending':
                step.status = 'cancelled'
        
        # 记录日志
        from app.approval_models import ApprovalLog
        log = ApprovalLog(
            instance_id=instance.id,
            action='cancel',
            operator_id=current_user.id,
            comment=reason,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '审批已取消'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'取消失败: {str(e)}'}), 500
