"""
测试公开仓库功能
"""
import sqlite3
import os

# 获取数据库路径
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db')

print("=== 公开仓库功能测试 ===\n")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. 检查SparePart表是否有is_public字段
    print("1. 检查SparePart表结构:")
    cursor.execute("PRAGMA table_info(spare_part)")
    columns = cursor.fetchall()
    has_is_public = False
    for col in columns:
        if col[1] == 'is_public':
            has_is_public = True
            print(f"   ✓ 找到is_public字段: {col}")
    
    if not has_is_public:
        print("   ✗ 未找到is_public字段!")
    
    # 2. 检查公开设备数量
    print("\n2. 公开设备统计:")
    cursor.execute("SELECT COUNT(*) FROM equipment WHERE is_public_pool = 1")
    public_equipment_count = cursor.fetchone()[0]
    print(f"   公开设备数量: {public_equipment_count}")
    
    # 3. 检查公开配件数量
    print("\n3. 公开配件统计:")
    cursor.execute("SELECT COUNT(*) FROM spare_part WHERE is_public = 1")
    public_spare_part_count = cursor.fetchone()[0]
    print(f"   公开配件数量: {public_spare_part_count}")
    
    # 4. 列出所有公开设备
    if public_equipment_count > 0:
        print("\n4. 公开设备列表:")
        cursor.execute("""
            SELECT e.id, e.name, e.asset_number, d.name as dept_name 
            FROM equipment e 
            LEFT JOIN department d ON e.department_id = d.id
            WHERE e.is_public_pool = 1 
            LIMIT 5
        """)
        for row in cursor.fetchall():
            print(f"   - [ID:{row[0]}] {row[1]} (编号:{row[2]}) - {row[3]}")
    
    # 5. 列出所有公开配件
    if public_spare_part_count > 0:
        print("\n5. 公开配件列表:")
        cursor.execute("""
            SELECT id, name, part_number, department 
            FROM spare_part 
            WHERE is_public = 1 
            LIMIT 5
        """)
        for row in cursor.fetchall():
            print(f"   - [ID:{row[0]}] {row[1]} (编号:{row[2]}) - {row[3]}")
    
    # 6. 测试建议:设置一些配件为公开
    if public_spare_part_count == 0:
        print("\n💡 建议: 当前没有公开配件,可以通过以下方式设置:")
        print("   1. 访问配件管理页面 (/spare_parts)")
        print("   2. 使用admin账号登录")
        print("   3. 勾选配件后点击'批量公开'按钮")
        print("   或")
        print("   4. 点击单个配件的'设为公开'按钮")
    
    print("\n=== 测试完成 ===")
    
    conn.close()
    
except Exception as e:
    print(f"✗ 测试失败: {str(e)}")
    if 'conn' in locals():
        conn.close()
