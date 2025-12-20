"""
升级 user_custom_role 表结构
从简单关联表升级为完整模型,添加分配人、时间、过期时间等字段
"""
import sqlite3
from datetime import datetime

def upgrade_user_custom_role():
    """升级 user_custom_role 表"""
    
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    try:
        print("开始升级 user_custom_role 表...")
        
        # 1. 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_custom_role'")
        if not cursor.fetchone():
            print("表 user_custom_role 不存在,无需升级")
            return
        
        # 2. 备份现有数据
        cursor.execute("SELECT * FROM user_custom_role")
        existing_data = cursor.fetchall()
        print(f"备份了 {len(existing_data)} 条现有记录")
        
        # 3. 检查是否已经有新字段
        cursor.execute("PRAGMA table_info(user_custom_role)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'assigned_by_id' in columns:
            print("表已经升级过,跳过")
            return
        
        # 4. 创建新表
        cursor.execute("""
            CREATE TABLE user_custom_role_new (
                user_id INTEGER NOT NULL,
                role_id INTEGER NOT NULL,
                assigned_by_id INTEGER,
                assigned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                expired_date DATETIME,
                is_active BOOLEAN DEFAULT 1,
                notes VARCHAR(500),
                PRIMARY KEY (user_id, role_id),
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (role_id) REFERENCES role_definition(id),
                FOREIGN KEY (assigned_by_id) REFERENCES user(id)
            )
        """)
        
        # 5. 迁移数据(assigned_by_id 设为 NULL,is_active 设为 1)
        if existing_data:
            for row in existing_data:
                user_id, role_id = row
                cursor.execute("""
                    INSERT INTO user_custom_role_new 
                    (user_id, role_id, assigned_date, is_active)
                    VALUES (?, ?, ?, 1)
                """, (user_id, role_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            print(f"迁移了 {len(existing_data)} 条记录")
        
        # 6. 删除旧表
        cursor.execute("DROP TABLE user_custom_role")
        
        # 7. 重命名新表
        cursor.execute("ALTER TABLE user_custom_role_new RENAME TO user_custom_role")
        
        conn.commit()
        print("✓ user_custom_role 表升级成功!")
        print("\n新增字段:")
        print("  - assigned_by_id: 分配人ID")
        print("  - assigned_date: 分配时间")
        print("  - expired_date: 过期时间(可选)")
        print("  - is_active: 是否启用")
        print("  - notes: 备注说明")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ 升级失败: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    upgrade_user_custom_role()
