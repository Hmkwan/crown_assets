#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化PostgreSQL数据库表结构
"""

from app import create_app, db

print("正在初始化PostgreSQL数据库...")
print()

app = create_app()

with app.app_context():
    # 显示连接信息
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if 'postgresql' in db_uri:
        # 隐藏密码
        parts = db_uri.split('@')
        if len(parts) == 2:
            display_uri = f"postgresql://***@{parts[1]}"
        else:
            display_uri = "postgresql://***"
        print(f"数据库: {display_uri}")
    else:
        print(f"数据库: {db_uri}")
    
    print()
    print("创建所有表...")
    
    # 创建所有表
    db.create_all()
    
    # 获取创建的表列表
    tables = sorted(db.metadata.tables.keys())
    
    print()
    print(f"✓ 成功创建 {len(tables)} 个表:")
    print()
    
    for i, table in enumerate(tables, 1):
        print(f"  {i:2}. {table}")
    
    print()
    print("数据库初始化完成!")
    print()
    print("下一步:")
    print("  1. 运行 python init_system_data.py 初始化系统数据")
    print("  2. 运行 python create_admin.py 创建管理员账户")
    print("  3. 运行 python app.py 启动应用")
