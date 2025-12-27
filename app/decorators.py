"""
权限装饰器
提供统一的权限检查装饰器，替代散落在各处的权限检查代码
"""
from functools import wraps
from flask import flash, redirect, url_for, jsonify, request
from flask_login import current_user


def admin_required(f):
    """
    管理员权限装饰器
    仅允许admin角色访问
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'success': False, 'message': '请先登录'}), 401
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        
        # 兼容 is_admin 属性或方法
        admin_check = getattr(current_user, 'is_admin', False)
        is_admin = admin_check() if callable(admin_check) else bool(admin_check)
        if not is_admin:
            if request.is_json:
                return jsonify({'success': False, 'message': '权限不足'}), 403
            flash('您没有权限访问此页面', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission):
    """
    基于权限标志的装饰器
    示例: @permission_required('can_manage_equipment')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'success': False, 'message': '请先登录'}), 401
                flash('请先登录', 'warning')
                return redirect(url_for('auth.login'))
            
            # 管理员拥有所有权限（兼容属性或方法）
            admin_check = getattr(current_user, 'is_admin', False)
            if callable(admin_check):
                if admin_check():
                    return f(*args, **kwargs)
            elif admin_check:
                return f(*args, **kwargs)
            
            # 检查用户权限
            if not hasattr(current_user, permission) or not getattr(current_user, permission):
                if request.is_json:
                    return jsonify({'success': False, 'message': '权限不足'}), 403
                flash('您没有权限执行此操作', 'danger')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def role_required(*roles):
    """
    基于角色的装饰器（支持多个角色）
    示例: @role_required('admin', 'technician')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'success': False, 'message': '请先登录'}), 401
                flash('请先登录', 'warning')
                return redirect(url_for('auth.login'))
            
            # 管理员自动拥有所有角色权限（兼容属性或方法）
            admin_check = getattr(current_user, 'is_admin', False)
            if callable(admin_check):
                if admin_check():
                    return f(*args, **kwargs)
            elif admin_check:
                return f(*args, **kwargs) 
            
            if current_user.role not in roles:
                if request.is_json:
                    return jsonify({'success': False, 'message': '权限不足'}), 403
                flash('您没有权限访问此页面', 'danger')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def workflow_role_required(*workflow_roles):
    """
    基于审批流角色的装饰器
    示例: @workflow_role_required('finance', 'executive')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'success': False, 'message': '请先登录'}), 401
                flash('请先登录', 'warning')
                return redirect(url_for('auth.login'))
            
            # 管理员自动拥有所有审批流角色权限（兼容属性或方法）
            admin_check = getattr(current_user, 'is_admin', False)
            if callable(admin_check):
                if admin_check():
                    return f(*args, **kwargs)
            elif admin_check:
                return f(*args, **kwargs) 
            
            # 检查用户是否拥有任一所需角色
            user_roles = current_user.get_workflow_roles()
            if not any(role in user_roles for role in workflow_roles):
                if request.is_json:
                    return jsonify({'success': False, 'message': '您没有所需的审批流角色'}), 403
                flash('您没有所需的审批流角色', 'danger')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def api_admin_required(f):
    """
    API专用管理员权限装饰器（总是返回JSON）
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'message': '未认证'}), 401
        
        # 兼容 is_admin 属性或方法
        admin_check = getattr(current_user, 'is_admin', False)
        is_admin = admin_check() if callable(admin_check) else bool(admin_check)
        if not is_admin:
            return jsonify({'success': False, 'message': '权限不足'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def owns_resource_or_admin(resource_owner_field='user_id'):
    """
    资源所有者或管理员装饰器
    用于检查用户是否拥有资源或者是管理员
    
    示例: @owns_resource_or_admin('requester_id')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'success': False, 'message': '请先登录'}), 401
                flash('请先登录', 'warning')
                return redirect(url_for('auth.login'))
            
            # 管理员可以访问所有资源（兼容属性或方法）
            admin_check = getattr(current_user, 'is_admin', False)
            if callable(admin_check):
                if admin_check():
                    return f(*args, **kwargs)
            elif admin_check:
                return f(*args, **kwargs) 
            
            # 获取资源对象（假设在kwargs中有resource对象）
            resource = kwargs.get('resource')
            if resource and hasattr(resource, resource_owner_field):
                owner_id = getattr(resource, resource_owner_field)
                if owner_id == current_user.id:
                    return f(*args, **kwargs)
            
            if request.is_json:
                return jsonify({'success': False, 'message': '权限不足'}), 403
            flash('您没有权限访问此资源', 'danger')
            return redirect(url_for('main.index'))
        
        return decorated_function
    return decorator


def module_permission_required(module, action):
    """
    基于模块和操作的权限装饰器
    检查用户是否有指定模块的指定操作权限
    
    示例: @module_permission_required('announcement', 'create')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'success': False, 'message': '请先登录'}), 401
                flash('请先登录', 'warning')
                return redirect(url_for('auth.login'))
            
            # 管理员拥有所有权限（兼容属性或方法）
            admin_check = getattr(current_user, 'is_admin', False)
            if callable(admin_check):
                if admin_check():
                    return f(*args, **kwargs)
            elif admin_check:
                return f(*args, **kwargs)
            
            # 检查用户的自定义角色权限
            if current_user.has_permission(module, action):
                return f(*args, **kwargs)
            
            if request.is_json:
                return jsonify({'success': False, 'message': f'权限不足: 需要{module}.{action}权限'}), 403
            flash('您没有权限执行此操作', 'danger')
            return redirect(url_for('main.index'))
        
        return decorated_function
    return decorator
