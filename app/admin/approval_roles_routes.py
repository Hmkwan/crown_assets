"""审批角色管理路由"""
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.admin.workflow_config_routes import admin_bp as bp
from app import db
from app.models import User
from app.approval_roles import ApprovalRole, UserApprovalRole
from app.decorators import admin_required
from datetime import datetime


@bp.route('/approval_roles')
@login_required
@admin_required
def approval_roles():
    """审批角色管理页面"""
    # 获取所有角色
    roles = ApprovalRole.query.filter_by(is_active=True).order_by(ApprovalRole.level.desc()).all()
    
    return render_template('admin/approval_roles.html', roles=roles)


@bp.route('/approval_roles/list')
@login_required
@admin_required
def get_approval_roles():
    """获取所有审批角色列表"""
    roles = ApprovalRole.query.filter_by(is_active=True).order_by(ApprovalRole.level.desc()).all()
    
    return jsonify({
        'success': True,
        'roles': [role.to_dict() for role in roles]
    })


@bp.route('/approval_roles/<int:role_id>')
@login_required
@admin_required
def get_approval_role(role_id):
    """获取单个审批角色详情"""
    role = ApprovalRole.query.get_or_404(role_id)
    
    # 获取拥有此角色的用户
    assignments = UserApprovalRole.query.filter_by(
        role_id=role_id,
        is_active=True
    ).all()
    
    users = []
    for assignment in assignments:
        if assignment.is_valid():
            user = assignment.user
            users.append({
                'id': user.id,
                'username': user.username,
                'name': user.username,
                'department_name': user.get_department_name(),
                'assigned_date': assignment.assigned_date.strftime('%Y-%m-%d') if assignment.assigned_date else None,
                'start_date': assignment.start_date.strftime('%Y-%m-%d') if assignment.start_date else None,
                'end_date': assignment.end_date.strftime('%Y-%m-%d') if assignment.end_date else None
            })
    
    data = role.to_dict()
    data['users'] = users
    
    return jsonify({
        'success': True,
        'role': data
    })


@bp.route('/approval_roles/create', methods=['POST'])
@login_required
@admin_required
def create_approval_role():
    """创建新的审批角色"""
    data = request.get_json()
    
    # 验证必填字段
    if not data.get('code') or not data.get('name'):
        return jsonify({'error': '角色代码和名称不能为空'}), 400
    
    # 检查代码是否已存在
    existing = ApprovalRole.query.filter_by(code=data['code']).first()
    if existing:
        return jsonify({'error': '角色代码已存在'}), 400
    
    try:
        role = ApprovalRole(
            code=data['code'],
            name=data['name'],
            description=data.get('description', ''),
            category=data.get('category', 'custom'),
            level=int(data.get('level', 10)),
            icon=data.get('icon', 'fa-user'),
            color=data.get('color', '#6c757d'),
            can_approve_repair=data.get('can_approve_repair', False),
            can_approve_part_request=data.get('can_approve_part_request', False),
            can_approve_equipment_transfer=data.get('can_approve_equipment_transfer', False),
            can_approve_equipment_scrap=data.get('can_approve_equipment_scrap', False),
            can_approve_equipment_loan=data.get('can_approve_equipment_loan', False),
            can_approve_equipment_application=data.get('can_approve_equipment_application', False),
            max_approval_amount=float(data.get('max_approval_amount', 0)) if data.get('max_approval_amount') else None,
            is_system_role=False
        )
        
        db.session.add(role)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '审批角色创建成功',
            'role': role.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建失败: {str(e)}'}), 500


@bp.route('/approval_roles/<int:role_id>/update', methods=['PUT'])
@login_required
@admin_required
def update_approval_role(role_id):
    """更新审批角色"""
    role = ApprovalRole.query.get_or_404(role_id)
    
    # 系统角色只允许修改部分字段
    if role.is_system_role:
        return jsonify({'error': '系统角色不允许修改'}), 403
    
    data = request.get_json()
    
    try:
        # 更新字段
        if 'name' in data:
            role.name = data['name']
        if 'description' in data:
            role.description = data['description']
        if 'level' in data:
            role.level = int(data['level'])
        if 'icon' in data:
            role.icon = data['icon']
        if 'color' in data:
            role.color = data['color']
        
        # 更新权限
        if 'can_approve_repair' in data:
            role.can_approve_repair = data['can_approve_repair']
        if 'can_approve_part_request' in data:
            role.can_approve_part_request = data['can_approve_part_request']
        if 'can_approve_equipment_transfer' in data:
            role.can_approve_equipment_transfer = data['can_approve_equipment_transfer']
        if 'can_approve_equipment_scrap' in data:
            role.can_approve_equipment_scrap = data['can_approve_equipment_scrap']
        if 'can_approve_equipment_loan' in data:
            role.can_approve_equipment_loan = data['can_approve_equipment_loan']
        if 'can_approve_equipment_application' in data:
            role.can_approve_equipment_application = data['can_approve_equipment_application']
        
        if 'max_approval_amount' in data:
            role.max_approval_amount = float(data['max_approval_amount']) if data['max_approval_amount'] else None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '审批角色更新成功',
            'role': role.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新失败: {str(e)}'}), 500


@bp.route('/approval_roles/<int:role_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_approval_role(role_id):
    """删除审批角色"""
    role = ApprovalRole.query.get_or_404(role_id)
    
    # 系统角色不允许删除
    if role.is_system_role:
        return jsonify({'error': '系统角色不允许删除'}), 403
    
    # 检查是否有用户正在使用此角色
    active_assignments = UserApprovalRole.query.filter_by(
        role_id=role_id,
        is_active=True
    ).count()
    
    if active_assignments > 0:
        return jsonify({'error': f'还有 {active_assignments} 个用户正在使用此角色,无法删除'}), 400
    
    try:
        role.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '审批角色删除成功'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除失败: {str(e)}'}), 500


@bp.route('/approval_roles/assign')
@login_required
@admin_required
def assign_roles_page():
    """角色分配页面"""
    # 获取所有活跃角色
    roles = ApprovalRole.query.filter_by(is_active=True).order_by(ApprovalRole.level.desc()).all()
    
    # 获取所有用户
    users = User.query.filter_by(is_active=True).order_by(User.username).all()
    
    return render_template('admin/assign_approval_roles.html', roles=roles, users=users)


@bp.route('/approval_roles/assign/create', methods=['POST'])
@login_required
@admin_required
def assign_role_to_user():
    """为用户分配审批角色"""
    data = request.get_json()
    
    user_id = data.get('user_id')
    role_id = data.get('role_id')
    
    if not user_id or not role_id:
        return jsonify({'error': '用户ID和角色ID不能为空'}), 400
    
    # 验证用户和角色存在
    user = User.query.get(user_id)
    role = ApprovalRole.query.get(role_id)
    
    if not user or not role:
        return jsonify({'error': '用户或角色不存在'}), 404
    
    # 检查是否已分配
    existing = UserApprovalRole.query.filter_by(
        user_id=user_id,
        role_id=role_id,
        is_active=True
    ).first()
    
    if existing and existing.is_valid():
        return jsonify({'error': '该用户已拥有此角色'}), 400
    
    try:
        # 解析日期
        start_date = None
        end_date = None
        
        if data.get('start_date'):
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        if data.get('end_date'):
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        
        assignment = UserApprovalRole(
            user_id=user_id,
            role_id=role_id,
            assigned_by_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            notes=data.get('notes', '')
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'已为用户 {user.username} 分配角色 {role.name}'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'分配失败: {str(e)}'}), 500


@bp.route('/approval_roles/assign/<int:assignment_id>/revoke', methods=['DELETE'])
@login_required
@admin_required
def revoke_role_from_user(assignment_id):
    """撤销用户的审批角色"""
    assignment = UserApprovalRole.query.get_or_404(assignment_id)
    
    try:
        assignment.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '角色已撤销'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'撤销失败: {str(e)}'}), 500


@bp.route('/approval_roles/user/<int:user_id>')
@login_required
def get_user_approval_roles(user_id):
    """获取用户的所有审批角色"""
    if current_user.role != 'admin' and current_user.id != user_id:
        return jsonify({'error': '权限不足'}), 403
    
    user = User.query.get_or_404(user_id)
    
    assignments = UserApprovalRole.query.filter_by(
        user_id=user_id,
        is_active=True
    ).all()
    
    roles = []
    for assignment in assignments:
        if assignment.is_valid():
            role = assignment.role
            roles.append({
                'assignment_id': assignment.id,
                'role_id': role.id,
                'role_code': role.code,
                'role_name': role.name,
                'role_icon': role.icon,
                'role_color': role.color,
                'level': role.level,
                'assigned_date': assignment.assigned_date.strftime('%Y-%m-%d') if assignment.assigned_date else None,
                'start_date': assignment.start_date.strftime('%Y-%m-%d') if assignment.start_date else None,
                'end_date': assignment.end_date.strftime('%Y-%m-%d') if assignment.end_date else None,
                'assigned_by': assignment.assigned_by.username if assignment.assigned_by else None
            })
    
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'name': user.username,
            'department_name': user.get_department_name()
        },
        'roles': roles
    })
