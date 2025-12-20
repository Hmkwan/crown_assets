"""
审批服务测试和辅助API路由
"""
from flask import jsonify, request
from flask_login import login_required, current_user
from app.admin.workflow_config_routes import admin_bp
from app.services import ApprovalService, ApprovalPermissionError
from app.models import User, WorkflowNode
from app.approval_roles import ApprovalRole


@admin_bp.route('/approval_service/check_permission', methods=['POST'])
@login_required
def check_approval_permission():
    """检查用户审批权限"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', current_user.id)
        order_type = data.get('order_type')
        amount = data.get('amount')
        
        if not order_type:
            return jsonify({'error': '缺少工单类型'}), 400
        
        has_permission, reason, valid_roles = ApprovalService.check_user_permission(
            user_id, order_type, amount
        )
        
        return jsonify({
            'success': True,
            'has_permission': has_permission,
            'reason': reason,
            'valid_roles': [
                {
                    'id': role.id,
                    'name': role.name,
                    'level': role.level,
                    'max_amount': role.max_approval_amount
                } for role in valid_roles
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/approval_service/find_approvers', methods=['POST'])
@login_required
def find_suitable_approvers():
    """智能查找合适的审批人"""
    try:
        data = request.get_json()
        order_type = data.get('order_type')
        amount = data.get('amount')
        department_id = data.get('department_id')
        exclude_user_ids = data.get('exclude_user_ids', [])
        
        if not order_type:
            return jsonify({'error': '缺少工单类型'}), 400
        
        approvers = ApprovalService.find_suitable_approvers(
            order_type,
            amount,
            department_id,
            exclude_user_ids
        )
        
        result = []
        for user, role, priority in approvers:
            result.append({
                'user_id': user.id,
                'username': user.username,
                'real_name': user.real_name,
                'department': user.get_department_name(),
                'role_id': role.id,
                'role_name': role.name,
                'role_level': role.level,
                'priority': priority
            })
        
        return jsonify({
            'success': True,
            'approvers': result,
            'count': len(result)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/approval_service/validate_action', methods=['POST'])
@login_required
def validate_approval_action():
    """验证用户是否可以执行审批操作"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', current_user.id)
        node_id = data.get('node_id')
        amount = data.get('amount')
        
        if not node_id:
            return jsonify({'error': '缺少节点ID'}), 400
        
        node = WorkflowNode.query.get(node_id)
        if not node:
            return jsonify({'error': '节点不存在'}), 404
        
        is_valid, reason = ApprovalService.validate_approval_action(
            user_id, node, amount
        )
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'reason': reason
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/approval_service/auto_assign/<int:node_id>', methods=['POST'])
@login_required
def auto_assign_node_approvers(node_id):
    """为节点自动分配审批人"""
    try:
        data = request.get_json()
        amount = data.get('amount')
        department_id = data.get('department_id')
        exclude_user_ids = data.get('exclude_user_ids', [])
        
        node = WorkflowNode.query.get(node_id)
        if not node:
            return jsonify({'error': '节点不存在'}), 404
        
        approver_ids = ApprovalService.auto_assign_approvers(
            node,
            amount,
            department_id,
            exclude_user_ids
        )
        
        # 获取用户信息
        users = User.query.filter(User.id.in_(approver_ids)).all()
        
        return jsonify({
            'success': True,
            'approver_ids': approver_ids,
            'approvers': [
                {
                    'id': u.id,
                    'username': u.username,
                    'real_name': u.real_name,
                    'department': u.get_department_name()
                } for u in users
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/approval_service/get_next_approvers', methods=['POST'])
@login_required
def get_next_workflow_approvers():
    """获取下一个审批节点和审批人"""
    try:
        data = request.get_json()
        order_type = data.get('order_type')
        current_sequence = data.get('current_sequence', 0)
        amount = data.get('amount')
        department_id = data.get('department_id')
        
        if not order_type:
            return jsonify({'error': '缺少工单类型'}), 400
        
        next_node, approver_ids = ApprovalService.get_next_approvers(
            order_type,
            current_sequence,
            amount,
            department_id
        )
        
        if not next_node:
            return jsonify({
                'success': True,
                'has_next': False,
                'message': '没有更多审批节点'
            })
        
        # 获取用户信息
        users = User.query.filter(User.id.in_(approver_ids)).all() if approver_ids else []
        
        return jsonify({
            'success': True,
            'has_next': True,
            'next_node': {
                'id': next_node.id,
                'name': next_node.name,
                'sequence': next_node.sequence,
                'node_type': next_node.node_type,
                'is_parallel': next_node.is_parallel,
                'required_approvals': next_node.required_approvals
            },
            'approver_ids': approver_ids,
            'approvers': [
                {
                    'id': u.id,
                    'username': u.username,
                    'real_name': u.real_name,
                    'department': u.get_department_name()
                } for u in users
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/approval_service/user_roles/<int:user_id>')
@login_required
def get_user_approval_roles_info(user_id):
    """获取用户的所有审批角色信息"""
    try:
        roles = ApprovalService.get_user_approval_roles(user_id)
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'real_name': user.real_name,
                'department': user.get_department_name()
            },
            'roles': [
                {
                    'id': role.id,
                    'code': role.code,
                    'name': role.name,
                    'level': role.level,
                    'max_approval_amount': role.max_approval_amount,
                    'permissions': {
                        'repair': role.can_approve_repair,
                        'part_request': role.can_approve_part_request,
                        'transfer': role.can_approve_equipment_transfer,
                        'scrap': role.can_approve_equipment_scrap,
                        'loan': role.can_approve_equipment_loan,
                        'application': role.can_approve_equipment_application
                    }
                } for role in roles
            ],
            'count': len(roles)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
