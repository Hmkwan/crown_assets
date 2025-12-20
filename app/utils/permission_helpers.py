"""
权限辅助函数
用于统一处理admin全局权限和部门权限
"""
from flask_login import current_user


def can_access_department(department_name=None, department_id=None):
    """
    检查当前用户是否可以访问指定部门的数据
    
    Args:
        department_name: 部门名称
        department_id: 部门ID
    
    Returns:
        bool: True表示可以访问
    
    规则:
        - admin角色: 可以访问所有部门
        - 其他角色: 只能访问自己所属部门
    """
    if not current_user.is_authenticated:
        return False
    
    # admin拥有全局权限，可以访问所有部门
    if current_user.role == 'admin':
        return True
    
    # 其他用户只能访问自己的部门
    if department_name:
        return current_user.department == department_name
    
    if department_id:
        return current_user.department_id == department_id
    
    return False


def filter_by_department(query, model_department_field='department'):
    """
    根据用户权限过滤查询结果
    
    Args:
        query: SQLAlchemy查询对象
        model_department_field: 模型中部门字段的名称（默认'department'）
    
    Returns:
        过滤后的查询对象
    
    规则:
        - admin: 不过滤，返回所有数据
        - 其他角色: 只返回本部门数据
    """
    if not current_user.is_authenticated:
        return query.filter(False)  # 返回空结果
    
    # admin不需要过滤
    if current_user.role == 'admin':
        return query
    
    # 其他用户按部门过滤
    if current_user.department:
        return query.filter(getattr(query.column_descriptions[0]['type'], model_department_field) == current_user.department)
    
    return query.filter(False)  # 没有部门的用户返回空结果


def is_admin():
    """
    检查当前用户是否是admin
    
    Returns:
        bool: True表示是admin
    """
    return current_user.is_authenticated and current_user.role == 'admin'


def get_accessible_departments():
    """
    获取当前用户可访问的部门列表
    
    Returns:
        list: 部门对象列表
    
    规则:
        - admin: 返回所有部门
        - 其他角色: 只返回自己所属部门
    """
    from app.models import Department
    
    if not current_user.is_authenticated:
        return []
    
    # admin可以访问所有部门
    if current_user.role == 'admin':
        return Department.query.all()
    
    # 其他用户只能访问自己的部门
    if current_user.department_id:
        dept = Department.query.get(current_user.department_id)
        return [dept] if dept else []
    
    return []


def can_manage_user(target_user):
    """
    检查当前用户是否可以管理目标用户
    
    Args:
        target_user: 目标用户对象
    
    Returns:
        bool: True表示可以管理
    
    规则:
        - admin: 可以管理所有用户
        - department_head: 只能管理本部门用户
        - 其他角色: 不能管理用户
    """
    if not current_user.is_authenticated:
        return False
    
    # admin可以管理所有用户
    if current_user.role == 'admin':
        return True
    
    # 部门经理只能管理本部门用户
    if current_user.role == 'department_head':
        return current_user.department == target_user.department
    
    return False


def can_view_all_data():
    """
    检查当前用户是否可以查看所有数据（跨部门）
    
    Returns:
        bool: True表示可以查看所有数据
    """
    return current_user.is_authenticated and current_user.role == 'admin'


def apply_department_filter(query, model_class, department_field='department'):
    """
    应用部门过滤器到查询
    
    Args:
        query: SQLAlchemy查询对象
        model_class: 模型类
        department_field: 部门字段名（默认'department'）
    
    Returns:
        过滤后的查询对象
    """
    if not current_user.is_authenticated:
        return query.filter(False)
    
    # admin不需要过滤
    if current_user.role == 'admin':
        return query
    
    # 其他用户按部门过滤
    if hasattr(model_class, department_field):
        if department_field == 'department_id':
            # 使用department_id字段
            if current_user.department_id:
                return query.filter(getattr(model_class, department_field) == current_user.department_id)
        else:
            # 使用department字符串字段
            if current_user.department:
                return query.filter(getattr(model_class, department_field) == current_user.department)
    
    return query.filter(False)
