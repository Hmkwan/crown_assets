#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQLite数据迁移到PostgreSQL脚本

使用方法:
1. 确保PostgreSQL数据库 'it_asset' 已创建
2. 安装依赖: pip install psycopg2-binary
3. 修改下面的数据库连接参数
4. 运行: python migrate_to_postgresql.py

注意事项:
- 此脚本会将SQLite中的所有数据迁移到PostgreSQL
- PostgreSQL数据库需要先创建好
- 建议先在测试环境运行
"""

import os
import sys
from datetime import datetime

# SQLite配置
SQLITE_DB = os.path.join(os.path.dirname(__file__), 'app.db')

# PostgreSQL配置 - 从.env文件或环境变量读取
def load_env():
    """加载.env文件中的环境变量"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# 从环境变量获取DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL', '')

if DATABASE_URL and DATABASE_URL.startswith('postgresql'):
    # 解析DATABASE_URL: postgresql://user:password@host:port/database
    try:
        from urllib.parse import urlparse
        parsed = urlparse(DATABASE_URL)
        PG_HOST = parsed.hostname or 'localhost'
        PG_PORT = str(parsed.port or 5432)
        PG_USER = parsed.username or 'postgres'
        PG_PASSWORD = parsed.password or ''
        PG_DATABASE = parsed.path.lstrip('/') or 'it_asset'
    except:
        # 解析失败,使用默认值
        PG_HOST = 'localhost'
        PG_PORT = '5432'
        PG_USER = 'postgres'
        PG_PASSWORD = ''
        PG_DATABASE = 'it_asset'
else:
    # 使用默认值
    PG_HOST = 'localhost'
    PG_PORT = '5432'
    PG_USER = 'postgres'
    PG_PASSWORD = ''
    PG_DATABASE = 'it_asset'


def migrate_sqlite_to_postgresql():
    """迁移SQLite数据到PostgreSQL"""
    print("=" * 60)
    print("SQLite -> PostgreSQL 数据迁移工具")
    print("=" * 60)
    print()
    
    # 检查SQLite数据库是否存在
    if not os.path.exists(SQLITE_DB):
        print(f"错误: SQLite数据库文件不存在: {SQLITE_DB}")
        print("请确保app.db文件存在")
        return False
    
    print(f"✓ 找到SQLite数据库: {SQLITE_DB}")
    
    # 导入必要的库
    try:
        from sqlalchemy import create_engine, MetaData, Table, inspect
        from sqlalchemy.orm import sessionmaker
        import psycopg2
    except ImportError as e:
        print(f"错误: 缺少必要的Python包: {e}")
        print("请运行: pip install psycopg2-binary sqlalchemy")
        return False
    
    print("✓ 依赖包检查通过")
    
    # 测试PostgreSQL连接
    print()
    print("测试PostgreSQL连接...")
    pg_url = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
    
    try:
        from sqlalchemy import create_engine, MetaData, Table, inspect, text
        pg_engine = create_engine(pg_url)
        with pg_engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✓ PostgreSQL连接成功")
            print(f"  版本: {version.split(',')[0]}")
    except Exception as e:
        print(f"✗ PostgreSQL连接失败: {e}")
        print()
        print("请检查:")
        print(f"  1. PostgreSQL服务是否运行")
        print(f"  2. 数据库 '{PG_DATABASE}' 是否已创建")
        print(f"  3. 用户名密码是否正确: {PG_USER}")
        print(f"  4. 主机端口是否正确: {PG_HOST}:{PG_PORT}")
        print()
        print("创建数据库命令:")
        print(f"  psql -U {PG_USER} -c \"CREATE DATABASE {PG_DATABASE};\"")
        return False
    
    # 连接SQLite
    print()
    print("连接SQLite数据库...")
    sqlite_url = f"sqlite:///{SQLITE_DB}"
    sqlite_engine = create_engine(sqlite_url)
    
    # 获取表信息
    print()
    print("分析数据库结构...")
    inspector = inspect(sqlite_engine)
    tables = inspector.get_table_names()
    
    print(f"✓ 找到 {len(tables)} 个表:")
    for table in tables:
        with sqlite_engine.connect() as conn:
            row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()[0]
        print(f"  - {table}: {row_count} 条记录")
    
    if not tables:
        print("警告: SQLite数据库中没有表,可能需要先运行 flask db upgrade")
        return False
    
    # 确认迁移
    print()
    response = input("是否继续迁移? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("迁移已取消")
        return False
    
    # 创建PostgreSQL表结构
    print()
    print("创建PostgreSQL表结构...")
    
    # 设置临时环境变量使用PostgreSQL
    original_db_url = os.environ.get('DATABASE_URL')
    os.environ['DATABASE_URL'] = pg_url
    
    try:
        # 导入Flask应用以创建表
        from app import create_app, db
        app = create_app()
        
        with app.app_context():
            print("  删除现有表...")
            db.drop_all()
            print("  创建新表...")
            db.create_all()
            print("✓ 表结构创建完成")
    except Exception as e:
        print(f"✗ 创建表结构失败: {e}")
        if original_db_url:
            os.environ['DATABASE_URL'] = original_db_url
        else:
            os.environ.pop('DATABASE_URL', None)
        return False
    
    # 迁移数据
    print()
    print("开始迁移数据...")
    
    metadata = MetaData()
    metadata.reflect(bind=sqlite_engine)
    
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    PGSession = sessionmaker(bind=pg_engine)
    
    sqlite_session = SQLiteSession()
    pg_session = PGSession()
    
    total_rows = 0
    failed_tables = []
    
    for table_name in tables:
        try:
            print(f"  迁移表: {table_name}...", end=" ")
            
            # 从SQLite读取数据
            table = Table(table_name, metadata, autoload_with=sqlite_engine)
            sqlite_data = sqlite_session.execute(table.select()).fetchall()
            
            if not sqlite_data:
                print("(空表)")
                continue
            
            # 插入到PostgreSQL
            pg_table = Table(table_name, MetaData(), autoload_with=pg_engine)
            
            # 批量插入
            batch_size = 1000
            for i in range(0, len(sqlite_data), batch_size):
                batch = sqlite_data[i:i + batch_size]
                insert_data = [dict(row._mapping) for row in batch]
                pg_session.execute(pg_table.insert(), insert_data)
                pg_session.commit()
            
            total_rows += len(sqlite_data)
            print(f"✓ {len(sqlite_data)} 条")
            
        except Exception as e:
            print(f"✗ 失败: {e}")
            failed_tables.append((table_name, str(e)))
            pg_session.rollback()
    
    sqlite_session.close()
    pg_session.close()
    
    # 恢复原始环境变量
    if original_db_url:
        os.environ['DATABASE_URL'] = original_db_url
    else:
        os.environ.pop('DATABASE_URL', None)
    
    # 输出迁移结果
    print()
    print("=" * 60)
    print("迁移完成!")
    print("=" * 60)
    print(f"总共迁移: {total_rows} 条记录")
    print(f"成功表数: {len(tables) - len(failed_tables)}/{len(tables)}")
    
    if failed_tables:
        print()
        print("失败的表:")
        for table_name, error in failed_tables:
            print(f"  - {table_name}: {error}")
    
    print()
    print("后续步骤:")
    print("1. 修改 config.py 中的数据库配置为PostgreSQL")
    print("2. 或创建 .env 文件设置 DATABASE_URL")
    print(f"   DATABASE_URL={pg_url}")
    print("3. 重启Flask应用")
    print()
    
    return len(failed_tables) == 0


if __name__ == '__main__':
    print()
    print("PostgreSQL数据库迁移向导")
    print()
    print("当前配置:")
    print(f"  SQLite数据库: {SQLITE_DB}")
    print(f"  PostgreSQL主机: {PG_HOST}:{PG_PORT}")
    print(f"  PostgreSQL数据库: {PG_DATABASE}")
    print(f"  PostgreSQL用户: {PG_USER}")
    print()
    print("如需修改配置,请编辑此脚本文件顶部的配置变量")
    print()
    
    success = migrate_sqlite_to_postgresql()
    
    if success:
        print("✓ 迁移成功完成!")
        sys.exit(0)
    else:
        print("✗ 迁移过程中遇到错误")
        sys.exit(1)
