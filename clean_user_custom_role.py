"""
清理 user_custom_role 表中的无效数据
1. 删除 is_active=0 的记录
2. 删除角色不存在的记录
3. 删除用户不存在的记录
"""
import sqlite3

def clean_user_custom_role():
    """清理 user_custom_role 表"""
    
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    try:
        print("开始清理 user_custom_role 表...")
        
        # 1. 统计总记录数
        cursor.execute("SELECT COUNT(*) FROM user_custom_role")
        total_before = cursor.fetchone()[0]
        print(f"清理前总记录数: {total_before}")
        
        # 2. 删除不活跃的记录
        cursor.execute("DELETE FROM user_custom_role WHERE is_active = 0")
        inactive_deleted = cursor.rowcount
        print(f"✓ 删除了 {inactive_deleted} 条不活跃记录")
        
        # 3. 删除角色不存在的记录
        cursor.execute("""
            DELETE FROM user_custom_role 
            WHERE role_id NOT IN (SELECT id FROM role_definition)
        """)
        orphan_role_deleted = cursor.rowcount
        print(f"✓ 删除了 {orphan_role_deleted} 条孤立角色记录(角色已被删除)")
        
        # 4. 删除用户不存在的记录
        cursor.execute("""
            DELETE FROM user_custom_role 
            WHERE user_id NOT IN (SELECT id FROM user)
        """)
        orphan_user_deleted = cursor.rowcount
        print(f"✓ 删除了 {orphan_user_deleted} 条孤立用户记录(用户已被删除)")
        
        # 5. 统计清理后记录数
        cursor.execute("SELECT COUNT(*) FROM user_custom_role")
        total_after = cursor.fetchone()[0]
        print(f"\n清理后总记录数: {total_after}")
        print(f"共删除: {total_before - total_after} 条记录")
        
        # 6. 显示剩余记录
        if total_after > 0:
            print("\n剩余有效记录:")
            cursor.execute("""
                SELECT ucr.user_id, u.username, ucr.role_id, r.name, 
                       ucr.assigned_date, ucr.is_active
                FROM user_custom_role ucr
                LEFT JOIN user u ON ucr.user_id = u.id
                LEFT JOIN role_definition r ON ucr.role_id = r.id
            """)
            for row in cursor.fetchall():
                user_id, username, role_id, role_name, assigned_date, is_active = row
                status = "✓活跃" if is_active else "✗不活跃"
                print(f"  - 用户: {username}(ID:{user_id}), 角色: {role_name}(ID:{role_id}), 状态: {status}, 时间: {assigned_date}")
        else:
            print("\n⚠ 没有剩余记录")
        
        conn.commit()
        print("\n✓ 清理完成!")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ 清理失败: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    clean_user_custom_role()
