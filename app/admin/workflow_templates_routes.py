"""
工作流模板管理路由
提供模板的查看、编辑、克隆、激活/停用、应用等功能
"""

from flask import jsonify, request, render_template
from app.admin.workflow_config_routes import admin_bp
from app.models import db, WorkflowTemplate, WorkflowNode, ApprovalRole
from flask_login import login_required, current_user
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'success': False, 'message': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ==================== 模板管理页面 ====================

@admin_bp.route('/workflow_templates')
@admin_required
def workflow_templates():
    """工作流模板管理页面"""
    return render_template('admin/workflow_templates.html')


# ==================== 模板CRUD API ====================

@admin_bp.route('/api/workflow_templates/list', methods=['GET'])
@admin_required
def list_workflow_templates():
    """获取所有工作流模板列表"""
    try:
        order_type = request.args.get('order_type')  # 可选:按工单类型筛选
        
        query = WorkflowTemplate.query
        if order_type:
            query = query.filter_by(order_type=order_type)
        
        templates = query.order_by(WorkflowTemplate.created_date.desc()).all()
        
        result = []
        for template in templates:
            # 获取节点数量
            node_count = WorkflowNode.query.filter_by(template_id=template.id).count()
            
            result.append({
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'order_type': template.order_type,
                'is_default': template.is_default,
                'is_active': template.is_active,
                'node_count': node_count,
                'created_date': template.created_date.strftime('%Y-%m-%d %H:%M') if template.created_date else None,
                'updated_date': template.updated_date.strftime('%Y-%m-%d %H:%M') if template.updated_date else None
            })
        
        return jsonify({'success': True, 'templates': result})
    
    except Exception as e:
        logger.error(f"获取模板列表失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取模板列表失败: {str(e)}'}), 500


@admin_bp.route('/api/workflow_templates/<int:template_id>', methods=['GET'])
@admin_required
def get_workflow_template(template_id):
    """获取模板详情(包含所有节点)"""
    try:
        template = WorkflowTemplate.query.get(template_id)
        if not template:
            return jsonify({'success': False, 'message': '模板不存在'}), 404
        
        # 获取所有节点
        nodes = WorkflowNode.query.filter_by(template_id=template.id)\
            .order_by(WorkflowNode.sequence).all()
        
        nodes_data = []
        for node in nodes:
            nodes_data.append({
                'id': node.id,
                'name': node.name,
                'order_type': node.template.order_type if node.template else None,
                'node_type': node.node_type,
                'sequence': node.sequence,
                'approval_role_id': node.approval_role_id,
                'approval_role_name': node.approval_role.name if node.approval_role else None,
                'is_parallel': node.is_parallel,
                'required_approvals': node.required_approvals,
                'timeout_seconds': node.timeout_seconds,
                'amount_threshold': node.amount_threshold,
                'skip_if_below_threshold': node.skip_if_below_threshold,
                'is_active': node.is_active
            })
        
        template_data = {
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'order_type': template.order_type,
            'is_default': template.is_default,
            'is_active': template.is_active,
            'created_date': template.created_date.strftime('%Y-%m-%d %H:%M') if template.created_date else None,
            'updated_date': template.updated_date.strftime('%Y-%m-%d %H:%M') if template.updated_date else None,
            'nodes': nodes_data
        }
        
        return jsonify({'success': True, 'template': template_data})
    
    except Exception as e:
        logger.error(f"获取模板详情失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取模板详情失败: {str(e)}'}), 500


@admin_bp.route('/api/workflow_templates/create', methods=['POST'])
@admin_required
def create_workflow_template():
    """创建新模板"""
    try:
        data = request.get_json()
        
        # 检查是否已有同名模板
        existing = WorkflowTemplate.query.filter_by(
            name=data['name'],
            order_type=data['order_type']
        ).first()
        
        if existing:
            return jsonify({'success': False, 'message': '已存在同名模板'}), 400
        
        # 创建模板
        template = WorkflowTemplate(
            name=data['name'],
            description=data.get('description', ''),
            order_type=data['order_type'],
            is_default=data.get('is_default', False),
            is_active=data.get('is_active', True)
        )
        db.session.add(template)
        db.session.commit()
        
        logger.info(f"创建模板成功: {template.name} (ID: {template.id})")
        return jsonify({'success': True, 'message': '创建成功', 'template_id': template.id})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建模板失败: {str(e)}")
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500


@admin_bp.route('/api/workflow_templates/<int:template_id>/update', methods=['PUT'])
@admin_required
def update_workflow_template(template_id):
    """更新模板基本信息"""
    try:
        template = WorkflowTemplate.query.get(template_id)
        if not template:
            return jsonify({'success': False, 'message': '模板不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            template.name = data['name']
        if 'description' in data:
            template.description = data['description']
        if 'is_default' in data:
            template.is_default = data['is_default']
        if 'is_active' in data:
            template.is_active = data['is_active']
        
        db.session.commit()
        
        logger.info(f"更新模板成功: {template.name} (ID: {template.id})")
        return jsonify({'success': True, 'message': '更新成功'})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新模板失败: {str(e)}")
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@admin_bp.route('/api/workflow_templates/<int:template_id>/delete', methods=['DELETE'])
@admin_required
def delete_workflow_template(template_id):
    """删除模板(软删除:设为非激活)"""
    try:
        template = WorkflowTemplate.query.get(template_id)
        if not template:
            return jsonify({'success': False, 'message': '模板不存在'}), 404
        
        # 检查是否为默认模板
        if template.is_default:
            return jsonify({'success': False, 'message': '默认模板不能删除,请先取消默认标记'}), 400
        
        # 软删除:设为非激活
        template.is_active = False
        db.session.commit()
        
        logger.info(f"删除模板成功: {template.name} (ID: {template.id})")
        return jsonify({'success': True, 'message': '删除成功'})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除模板失败: {str(e)}")
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


@admin_bp.route('/api/workflow_templates/<int:template_id>/clone', methods=['POST'])
@admin_required
def clone_workflow_template(template_id):
    """克隆模板(复制模板及所有节点)"""
    try:
        source_template = WorkflowTemplate.query.get(template_id)
        if not source_template:
            return jsonify({'success': False, 'message': '源模板不存在'}), 404
        
        data = request.get_json()
        new_name = data.get('name', f"{source_template.name} (副本)")
        
        # 创建新模板
        new_template = WorkflowTemplate(
            name=new_name,
            description=source_template.description,
            order_type=source_template.order_type,
            is_default=False,  # 克隆的模板不设为默认
            is_active=True
        )
        db.session.add(new_template)
        db.session.flush()
        
        # 复制所有节点
        source_nodes = WorkflowNode.query.filter_by(template_id=source_template.id)\
            .order_by(WorkflowNode.sequence).all()
        
        for source_node in source_nodes:
            new_node = WorkflowNode(
                template_id=new_template.id,
                name=source_node.name,
                order_type=source_node.template.order_type if source_node.template else None,
                node_type=source_node.node_type,
                sequence=source_node.sequence,
                approval_role_id=source_node.approval_role_id,
                approver_user_id=source_node.approver_user_id,
                approver_user_ids=source_node.approver_user_ids,
                is_parallel=source_node.is_parallel,
                required_approvals=source_node.required_approvals,
                timeout_seconds=source_node.timeout_seconds,
                amount_threshold=source_node.amount_threshold,
                skip_if_below_threshold=source_node.skip_if_below_threshold,
                is_active=source_node.is_active
            )
            db.session.add(new_node)
        
        db.session.commit()
        
        logger.info(f"克隆模板成功: {source_template.name} -> {new_template.name} (ID: {new_template.id})")
        return jsonify({'success': True, 'message': '克隆成功', 'template_id': new_template.id})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"克隆模板失败: {str(e)}")
        return jsonify({'success': False, 'message': f'克隆失败: {str(e)}'}), 500


@admin_bp.route('/api/workflow_templates/<int:template_id>/activate', methods=['POST'])
@admin_required
def activate_workflow_template(template_id):
    """激活/停用模板"""
    try:
        template = WorkflowTemplate.query.get(template_id)
        if not template:
            return jsonify({'success': False, 'message': '模板不存在'}), 404
        
        data = request.get_json()
        is_active = data.get('is_active', True)
        
        template.is_active = is_active
        db.session.commit()
        
        status = "激活" if is_active else "停用"
        logger.info(f"{status}模板成功: {template.name} (ID: {template.id})")
        return jsonify({'success': True, 'message': f'{status}成功'})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新模板状态失败: {str(e)}")
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500


@admin_bp.route('/api/workflow_templates/<int:template_id>/set_default', methods=['POST'])
@admin_required
def set_default_template(template_id):
    """设置为默认模板(同一工单类型只能有一个默认模板)"""
    try:
        template = WorkflowTemplate.query.get(template_id)
        if not template:
            return jsonify({'success': False, 'message': '模板不存在'}), 404
        
        # 取消同一工单类型的其他默认模板
        WorkflowTemplate.query.filter_by(
            order_type=template.order_type,
            is_default=True
        ).update({'is_default': False})
        
        # 设置为默认
        template.is_default = True
        template.is_active = True  # 默认模板必须激活
        db.session.commit()
        
        logger.info(f"设置默认模板成功: {template.name} (ID: {template.id})")
        return jsonify({'success': True, 'message': '设置成功'})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"设置默认模板失败: {str(e)}")
        return jsonify({'success': False, 'message': f'设置失败: {str(e)}'}), 500
