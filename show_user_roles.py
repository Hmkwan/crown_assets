"""
查看用户自定义角色分配详情
显示完整的用户名、角色名、分配人等信息
"""
import sqlite3
from datetime import datetime

def show_user_custom_roles():
    """显示用户角色分配的完整信息"""
    
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    try:
        print("=" * 100)
        print("用户自定义角色分配详情".center(100))
        print("=" * 100)
        
        # 查询完整信息(包含用户名、角色名、分配人)
        cursor.execute("""
            SELECT 
                ucr.user_id,
                u.username AS 用户名,
                u.department AS 部门,
                ucr.role_id,
                r.name AS 角色名,
                r.description AS 角色描述,
                ucr.assigned_by_id,
                assigner.username AS 分配人,
                ucr.assigned_date AS 分配时间,
                ucr.expired_date AS 过期时间,
                ucr.is_active AS 是否活跃,
                ucr.notes AS 备注
            FROM user_custom_role ucr
            LEFT JOIN user u ON ucr.user_id = u.id
            LEFT JOIN role_definition r ON ucr.role_id = r.id
            LEFT JOIN user assigner ON ucr.assigned_by_id = assigner.id
            ORDER BY ucr.assigned_date DESC
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("\n⚠ 没有找到任何角色分配记录")
            print("\n提示: 请在权限管理页面为用户分配角色")
            return
        
        print(f"\n共找到 {len(rows)} 条记录:\n")
        
        for i, row in enumerate(rows, 1):
            user_id, username, dept, role_id, role_name, role_desc, assigned_by_id, assigner, \
            assigned_date, expired_date, is_active, notes = row
            
            print(f"【记录 {i}】")
            print(f"  用户: {username} (ID:{user_id}) - {dept or '未设置部门'}")
            print(f"  角色: {role_name or '角色已删除'} (ID:{role_id})")
            if role_desc:
                print(f"  角色说明: {role_desc}")
            print(f"  分配人: {assigner or '系统迁移'} (ID:{assigned_by_id or 'NULL'})")
            print(f"  分配时间: {assigned_date}")
            
            if expired_date:
                exp_dt = datetime.strptime(expired_date, '%Y-%m-%d %H:%M:%S')
                now = datetime.now()
                if exp_dt < now:
                    print(f"  过期时间: {expired_date} ⚠ 已过期")
                else:
                    days_left = (exp_dt - now).days
                    print(f"  过期时间: {expired_date} (剩余{days_left}天)")
            else:
                print(f"  过期时间: 永久有效")
            
            status = "✓ 活跃" if is_active else "✗ 已停用"
            print(f"  状态: {status}")
            
            if notes:
                print(f"  备注: {notes}")
            
            print()
        
        # 统计信息
        cursor.execute("SELECT COUNT(*) FROM user_custom_role WHERE is_active = 1")
        active_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_custom_role WHERE is_active = 0")
        inactive_count = cursor.fetchone()[0]
        
        print("=" * 100)
        print(f"统计: 活跃 {active_count} 条 | 已停用 {inactive_count} 条")
        print("=" * 100)
        
    except Exception as e:
        print(f"✗ 查询失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


def show_role_permissions():
    """显示角色的权限配置"""
    
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    try:
        print("\n" + "=" * 100)
        print("角色权限配置".center(100))
        print("=" * 100)
        
        cursor.execute("""
            SELECT 
                r.id,
                r.name,
                r.description,
                r.is_active,
                COUNT(p.id) AS 权限数量,
                COUNT(ucr.user_id) AS 分配用户数
            FROM role_definition r
            LEFT JOIN permission p ON r.id = p.role_id AND p.is_granted = 1
            LEFT JOIN user_custom_role ucr ON r.id = ucr.role_id AND ucr.is_active = 1
            GROUP BY r.id, r.name, r.description, r.is_active
            ORDER BY r.id
        """)
        
        roles = cursor.fetchall()
        
        if not roles:
            print("\n⚠ 没有找到任何自定义角色")
            return
        
        print(f"\n共有 {len(roles)} 个角色:\n")
        
        for role_id, name, desc, is_active, perm_count, user_count in roles:
            status = "✓ 活跃" if is_active else "✗ 已停用"
            print(f"【{name}】 (ID:{role_id}) - {status}")
            if desc:
                print(f"  说明: {desc}")
            print(f"  权限数量: {perm_count}")
            print(f"  分配用户: {user_count}")
            
            # 显示具体权限
            if perm_count > 0:
                cursor.execute("""
                    SELECT module, action 
                    FROM permission 
                    WHERE role_id = ? AND is_granted = 1
                    ORDER BY module, action
                """, (role_id,))
                perms = cursor.fetchall()
                modules = {}
                for module, action in perms:
                    if module not in modules:
                        modules[module] = []
                    modules[module].append(action)
                
                print(f"  权限详情:")
                for module, actions in modules.items():
                    print(f"    - {module}: {', '.join(actions)}")
            
            # 显示分配的用户
            if user_count > 0:
                cursor.execute("""
                    SELECT u.username, u.department
                    FROM user_custom_role ucr
                    JOIN user u ON ucr.user_id = u.id
                    WHERE ucr.role_id = ? AND ucr.is_active = 1
                """, (role_id,))
                users = cursor.fetchall()
                print(f"  分配给:")
                for username, dept in users:
                    print(f"    - {username} ({dept or '无部门'})")
            
            print()
        
        print("=" * 100)
        
    except Exception as e:
        print(f"✗ 查询失败: {str(e)}")
    finally:
        conn.close()


if __name__ == '__main__':
    show_user_custom_roles()
    show_role_permissions()
