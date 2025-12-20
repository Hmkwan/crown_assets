"""
审批流程配置管理路由
管理员可以自定义流程节点的金额阈值和跳过规则
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.approval_models import WorkflowNode, WorkflowTemplate
from app import db
from app.decorators import admin_required
from decimal import Decimal

# 创建admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/workflow_config')
@login_required
@admin_required
def workflow_config():
    """审批流程配置管理页面"""
    from app.models import User
    from app.approval_roles import ApprovalRole
    
    # 获取所有工单类型
    order_types = [
        {'value': 'repair_order', 'label': '维修工单'},
        {'value': 'part_request_order', 'label': '配件申请'},
        {'value': 'equipment_transfer', 'label': '设备调拨'},
        {'value': 'equipment_scrap', 'label': '设备报废'},
        {'value': 'equipment_loan', 'label': '设备借用'},
        {'value': 'equipment_application', 'label': '设备申请'}
    ]
    
    # 获取选中的工单类型
    selected_type = request.args.get('order_type', 'repair_order')
    
    # 查询该类型的所有节点(通过join WorkflowTemplate)
    nodes = WorkflowNode.query.join(WorkflowTemplate).filter(
        WorkflowTemplate.order_type == selected_type,
        WorkflowNode.is_active == True
    ).order_by(WorkflowNode.sequence).all()
    
    # 查询模板信息
    template = WorkflowTemplate.query.filter_by(
        order_type=selected_type,
        is_active=True
    ).first()
    
    # 获取所有用户（用于指定审批人）
    users = User.query.filter_by(is_active=True).order_by(User.department_id, User.username).all()
    
    # 获取所有审批角色
    approval_roles = ApprovalRole.query.filter_by(is_active=True).order_by(ApprovalRole.level.desc()).all()
    
    return render_template('admin/workflow_config.html',
                         order_types=order_types,
                         selected_type=selected_type,
                         nodes=nodes,
                         template=template,
                         users=users,
                         approval_roles=approval_roles)


@admin_bp.route('/workflow_config/get_node/<int:node_id>')
@login_required
@admin_required
def get_workflow_node(node_id):
    """获取流程节点详细信息"""
    try:
        node = WorkflowNode.query.get_or_404(node_id)
        
        # 解析审批人ID列表
        approver_ids = []
        if node.approver_user_ids:
            import json
            try:
                approver_ids = json.loads(node.approver_user_ids)
            except:
                pass
        
        return jsonify({
            'success': True,
            'node': {
                'id': node.id,
                'name': node.name,
                'sequence': node.sequence,
                'role_required': node.role_required,
                'approval_role_id': node.approval_role_id,
                'node_type': node.node_type or 'approval',
                'amount_threshold': float(node.amount_threshold) if node.amount_threshold else None,
                'skip_if_below_threshold': node.skip_if_below_threshold,
                'is_parallel': node.is_parallel or False,
                'required_approvals': node.required_approvals or 1,
                'approver_user_ids': approver_ids
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取失败: {str(e)}'
        }), 500


@admin_bp.route('/workflow_config/update_node/<int:node_id>', methods=['POST'])
@login_required
@admin_required
def update_workflow_node(node_id):
    """更新流程节点配置"""
    try:
        node = WorkflowNode.query.get_or_404(node_id)
        
        # 获取提交的数据
        data = request.get_json()
        
        # 更新金额阈值
        if 'amount_threshold' in data:
            threshold = data['amount_threshold']
            if threshold is None or threshold == '':
                node.amount_threshold = None
            else:
                try:
                    node.amount_threshold = float(threshold)
                except (ValueError, TypeError):
                    return jsonify({
                        'success': False,
                        'message': '金额格式不正确'
                    }), 400
        
        # 更新跳过规则
        if 'skip_if_below_threshold' in data:
            node.skip_if_below_threshold = bool(data['skip_if_below_threshold'])
        
        # 更新节点名称
        if 'name' in data and data['name']:
            node.name = data['name']
        
        # 更新所需角色(兼容旧版)
        if 'role_required' in data and data['role_required']:
            node.role_required = data['role_required']
        
        # 更新审批角色ID(新版)
        if 'approval_role_id' in data:
            role_id = data['approval_role_id']
            if role_id:
                try:
                    node.approval_role_id = int(role_id)
                except (ValueError, TypeError):
                    return jsonify({
                        'success': False,
                        'message': '审批角色ID格式不正确'
                    }), 400
            else:
                node.approval_role_id = None
        
        # 更新序号
        if 'sequence' in data:
            try:
                node.sequence = int(data['sequence'])
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': '序号必须是数字'
                }), 400
        
        # 更新节点类型
        if 'node_type' in data:
            node.node_type = data['node_type']
        
        # 更新并行审批设置
        if 'is_parallel' in data:
            node.is_parallel = bool(data['is_parallel'])
        
        if 'required_approvals' in data:
            try:
                node.required_approvals = int(data['required_approvals'])
            except (ValueError, TypeError):
                node.required_approvals = 1
        
        # 更新指定审批人
        if 'approver_user_ids' in data:
            node.approver_user_ids = data['approver_user_ids']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '流程节点已更新',
            'node': {
                'id': node.id,
                'name': node.name,
                'sequence': node.sequence,
                'role_required': node.role_required,
                'node_type': node.node_type,
                'amount_threshold': float(node.amount_threshold) if node.amount_threshold else None,
                'skip_if_below_threshold': node.skip_if_below_threshold,
                'is_parallel': node.is_parallel,
                'required_approvals': node.required_approvals
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新失败: {str(e)}'
        }), 500


@admin_bp.route('/workflow_config/delete_node/<int:node_id>', methods=['POST'])
@login_required
@admin_required
def delete_workflow_node(node_id):
    """删除流程节点（软删除）"""
    try:
        node = WorkflowNode.query.get_or_404(node_id)
        
        # 软删除：设置为不活跃
        node.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'已删除节点: {node.name}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'删除失败: {str(e)}'
        }), 500


@admin_bp.route('/workflow_config/add_node', methods=['POST'])
@login_required
@admin_required
def add_workflow_node():
    """添加新的流程节点"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['order_type', 'name', 'sequence']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'缺少必填字段: {field}'
                }), 400
        
        # 审批角色ID(新版)或role_required(旧版兼容)至少要有一个
        approval_role_id = data.get('approval_role_id')
        role_required = data.get('role_required')
        
        if not approval_role_id and not role_required:
            return jsonify({
                'success': False,
                'message': '必须指定审批角色'
            }), 400
        
        # 创建新节点
        node = WorkflowNode(
            order_type=data['order_type'],
            name=data['name'],
            role_required=role_required if role_required else '',
            approval_role_id=int(approval_role_id) if approval_role_id else None,
            sequence=int(data['sequence']),
            node_type=data.get('node_type', 'approval'),
            is_active=True,
            is_parallel=data.get('is_parallel', False),
            required_approvals=data.get('required_approvals', 1)
        )
        
        # 设置金额阈值（可选）
        if 'amount_threshold' in data and data['amount_threshold']:
            try:
                node.amount_threshold = float(data['amount_threshold'])
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': '金额格式不正确'
                }), 400
        
        # 设置跳过规则（可选）
        if 'skip_if_below_threshold' in data:
            node.skip_if_below_threshold = bool(data['skip_if_below_threshold'])
        
        # 设置指定审批人（可选）
        if 'approver_user_ids' in data:
            node.approver_user_ids = data['approver_user_ids']
        
        # 查找或创建模板关联
        template = WorkflowTemplate.query.filter_by(
            order_type=data['order_type'],
            is_active=True
        ).first()
        
        if template:
            node.template_id = template.id
        
        db.session.add(node)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '流程节点已添加',
            'node': {
                'id': node.id,
                'name': node.name,
                'sequence': node.sequence,
                'role_required': node.role_required,
                'node_type': node.node_type,
                'amount_threshold': float(node.amount_threshold) if node.amount_threshold else None,
                'skip_if_below_threshold': node.skip_if_below_threshold,
                'is_parallel': node.is_parallel,
                'required_approvals': node.required_approvals
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'添加失败: {str(e)}'
        }), 500


@admin_bp.route('/workflow_config/reorder_nodes', methods=['POST'])
@login_required
@admin_required
def reorder_workflow_nodes():
    """重新排序流程节点"""
    try:
        data = request.get_json()
        node_orders = data.get('node_orders', [])  # [{id: 1, sequence: 1}, {id: 2, sequence: 2}, ...]
        
        for item in node_orders:
            node = WorkflowNode.query.get(item['id'])
            if node:
                node.sequence = item['sequence']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '节点顺序已更新'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'排序失败: {str(e)}'
        }), 500


# 导入审批管理路由,让它们注册到同一个 admin_bp
from app.admin import approval_management_routes
