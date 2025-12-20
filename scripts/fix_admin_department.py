"""
确保admin用户不属于任何部门
使admin拥有全局权限
"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # 查找所有admin角色的用户
    admin_users = User.query.filter_by(role='admin').all()
    
    if not admin_users:
        print("未找到admin用户")
    else:
        for admin_user in admin_users:
            print(f"\n处理admin用户: {admin_user.username}")
            print(f"  当前部门: {admin_user.department}")
            print(f"  当前部门ID: {admin_user.department_id}")
            
            # 清空admin的部门信息
            admin_user.department = None
            admin_user.department_id = None
            
            print(f"  已清空部门信息")
        
        try:
            db.session.commit()
            print("\n✓ 成功更新admin用户，使其不属于任何部门")
            print("✓ admin现在拥有全局权限，可以查看和管理所有部门的数据")
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ 更新失败: {str(e)}")
