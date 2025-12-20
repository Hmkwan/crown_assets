"""
用户API路由 - 用于管理员干预界面
"""
from flask import jsonify
from flask_login import login_required, current_user
from app.models import User
from app.main import bp

@bp.route('/api/users/list')
@login_required
def api_users_list():
    """获取用户列表 - 用于管理员转交审批"""
    if current_user.role not in ['admin', 'super_admin']:
        return jsonify({'error': '权限不足'}), 403
    
    users = User.query.filter(User.is_active == True).all()
    
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'department': user.department if user.department else '无'
        })
    
    return jsonify({'users': user_list})
