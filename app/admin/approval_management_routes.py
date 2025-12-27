"""
管理员审批流程管理路由
管理员可以查看所有审批流程,并进行干预操作
"""
from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timezone
from app.admin.workflow_config_routes import admin_bp
from app.models import (
    ApprovalWorkflow, WorkflowNode, WorkflowTemplate, RepairOrder, PartRequestOrder,
    EquipmentTransfer, EquipmentScrap, EquipmentLoan, EquipmentApplication,
    User, db
)
from app.decorators import admin_required

# 避免循环导入,直接定义时间函数
def get_beijing_now():
    """获取当前北京时间（Asia/Shanghai）"""
    try:
        import pytz
        tz = pytz.timezone('Asia/Shanghai')
        return datetime.now(tz).replace(tzinfo=None)
    except:
        from datetime import timedelta
        return datetime.now(timezone.utc) + timedelta(hours=8)


@admin_bp.route('/approval_flows')
@login_required
@admin_required
def approval_flows():
    """管理员查看所有审批流程模板"""
    # 获取所有流程模板
    templates = WorkflowTemplate.query.order_by(
        WorkflowTemplate.order_type,
        WorkflowTemplate.version.desc()
    ).all()
    
    # 按工单类型分组
    templates_by_type = {}
    for template in templates:
        if template.order_type not in templates_by_type:
            templates_by_type[template.order_type] = []
        templates_by_type[template.order_type].append(template)
    
    # 统计每个模板的节点数
    for template in templates:
        template.node_count = WorkflowNode.query.filter_by(template_id=template.id).count()
    
    return render_template('admin/approval_flows.html',
                         templates=templates,
                         templates_by_type=templates_by_type)


@admin_bp.route('/approval_flow/<int:approval_id>')
@login_required
@admin_required
def approval_flow_detail(approval_id):
    """查看审批流程详情"""
    approval = ApprovalWorkflow.query.get_or_404(approval_id)
    
    # 获取工单信息
    order_info = _get_order_info(approval.order_type, approval.order_id)
    
    # 获取该工单的所有审批节点
    all_approvals = ApprovalWorkflow.query.filter_by(
        order_type=approval.order_type,
        order_id=approval.order_id
    ).order_by(ApprovalWorkflow.created_date).all()
    
    # 获取该工单类型的所有流程节点（通过join WorkflowTemplate）
    workflow_nodes = WorkflowNode.query.join(WorkflowTemplate).filter(
        WorkflowTemplate.order_type == approval.order_type,
        WorkflowNode.is_active == True
    ).order_by(WorkflowNode.sequence).all()
    
    # 获取当前节点可选的审批人
    eligible_users = []
    if approval.workflow_node and approval.workflow_node.approval_role_id:
        # 根据审批角色获取有资格的用户
        from app.approval_roles import UserApprovalRole
        role_assignments = UserApprovalRole.query.filter_by(
            role_id=approval.workflow_node.approval_role_id,
            is_active=True
        ).all()
        eligible_users = [assignment.user for assignment in role_assignments if assignment.user and assignment.user.is_active]
        
        # 如果该角色没有分配任何用户，fallback到所有活跃用户
        if not eligible_users:
            eligible_users = User.query.filter_by(is_active=True).all()
    else:
        # 如果没有设置审批角色,获取所有活跃用户
        eligible_users = User.query.filter_by(is_active=True).all()
    
    return render_template('admin/approval_flow_detail.html',
                         approval=approval,
                         order_info=order_info,
                         all_approvals=all_approvals,
                         workflow_nodes=workflow_nodes,
                         users=eligible_users)


@admin_bp.route('/approval_flow/<int:approval_id>/jump_to_node', methods=['POST'])
@login_required
@admin_required
def jump_to_node(approval_id):
    """打回到指定节点"""
    try:
        approval = ApprovalWorkflow.query.get_or_404(approval_id)
        target_node_id = request.json.get('node_id')
        reason = request.json.get('reason', '')
        
        if not target_node_id:
            return jsonify({'success': False, 'message': '请选择目标节点'}), 400
        
        target_node = WorkflowNode.query.get(target_node_id)
        if not target_node:
            return jsonify({'success': False, 'message': '目标节点不存在'}), 404
        
        # 验证目标节点是否属于同一工单类型
        target_order_type = target_node.order_type if target_node.template else None
        if target_order_type != approval.order_type:
            return jsonify({'success': False, 'message': '目标节点类型不匹配'}), 400
        
        # 终止当前审批
        approval.status = 'terminated'
        approval.comments = f'管理员操作: 打回到{target_node.name}. 原因: {reason}'
        approval.admin_action = 'jump_to_node'
        approval.admin_operator_id = current_user.id
        approval.approved_date = get_beijing_now()
        
        # 创建新的审批节点
        from app.main.routes import get_approver_id
        new_approver_id = get_approver_id(target_node, '')
        
        new_approval = ApprovalWorkflow(
            order_type=approval.order_type,
            order_id=approval.order_id,
            approver_id=new_approver_id,
            node_id=target_node.id,
            status='pending',
            comments=f'管理员打回: {reason}'
        )
        
        db.session.add(new_approval)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'已打回到节点: {target_node.name}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/approval_flow/<int:approval_id>/skip_node', methods=['POST'])
@login_required
@admin_required
def skip_node(approval_id):
    """跳过当前节点,进入下一个节点"""
    try:
        approval = ApprovalWorkflow.query.get_or_404(approval_id)
        reason = request.json.get('reason', '')
        
        if approval.status != 'pending':
            return jsonify({'success': False, 'message': '只能跳过待审批的节点'}), 400
        
        # 标记当前节点为跳过
        approval.status = 'approved'
        approval.comments = f'管理员操作: 跳过此节点. 原因: {reason}'
        approval.admin_action = 'skip'
        approval.admin_operator_id = current_user.id
        approval.approved_date = get_beijing_now()
        
        # 查找下一个节点
        from app.main.routes import get_next_approval_node, get_approver_id
        next_node = get_next_approval_node(approval.order_type, approval.order_id)
        
        if next_node:
            # 创建下一个审批节点
            next_approver_id = get_approver_id(next_node, '')
            next_approval = ApprovalWorkflow(
                order_type=approval.order_type,
                order_id=approval.order_id,
                approver_id=next_approver_id,
                node_id=next_node.id,
                status='pending',
                comments='上一节点被管理员跳过'
            )
            db.session.add(next_approval)
            message = f'已跳过当前节点,进入下一节点: {next_node.name}'
        else:
            # 没有下一节点,完成审批
            _complete_order(approval.order_type, approval.order_id)
            message = '已跳过当前节点,审批流程已完成'
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': message})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/approval_flow/<int:approval_id>/reassign', methods=['POST'])
@login_required
@admin_required
def reassign_approver(approval_id):
    """重新分配审批人"""
    try:
        approval = ApprovalWorkflow.query.get_or_404(approval_id)
        new_approver_id = request.json.get('approver_id')
        reason = request.json.get('reason', '')
        
        if not new_approver_id:
            return jsonify({'success': False, 'message': '请选择新的审批人'}), 400
        
        new_approver = User.query.get(new_approver_id)
        if not new_approver:
            return jsonify({'success': False, 'message': '审批人不存在'}), 404
        
        old_approver = approval.approver
        old_name = old_approver.username if old_approver else '未分配'
        new_name = new_approver.username
        
        approval.transferred_from_id = approval.approver_id
        approval.approver_id = new_approver_id
        approval.comments = f'管理员重新分配: {old_name} → {new_name}. 原因: {reason}'
        approval.admin_action = 'reassign'
        approval.admin_operator_id = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'已重新分配给: {new_approver.username}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


def _get_order_info(order_type, order_id):
    """获取工单信息"""
    order_models = {
        'repair_order': RepairOrder,
        'part_request_order': PartRequestOrder,
        'equipment_transfer': EquipmentTransfer,
        'equipment_scrap': EquipmentScrap,
        'equipment_loan': EquipmentLoan,
        'equipment_application': EquipmentApplication
    }
    
    model = order_models.get(order_type)
    if model:
        order = model.query.get(order_id)
        if order:
            return {
                'id': order.id,
                'type': order_type,
                'status': getattr(order, 'status', 'unknown'),
                'requester': getattr(order, 'requester', None) or getattr(order, 'applicant', None),
                'created_date': getattr(order, 'created_date', None),
                'description': getattr(order, 'description', '') or getattr(order, 'reason', ''),
                'equipment': getattr(order, 'equipment', None)
            }
    return None


def _complete_order(order_type, order_id):
    """完成工单"""
    order_models = {
        'repair_order': RepairOrder,
        'part_request_order': PartRequestOrder,
        'equipment_transfer': EquipmentTransfer,
        'equipment_scrap': EquipmentScrap,
        'equipment_loan': EquipmentLoan,
        'equipment_application': EquipmentApplication
    }
    
    model = order_models.get(order_type)
    if model:
        order = model.query.get(order_id)
        if order:
            order.status = 'approved'
            if hasattr(order, 'approved_date'):
                order.approved_date = get_beijing_now()
            if hasattr(order, 'completed_date'):
                order.completed_date = get_beijing_now()


@admin_bp.route('/workflow_template/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_approval_workflow_template():
    """创建流程模板"""
    if request.method == 'POST':
        try:
            data = request.json
            template = WorkflowTemplate(
                code=data['code'],
                name=data['name'],
                order_type=data['order_type'],
                version=data.get('version', 1),
                is_active=data.get('is_active', True),
                is_default=data.get('is_default', False),
                description=data.get('description', ''),
                created_by_id=current_user.id
            )
            db.session.add(template)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '流程模板创建成功',
                'template_id': template.id
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500
    
    return render_template('admin/create_workflow_template.html')


@admin_bp.route('/workflow_template/<int:template_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_approval_workflow_template(template_id):
    """编辑流程模板"""
    template = WorkflowTemplate.query.get_or_404(template_id)
    
    if request.method == 'POST':
        try:
            data = request.json
            template.name = data.get('name', template.name)
            template.is_active = data.get('is_active', template.is_active)
            template.is_default = data.get('is_default', template.is_default)
            template.description = data.get('description', template.description)
            template.updated_date = get_beijing_now()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '流程模板更新成功'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500
    
    nodes = WorkflowNode.query.filter_by(template_id=template_id).order_by(WorkflowNode.sequence).all()
    from app.approval_roles import ApprovalRole
    roles = ApprovalRole.query.filter_by(is_active=True).all()
    return render_template('admin/edit_workflow_template.html', template=template, nodes=nodes, roles=roles)


@admin_bp.route('/workflow_template/<int:template_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_approval_workflow_template(template_id):
    """删除流程模板"""
    try:
        template = WorkflowTemplate.query.get_or_404(template_id)
        
        # 检查是否有正在使用的审批实例
        from app.approval_models import ApprovalInstance
        active_instances = ApprovalInstance.query.filter_by(
            template_id=template_id
        ).filter(
            ApprovalInstance.status.in_(['pending', 'in_progress'])
        ).count()
        
        if active_instances > 0:
            return jsonify({
                'success': False,
                'message': f'该模板有 {active_instances} 个正在进行的审批，无法删除'
            }), 400
        
        # 删除关联的节点（cascade会自动删除）
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '流程模板已删除'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/workflow_node/create', methods=['POST'])
@login_required
@admin_required
def create_approval_workflow_node():
    """创建流程节点"""
    try:
        data = request.json
        from app.approval_roles import ApprovalRole
        
        # 获取审批角色
        role = None
        if data.get('role_id'):
            role = ApprovalRole.query.get(data['role_id'])
        
        node = WorkflowNode(
            template_id=data['template_id'],
            code=data.get('code', ''),
            name=data['name'],
            sequence=data.get('sequence', 1),
            node_type=data.get('node_type', 'approval'),
            approval_role_id=role.id if role else None,
            is_active=data.get('is_active', True)
        )
        
        db.session.add(node)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '节点创建成功',
            'node_id': node.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/workflow_node/<int:node_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_approval_workflow_node(node_id):
    """编辑流程节点"""
    try:
        node = WorkflowNode.query.get_or_404(node_id)
        data = request.json
        
        from app.approval_roles import ApprovalRole
        
        node.name = data.get('name', node.name)
        node.sequence = data.get('sequence', node.sequence)
        node.is_active = data.get('is_active', node.is_active)
        
        if 'role_id' in data:
            node.approval_role_id = data['role_id']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '节点更新成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/workflow_node/<int:node_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_template_workflow_node(node_id):
    """删除流程节点"""
    try:
        node = WorkflowNode.query.get_or_404(node_id)
        db.session.delete(node)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '节点已删除'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/init_default_workflows', methods=['POST'])
@login_required
@admin_required
def init_default_workflows():
    """初始化默认审批流程"""
    try:
        from app.approval_roles import ApprovalRole
        
        # 工单类型定义
        order_types = [
            {'code': 'repair_order', 'name': '维修工单'},
            {'code': 'part_request_order', 'name': '配件申请'},
            {'code': 'equipment_transfer', 'name': '设备调拨'},
            {'code': 'equipment_scrap', 'name': '设备报废'},
            {'code': 'equipment_loan', 'name': '设备借用'},
            {'code': 'equipment_application', 'name': '设备申请'}
        ]
        
        created_count = 0
        
        for ot in order_types:
            # 检查是否已存在
            existing = WorkflowTemplate.query.filter_by(
                order_type=ot['code'],
                is_default=True
            ).first()
            
            if not existing:
                # 创建模板
                template = WorkflowTemplate(
                    code=f"{ot['code']}_std_v1",
                    name=f"{ot['name']}标准流程",
                    order_type=ot['code'],
                    version=1,
                    is_active=True,
                    is_default=True,
                    description=f"{ot['name']}的标准审批流程",
                    created_by_id=current_user.id
                )
                db.session.add(template)
                db.session.flush()
                
                # 创建基本节点
                # 1. 部门主管审批
                dept_role = ApprovalRole.query.filter_by(name='department_head').first()
                if dept_role:
                    node1 = WorkflowNode(
                        template_id=template.id,
                        code='dept_approve',
                        name='部门主管审批',
                        sequence=1,
                        node_type='approval',
                        approval_role_id=dept_role.id,
                        is_active=True
                    )
                    db.session.add(node1)
                
                # 2. 管理员审批
                admin_role = ApprovalRole.query.filter_by(name='admin').first()
                if admin_role:
                    node2 = WorkflowNode(
                        template_id=template.id,
                        code='admin_approve',
                        name='管理员审批',
                        sequence=2,
                        node_type='approval',
                        approval_role_id=admin_role.id,
                        is_active=True
                    )
                    db.session.add(node2)
                
                created_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功初始化 {created_count} 个默认流程模板'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

