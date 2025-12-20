#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""创建/重置管理员账户脚本（更安全）

改动说明:
- 优先使用命令行参数或环境变量提供密码 (`--password` 或 ADMIN_PASSWORD)
- 在交互式终端下，会提示输入密码并要求确认
- 如果在非交互式环境且未提供密码，会自动生成一个强随机密码并打印出来
- 默认不会在已有管理员上无交互地重置密码，除非使用 `--force`
"""

from __future__ import annotations

import argparse
import os
import sys
import secrets
import string
from getpass import getpass

# 延迟导入 (`app` / `app.models`)，避免在模块导入时触发 create_app() 中的副作用
# 将在 main() 中按需加载


def _generate_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%&*()-_=+[]{}:;?"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def _ask_password_interactive(prompt: str = 'Password: ') -> str:
    for _ in range(3):
        pw = getpass(prompt)
        if not pw:
            print('密码不能为空，请重试。')
            continue
        pw2 = getpass('再次输入以确认: ')
        if pw != pw2:
            print('两次输入的密码不一致，请重试。')
            continue
        return pw
    raise SystemExit('连续多次密码输入失败，终止。')


def main() -> None:
    parser = argparse.ArgumentParser(description='创建或重置管理员账号（更安全）')
    parser.add_argument('--force', '-f', action='store_true', help='若管理员已存在，则强制重置密码（无提示）')
    parser.add_argument('--password', '-p', help='指定管理员密码（不安全：避免在共享 shell 中使用）')
    args = parser.parse_args()

    # 优先级: CLI arg > 环境变量 > 交互式输入 > 自动生成
    given_pw = args.password or os.environ.get('ADMIN_PASSWORD')

    # 为避免在脚本执行时因 SocketIO/Redis 重试导致阻塞，临时跳过 SocketIO 初始化
    os.environ.setdefault('SKIP_SOCKETIO_INIT', '1')

    # 若使用 --force，则直接采用数据库回退路径，避免应用导入/蓝图引起的阻塞或导入错误
    if args.force:
        print('使用 --force 标志，直接采用数据库回退路径（跳过 create_app 调用）。')
    else:
        # 尝试以应用方式创建（首选）；如果 import/create_app 失败（模型导入循环或定义冲突），
        # 回退到直接使用数据库进行 upsert（更保守且更可靠，在运维脚本中常用）。
        try:
            # 延迟导入 create_app 和 模型，确保 SKIP_SOCKETIO_INIT 在 create_app() 之前生效
            from app import create_app, db
            from app.models import User, Department

            app = create_app()
            with app.app_context():
                # 检查或创建默认部门
                dept = Department.query.first()
                if not dept:
                    print('创建默认部门...')
                    dept = Department(name='信息部', code='SYS')
                    db.session.add(dept)
                    db.session.flush()
                else:
                    print(f'使用现有部门: {dept.name}')

                admin = User.query.filter_by(username='admin').first()
                # 使用 ORM 路径完成创建/重置
                if admin and not args.force:
                    try:
                        if sys.stdin.isatty():
                            resp = input("管理员 'admin' 已存在，是否要重置密码？ [y/N]: ")
                            if resp.strip().lower() not in ('y', 'yes'):
                                print('取消操作，未更改管理员密码。')
                                return
                        else:
                            print("管理员已存在，未在非交互环境中进行更改（使用 --force 强制重置）。")
                            return
                    except (KeyboardInterrupt, EOFError):
                        print('\n取消操作')
                        return

                # 获取或生成密码
                if given_pw:
                    password = given_pw
                else:
                    if sys.stdin.isatty():
                        password = _ask_password_interactive()
                    else:
                        password = _generate_password()
                        print('未提供密码，已自动生成强随机密码（请记录）：')

                # 应用变更（ORM）
                if admin:
                    admin.set_password(password)
                    db.session.commit()
                    print("管理员 'admin' 的密码已更新。")
                else:
                    print('创建管理员账户...')
                    admin = User(
                        username='admin',
                        email='admin@system.local',
                        role='admin',
                        department_id=dept.id,
                        department=dept.name,
                        can_manage_equipment=True,
                        can_manage_spare_parts=True,
                        can_manage_repairs=True,
                        can_manage_part_requests=True,
                        can_view_workflow=True,
                        can_view_reports=True,
                        can_view_logs=True,
                    )
                    admin.set_password(password)
                    db.session.add(admin)
                    db.session.commit()
                    print('✓ 管理员账户创建成功！')

                # 输出凭证
                print('\n登录凭证:')
                print('  用户名: admin')
                if given_pw:
                    print('  密码: (已设置，未在此输出以减少泄露风险)')
                    print('  提示：若需要查看或记录密码，请在安全的终端上使用 --password 或设置 ADMIN_PASSWORD 环境变量。')
                else:
                    print(f'  密码: {password}')
                return
        except Exception as e:
            print('应用方式创建/重置管理员失败，将尝试回退到直接数据库方式。错误信息:', e)

    # 回退：直接连接数据库并执行 upsert（避免加载 app 或 blueprint 导致的导入/循环依赖问题）
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('未设置 DATABASE_URL，无法回退到直接数据库模式，请先配置环境变量或修复应用导入问题。')
        return

    # 构造密码 hash
    try:
        from werkzeug.security import generate_password_hash
    except Exception:
        # werkzeug 可能不可用，尝试从项目依赖导入（再抛则会失败）
        from werkzeug.security import generate_password_hash

    password = given_pw or ( _generate_password() if not sys.stdin.isatty() else _ask_password_interactive() )

    # 使用 sqlalchemy 直接执行 SQL
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # 确保 department 存在
            res = conn.execute(text("SELECT id, name FROM department WHERE name = :name LIMIT 1"), {'name': '信息部'})
            row = res.fetchone()
            if row:
                dept_id = row[0]
            else:
                r = conn.execute(text("INSERT INTO department (name, code) VALUES (:name, :code) RETURNING id"), {'name': '信息部', 'code': 'SYS'})
                dept_id = r.fetchone()[0]

            # 检查 admin
            res = conn.execute(text("SELECT id FROM app_user WHERE username = :username"), {'username': 'admin'})
            row = res.fetchone()
            pw_hash = generate_password_hash(password, method='pbkdf2:sha256')
            if row:
                conn.execute(text("UPDATE app_user SET password_hash = :pw WHERE id = :id"), {'pw': pw_hash, 'id': row[0]})
                print("管理员 'admin' 的密码已更新（通过直接DB）。")
            else:
                conn.execute(text(
                    "INSERT INTO app_user (username, email, password_hash, role, department_id, department, can_manage_equipment, can_manage_spare_parts, can_manage_repairs, can_manage_part_requests, can_view_workflow, can_view_reports, can_view_logs, is_active) "
                    "VALUES (:username, :email, :pw, 'admin', :dept_id, :dept_name, true, true, true, true, true, true, true, true)"
                ), {'username': 'admin', 'email': 'admin@system.local', 'pw': pw_hash, 'dept_id': dept_id, 'dept_name': '信息部'})
                print('✓ 管理员账户创建成功（通过直接DB）！')

            # 输出凭证
            print('\n登录凭证:')
            print('  用户名: admin')
            if given_pw:
                print('  密码: (已设置，未在此输出以减少泄露风险)')
            else:
                print(f'  密码: {password}')
            return
    except Exception as e:
        print('直接数据库回退模式失败，错误信息:', e)
        return


if __name__ == '__main__':
    main()
    
