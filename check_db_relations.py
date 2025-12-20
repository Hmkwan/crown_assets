import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

print("=" * 80)
print("权限系统表结构检查")
print("=" * 80)

# 检查role_definition表
print("\n【role_definition 表】")
cursor.execute("PRAGMA table_info(role_definition)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]}: {col[2]}")

cursor.execute("PRAGMA foreign_key_list(role_definition)")
fks = cursor.fetchall()
if fks:
    print("  外键:")
    for fk in fks:
        print(f"    {fk[3]} -> {fk[2]}.{fk[4]}")

# 检查permission表
print("\n【permission 表】")
cursor.execute("PRAGMA table_info(permission)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]}: {col[2]}")

cursor.execute("PRAGMA foreign_key_list(permission)")
fks = cursor.fetchall()
if fks:
    print("  外键:")
    for fk in fks:
        print(f"    {fk[3]} -> {fk[2]}.{fk[4]}")

# 检查user_custom_role表
print("\n【user_custom_role 表】(多对多关联)")
cursor.execute("PRAGMA table_info(user_custom_role)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]}: {col[2]}")

cursor.execute("PRAGMA foreign_key_list(user_custom_role)")
fks = cursor.fetchall()
if fks:
    print("  外键:")
    for fk in fks:
        print(f"    {fk[3]} -> {fk[2]}.{fk[4]}")

# 检查数据
print("\n" + "=" * 80)
print("数据检查")
print("=" * 80)

cursor.execute("SELECT COUNT(*) FROM role_definition")
role_count = cursor.fetchone()[0]
print(f"\n角色总数: {role_count}")

cursor.execute("SELECT id, name, description, is_custom, is_active FROM role_definition")
roles = cursor.fetchall()
for role in roles:
    print(f"\n角色 ID={role[0]}: {role[1]}")
    print(f"  描述: {role[2] or '无'}")
    print(f"  类型: {'自定义' if role[3] else '系统内置'}")
    print(f"  状态: {'启用' if role[4] else '禁用'}")
    
    # 检查该角色的权限
    cursor.execute("SELECT COUNT(*) FROM permission WHERE role_id = ?", (role[0],))
    perm_count = cursor.fetchone()[0]
    print(f"  权限数: {perm_count}")
    
    # 检查该角色的用户
    cursor.execute("SELECT COUNT(*) FROM user_custom_role WHERE role_id = ?", (role[0],))
    user_count = cursor.fetchone()[0]
    print(f"  用户数: {user_count}")

print("\n" + "=" * 80)
print("关联完整性检查")
print("=" * 80)

# 检查是否有孤立的权限(role_id不存在)
cursor.execute("""
    SELECT p.id, p.module, p.action, p.role_id 
    FROM permission p 
    LEFT JOIN role_definition r ON p.role_id = r.id 
    WHERE r.id IS NULL
""")
orphan_perms = cursor.fetchall()
if orphan_perms:
    print(f"\n⚠️  发现 {len(orphan_perms)} 个孤立的权限记录:")
    for perm in orphan_perms:
        print(f"  Permission ID={perm[0]}: {perm[1]}.{perm[2]} (role_id={perm[3]})")
else:
    print("\n✓ 权限表无孤立记录")

# 检查是否有孤立的用户角色关联
cursor.execute("""
    SELECT ucr.user_id, ucr.role_id 
    FROM user_custom_role ucr 
    LEFT JOIN user u ON ucr.user_id = u.id 
    LEFT JOIN role_definition r ON ucr.role_id = r.id 
    WHERE u.id IS NULL OR r.id IS NULL
""")
orphan_user_roles = cursor.fetchall()
if orphan_user_roles:
    print(f"\n⚠️  发现 {len(orphan_user_roles)} 个孤立的用户角色关联:")
    for ur in orphan_user_roles:
        print(f"  user_id={ur[0]}, role_id={ur[1]}")
else:
    print("✓ 用户角色关联表无孤立记录")

print("\n" + "=" * 80)
print("检查完成!")
print("=" * 80)

conn.close()
