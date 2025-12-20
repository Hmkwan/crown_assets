"""
用户审批流角色管理路由
提供用户角色查看和设置的管理界面
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import User
import json

user_roles_bp = Blueprint('user_roles', __name__, url_prefix='/admin/user-roles')


@user_roles_bp.route('/')
@login_required
def index():
    """用户审批流角色管理页面"""
    if not current_user.is_admin():
        flash('无权访问', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.order_by(User.username).all()
    
    # 可用的审批流角色列表
    available_roles = [
        {'value': 'employee', 'label': '员工'},
        {'value': 'department_head', 'label': '部门经理'},
        {'value': 'admin', 'label': '系统管理员'},
        {'value': 'procurement', 'label': '采购'},
        {'value': 'warehouse', 'label': '库房'},
        {'value': 'security', 'label': '安全/合规'},
        {'value': 'finance', 'label': '财务'},
        {'value': 'executive', 'label': '总经理/高层'},
        {'value': 'auditor', 'label': '审计/稽核'}
    ]
    
    return render_template('admin/user_workflow_roles.html', 
                         users=users, 
                         available_roles=available_roles)


@user_roles_bp.route('/api/get/<int:user_id>')
@login_required
def get_user_roles(user_id):
    """获取用户的审批流角色"""
    if not current_user.is_admin():
        return jsonify({'error': '无权访问'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify({
        'user_id': user.id,
        'username': user.username,
        'workflow_roles': user.get_workflow_roles(),
        'workflow_roles_display': user.get_workflow_roles_display()
    })


@user_roles_bp.route('/api/set/<int:user_id>', methods=['POST'])
@login_required
def set_user_roles(user_id):
    """设置用户的审批流角色"""
    if not current_user.is_admin():
        return jsonify({'error': '无权访问'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'roles' not in data:
        return jsonify({'error': '缺少roles参数'}), 400
    
    roles = data['roles']
    if not isinstance(roles, list):
        return jsonify({'error': 'roles必须是数组'}), 400
    
    # 验证角色是否有效
    valid_roles = ['employee', 'department_head', 'admin', 'procurement', 
                   'warehouse', 'security', 'finance', 'executive', 'auditor']
    
    for role in roles:
        if role not in valid_roles:
            return jsonify({'error': f'无效的角色: {role}'}), 400
    
    # 设置角色
    user.set_workflow_roles(roles)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user_id': user.id,
        'username': user.username,
        'workflow_roles': user.get_workflow_roles(),
        'workflow_roles_display': user.get_workflow_roles_display()
    })


@user_roles_bp.route('/api/batch-set', methods=['POST'])
@login_required
def batch_set_roles():
    """批量设置用户角色"""
    if not current_user.is_admin():
        return jsonify({'error': '无权访问'}), 403
    
    data = request.get_json()
    updates = data.get('updates', [])
    
    success_count = 0
    errors = []
    
    for update in updates:
        try:
            user_id = update.get('user_id')
            roles = update.get('roles', [])
            
            user = User.query.get(user_id)
            if not user:
                errors.append(f'用户ID {user_id} 不存在')
                continue
            
            user.set_workflow_roles(roles)
            success_count += 1
        except Exception as e:
            errors.append(f'更新用户 {user_id} 失败: {str(e)}')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'updated': success_count,
        'errors': errors
    })
