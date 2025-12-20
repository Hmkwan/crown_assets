import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# 检查角色
cursor.execute('SELECT id, name, is_active FROM role_definition')
roles = cursor.fetchall()
print('现有角色:')
for role in roles:
    print(f'  ID:{role[0]}, 名称:{role[1]}, 活跃:{role[2]}')

# 检查用户
cursor.execute('SELECT id, username, role FROM user WHERE id IN (1,2,5)')
users = cursor.fetchall()
print('\n相关用户:')
for user in users:
    print(f'  ID:{user[0]}, 用户名:{user[1]}, 角色:{user[2]}')

# 检查user_custom_role表
cursor.execute('SELECT * FROM user_custom_role')
assignments = cursor.fetchall()
print(f'\nuser_custom_role 表记录数: {len(assignments)}')
if assignments:
    cursor.execute('PRAGMA table_info(user_custom_role)')
    columns = [col[1] for col in cursor.fetchall()]
    print(f'字段: {columns}')
    for row in assignments:
        print(f'  {row}')

conn.close()
