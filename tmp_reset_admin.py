#!/usr/bin/env python
import os, secrets, string
from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine, text

# 生成强密码
alphabet = string.ascii_letters + string.digits + '!@#$%&*()-_=+[]{}:;?'
password = ''.join(secrets.choice(alphabet) for _ in range(16))
print('生成密码:', password)

db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print('未检测到 DATABASE_URL')
    raise SystemExit(1)

engine = create_engine(db_url)
with engine.connect() as conn:
    # 确保 department 存在
    res = conn.execute(text("SELECT id FROM department WHERE name = :name LIMIT 1"), {'name':'信息部'})
    row = res.fetchone()
    if row:
        dept_id = row[0]
    else:
        r = conn.execute(text("INSERT INTO department (name, code) VALUES (:name, :code) RETURNING id"), {'name':'信息部','code':'SYS'})
        dept_id = r.fetchone()[0]

    res = conn.execute(text("SELECT id FROM app_user WHERE username = :username"), {'username':'admin'})
    row = res.fetchone()
    pw_hash = generate_password_hash(password, method='pbkdf2:sha256')
    if row:
        conn.execute(text("UPDATE app_user SET password_hash = :pw WHERE id = :id"), {'pw': pw_hash, 'id': row[0]})
        print('管理员密码已更新（通过直接DB）。')
    else:
        conn.execute(text(
            "INSERT INTO app_user (username, email, password_hash, role, department_id, department, can_manage_equipment, can_manage_spare_parts, can_manage_repairs, can_manage_part_requests, can_view_workflow, can_view_reports, can_view_logs, is_active) "
            "VALUES (:username, :email, :pw, 'admin', :dept_id, :dept_name, true, true, true, true, true, true, true, true)"
        ), {'username':'admin','email':'admin@system.local','pw':pw_hash,'dept_id':dept_id,'dept_name':'信息部'})
        print('管理员账户创建成功（通过直接DB）！')

print('\n请记录下新密码（仅本次显示）:')
print(password)
