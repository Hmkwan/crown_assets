"""
审批流引擎 API 路由
提供流程模板管理、审批操作、流程状态查询等接口
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db, get_beijing_now
from app.approval_models import WorkflowTemplate, WorkflowNode
from app.models import ApprovalWorkflow, User, Notification, UserActivityLog
from app.workflow_models_new import WorkflowInstance, ApprovalDecision, ActionLog
import json

workflow_bp = Blueprint('workflow', __name__, url_prefix='/api/v1/workflow')


# ==================== 模板管理 ====================

@workflow_bp.route('/templates', methods=['GET'])
@login_required
def list_templates():
    """获取所有可用的流程模板"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    templates = WorkflowTemplate.query.filter_by(is_active=True).all()
    result = []
    for tmpl in templates:
        result.append({
            'id': tmpl.id,
            'name': tmpl.name,
            'order_type': tmpl.order_type,
            'description': tmpl.description,
            'node_count': len(tmpl.nodes)
        })
    
    return jsonify({'success': True, 'templates': result})


@workflow_bp.route('/templates/<int:template_id>', methods=['GET'])
@login_required
def get_template(template_id):
    """获取模板详情及节点配置"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    template = WorkflowTemplate.query.get_or_404(template_id)
    nodes = WorkflowNode.query.filter_by(template_id=template_id, is_active=True).order_by(WorkflowNode.sequence).all()
    
    return jsonify({
        'success': True,
        'template': {
            'id': template.id,
            'name': template.name,
            'order_type': template.order_type,
            'description': template.description
        },
        'nodes': [{
            'id': n.id,
            'name': n.name,
            'node_type': n.node_type,
            'sequence': n.sequence,
            'is_parallel': n.is_parallel,
            'role_required': n.role_required,
            'approver_user_id': n.approver_user_id,
            'required_approvals': n.required_approvals,
            'timeout_seconds': n.timeout_seconds
        } for n in nodes]
    })


@workflow_bp.route('/templates', methods=['POST'])
@login_required
def create_template():
    """创建新流程模板"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    data = request.get_json()
    if not data or not data.get('name') or not data.get('order_type'):
        return jsonify({'success': False, 'message': '缺少必填字段'}), 400
    
    template = WorkflowTemplate(
        name=data['name'],
        order_type=data['order_type'],
        description=data.get('description', ''),
        created_by=current_user.id
    )
    db.session.add(template)
    db.session.flush()
    
    # 创建节点
    if 'nodes' in data:
        for node_data in data['nodes']:
            node = WorkflowNode(
                template_id=template.id,
                name=node_data.get('name', ''),
                node_type=node_data.get('node_type', 'approval'),
                sequence=node_data.get('sequence', 0),
                is_parallel=node_data.get('is_parallel', False),
                role_required=node_data.get('role_required'),
                approver_user_id=node_data.get('approver_user_id'),
                approver_user_ids=json.dumps(node_data.get('approver_user_ids', [])) if node_data.get('approver_user_ids') else None,
                required_approvals=node_data.get('required_approvals', 1),
                timeout_seconds=node_data.get('timeout_seconds')
            )
            db.session.add(node)
    
    db.session.commit()
    
    return jsonify({'success': True, 'template_id': template.id, 'message': '模板创建成功'}), 201


# ==================== 审批操作 ====================

@workflow_bp.route('/approvals', methods=['GET'])
@login_required
def list_my_approvals():
    """获取当前用户待审批列表"""
    status = request.args.get('status', 'pending')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = ApprovalWorkflow.query.filter_by(approver_id=current_user.id)
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    pagination = query.order_by(ApprovalWorkflow.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    result = []
    for approval in pagination.items:
        # 获取关联订单信息（根据 order_type 动态查询）
        order_info = _get_order_summary(approval.order_type, approval.order_id)
        
        result.append({
            'id': approval.id,
            'order_type': approval.order_type,
            'order_id': approval.order_id,
            'order_summary': order_info,
            'status': approval.status,
            'approval_level': approval.approval_level,
            'created_at': approval.created_at.isoformat() if approval.created_at else None,
            'node_id': approval.node_id
        })
    
    return jsonify({
        'success': True,
        'approvals': result,
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })


@workflow_bp.route('/approvals/<int:approval_id>/act', methods=['POST'])
@login_required
def approve_or_reject(approval_id):
    """执行审批操作（同意/拒绝/转交）"""
    data = request.get_json()
    action = data.get('action')  # approve/reject/reassign
    
    if action not in ['approve', 'reject', 'reassign']:
        return jsonify({'success': False, 'message': '无效操作'}), 400
    
    approval = ApprovalWorkflow.query.get_or_404(approval_id)
    
    # 权限检查
    if approval.approver_id != current_user.id:
        return jsonify({'success': False, 'message': '您无权操作此审批'}), 403
    
    if approval.status != 'pending':
        return jsonify({'success': False, 'message': '该审批已处理'}), 409
    
    if action == 'reassign':
        # 转交给其他审批人
        to_user_id = data.get('to_user_id')
        if not to_user_id:
            return jsonify({'success': False, 'message': '缺少目标审批人'}), 400
        
        approval.approver_id = to_user_id
        db.session.commit()
        
        # 通知新审批人
        _send_notification(to_user_id, f'审批转交', f'用户 {current_user.username} 将审批 #{approval.id} 转交给您')
        
        return jsonify({'success': True, 'message': '转交成功'})
    
    # 审批/拒绝
    approval.status = 'approved' if action == 'approve' else 'rejected'
    approval.acted_at = get_beijing_now()
    approval.comments = data.get('comments', '')
    
    # 记录决策（支持并行审批）
    decision = ApprovalDecision(
        approval_workflow_id=approval.id,
        approver_id=current_user.id,
        decision=action,
        comments=data.get('comments', '')
    )
    db.session.add(decision)
    
    # 更新流程状态
    instance = WorkflowInstance.query.filter_by(
        order_type=approval.order_type,
        order_id=approval.order_id
    ).first()
    
    if action == 'approve':
        # 查找下一个节点
        next_node = _get_next_node(approval.node_id)
        if next_node:
            # 创建下一个审批
            next_approval = ApprovalWorkflow(
                order_type=approval.order_type,
                order_id=approval.order_id,
                node_id=next_node.id,
                approver_id=_assign_approver(next_node, approval.order_type, approval.order_id),
                approval_level=next_node.role_required,
                status='pending'
            )
            db.session.add(next_approval)
            
            if instance:
                instance.current_node_id = next_node.id
        else:
            # 流程完成
            if instance:
                instance.status = 'approved'
                instance.finished_at = get_beijing_now()
            
            # 触发完成动作
            _execute_actions(approval, 'approve')
    else:
        # 拒绝
        if instance:
            instance.status = 'rejected'
            instance.finished_at = get_beijing_now()
        
        _execute_actions(approval, 'reject')
    
    db.session.commit()
    
    # 记录活动日志
    _log_activity('审批操作', f'用户 {current_user.username} {action} 了审批 #{approval.id}')
    
    return jsonify({
        'success': True,
        'message': '操作成功',
        'workflow_status': instance.status if instance else None
    })


# ==================== 流程状态查询 ====================

@workflow_bp.route('/workflows/<order_type>/<int:order_id>', methods=['GET'])
@login_required
def get_workflow_status(order_type, order_id):
    """查询流程状态与历史"""
    instance = WorkflowInstance.query.filter_by(
        order_type=order_type,
        order_id=order_id
    ).first_or_404()
    
    approvals = ApprovalWorkflow.query.filter_by(
        order_type=order_type,
        order_id=order_id
    ).order_by(ApprovalWorkflow.created_at).all()
    
    history = []
    for appr in approvals:
        approver = User.query.get(appr.approver_id) if appr.approver_id else None
        history.append({
            'id': appr.id,
            'approver': approver.username if approver else None,
            'status': appr.status,
            'comments': appr.comments,
            'created_at': appr.created_at.isoformat() if appr.created_at else None,
            'acted_at': appr.acted_at.isoformat() if appr.acted_at else None
        })
    
    return jsonify({
        'success': True,
        'instance': {
            'status': instance.status,
            'started_at': instance.started_at.isoformat() if instance.started_at else None,
            'finished_at': instance.finished_at.isoformat() if instance.finished_at else None
        },
        'history': history
    })


# ==================== 辅助函数 ====================

def _get_order_summary(order_type, order_id):
    """根据订单类型获取订单摘要"""
    from app.models import RepairOrder, PartRequestOrder, EquipmentApplication
    
    if order_type == 'repair_order':
        order = RepairOrder.query.get(order_id)
        return f'维修工单 #{order_id}' if order else None
    elif order_type == 'part_request_order':
        order = PartRequestOrder.query.get(order_id)
        return f'配件申请 #{order_id} - {order.part_name}' if order else None
    elif order_type == 'equipment_application':
        order = EquipmentApplication.query.get(order_id)
        return f'设备申请 #{order_id}' if order else None
    
    return f'{order_type} #{order_id}'


def _get_next_node(current_node_id):
    """获取下一个节点"""
    current = WorkflowNode.query.get(current_node_id)
    if not current:
        return None
    
    return WorkflowNode.query.filter_by(
        template_id=current.template_id,
        is_active=True
    ).filter(WorkflowNode.sequence > current.sequence).order_by(WorkflowNode.sequence).first()


def _assign_approver(node, order_type, order_id):
    """根据节点配置分配审批人"""
    if node.approver_user_id:
        return node.approver_user_id
    
    if node.role_required:
        # 根据角色查找审批人（简化版，实际需根据部门等动态筛选）
        approver = User.query.filter_by(role=node.role_required, is_active=True).first()
        return approver.id if approver else None
    
    return None


def _execute_actions(approval, action_type):
    """执行节点配置的动作"""
    node = WorkflowNode.query.get(approval.node_id)
    if not node:
        return
    
    actions_json = node.actions_on_approve if action_type == 'approve' else node.actions_on_reject
    if not actions_json:
        return
    
    try:
        actions = json.loads(actions_json)
        for action in actions:
            action_log = ActionLog(
                action_name=action.get('name', 'unknown'),
                workflow_node_id=node.id,
                approval_workflow_id=approval.id,
                payload=json.dumps(action),
                status='pending'
            )
            db.session.add(action_log)
            # TODO: 将动作加入队列异步执行
    except Exception:
        pass


def _send_notification(user_id, title, message):
    """发送通知"""
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message
    )
    db.session.add(notif)


def _log_activity(action, description):
    """记录活动日志"""
    log = UserActivityLog(
        user_id=current_user.id,
        action=action,
        description=description
    )
    db.session.add(log)


# ==================== 节点管理 ====================

@workflow_bp.route('/nodes', methods=['POST'])
@login_required
def add_node():
    """添加审批节点"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    data = request.get_json()
    
    try:
        # 解析审批人ID列表
        approver_ids = data.get('approver_user_ids', '')
        if approver_ids:
            approver_ids = approver_ids.strip()
        
        # 创建新节点
        node = WorkflowNode(
            name=data.get('name'),
            order_type=data.get('order_type'),
            role_required=data.get('role_required'),
            sequence=int(data.get('sequence', 1)),
            node_type=data.get('node_type', 'approval'),
            approver_user_ids=approver_ids if approver_ids else None,
            condition_expr=data.get('condition_expr'),
            is_active=True
        )
        
        db.session.add(node)
        db.session.commit()
        
        order_type = node.template.order_type if node.template else 'unknown'
        _log_activity('添加审批节点', f'工单类型: {order_type}, 节点: {node.name}')
        
        return jsonify({'success': True, 'message': '节点添加成功', 'node_id': node.id})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500


@workflow_bp.route('/nodes', methods=['PUT'])
@login_required
def update_node():
    """更新审批节点"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    data = request.get_json()
    node_id = data.get('id')
    
    if not node_id:
        return jsonify({'success': False, 'message': '缺少节点ID'}), 400
    
    try:
        node = WorkflowNode.query.get_or_404(node_id)
        
        # 更新字段
        if 'name' in data:
            node.name = data['name']
        if 'role_required' in data:
            node.role_required = data['role_required']
        if 'sequence' in data:
            node.sequence = int(data['sequence'])
        if 'node_type' in data:
            node.node_type = data['node_type']
        if 'condition_expr' in data:
            node.condition_expr = data['condition_expr']
        if 'approver_user_ids' in data:
            approver_ids = data['approver_user_ids'].strip() if data['approver_user_ids'] else None
            node.approver_user_ids = approver_ids
        
        db.session.commit()
        
        _log_activity('更新审批节点', f'节点ID: {node.id}, 名称: {node.name}')
        
        return jsonify({'success': True, 'message': '节点更新成功'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@workflow_bp.route('/nodes', methods=['DELETE'])
@login_required
def delete_node():
    """删除审批节点"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    data = request.get_json()
    node_id = data.get('id')
    
    if not node_id:
        return jsonify({'success': False, 'message': '缺少节点ID'}), 400
    
    try:
        node = WorkflowNode.query.get_or_404(node_id)
        node_name = node.name
        
        # 软删除（标记为不活动）
        node.is_active = False
        db.session.commit()
        
        _log_activity('删除审批节点', f'节点ID: {node_id}, 名称: {node_name}')
        
        return jsonify({'success': True, 'message': '节点删除成功'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

