#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PostgreSQL配置向导

此脚本帮助你配置PostgreSQL数据库连接参数
"""

import os
import sys


def test_connection(host, port, user, password, database):
    """测试PostgreSQL连接"""
    try:
        import psycopg2
        conn_str = f"host={host} port={port} user={user} password={password} dbname={database}"
        conn = psycopg2.connect(conn_str)
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return True, version
    except ImportError:
        return False, "请先安装 psycopg2-binary: pip install psycopg2-binary"
    except Exception as e:
        return False, str(e)


def main():
    print("=" * 70)
    print(" PostgreSQL 数据库配置向导")
    print("=" * 70)
    print()
    
    # 检查PostgreSQL是否安装
    print("步骤1: 检查PostgreSQL安装")
    print("-" * 70)
    
    try:
        import psycopg2
        print("✓ psycopg2-binary 已安装")
    except ImportError:
        print("✗ psycopg2-binary 未安装")
        print()
        response = input("是否现在安装? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            os.system("pip install psycopg2-binary")
            print()
            print("安装完成,请重新运行此脚本")
            return
        else:
            print("请手动安装: pip install psycopg2-binary")
            return
    
    print()
    
    # 获取连接参数
    print("步骤2: 输入PostgreSQL连接参数")
    print("-" * 70)
    print("提示: 直接按回车使用默认值")
    print()
    
    host = input("主机地址 [localhost]: ").strip() or "localhost"
    port = input("端口号 [5432]: ").strip() or "5432"
    user = input("用户名 [postgres]: ").strip() or "postgres"
    
    # 密码输入
    import getpass
    password = getpass.getpass("密码: ").strip()
    if not password:
        print("警告: 密码为空,这可能导致连接失败")
    
    database = input("数据库名 [it_asset]: ").strip() or "it_asset"
    
    print()
    
    # 测试连接
    print("步骤3: 测试数据库连接")
    print("-" * 70)
    print(f"连接参数:")
    print(f"  主机: {host}:{port}")
    print(f"  用户: {user}")
    print(f"  数据库: {database}")
    print()
    print("正在连接...", end=" ")
    
    success, message = test_connection(host, port, user, password, database)
    
    if success:
        print("✓ 成功!")
        print()
        print(f"PostgreSQL版本: {message.split(',')[0]}")
        print()
        
        # 生成配置
        print("步骤4: 生成配置文件")
        print("-" * 70)
        
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        # 创建.env文件
        env_content = f"""# Flask应用配置
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development

# PostgreSQL数据库配置
DATABASE_URL={db_url}

# 可选配置
FALLBACK_ADMIN_EMAIL=admin@example.com

# 企业微信集成 (可选)
WEWORK_CORP_ID=
WEWORK_AGENT_ID=
WEWORK_SECRET=
WEWORK_ENABLED=false
"""
        
        env_file = ".env"
        
        # 检查是否已存在
        if os.path.exists(env_file):
            print(f"警告: {env_file} 文件已存在")
            response = input("是否覆盖? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("已取消,配置信息:")
                print()
                print(f"DATABASE_URL={db_url}")
                print()
                print("请手动添加到 .env 文件或 config.py")
                return
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✓ 已创建 {env_file} 文件")
        print()
        
        # 下一步提示
        print("步骤5: 数据迁移")
        print("-" * 70)
        print()
        print("配置完成! 接下来你可以:")
        print()
        print("1. 如果需要从SQLite迁移数据:")
        print("   python migrate_to_postgresql.py")
        print()
        print("2. 如果是新数据库,需要初始化表结构:")
        print("   flask db upgrade")
        print("   或")
        print("   python init_db.py")
        print()
        print("3. 启动应用:")
        print("   python app.py")
        print()
        
    else:
        print("✗ 失败!")
        print()
        print(f"错误信息: {message}")
        print()
        print("常见问题:")
        print()
        print("1. 密码错误")
        print("   - 确认PostgreSQL密码是否正确")
        print("   - 可能需要重置密码")
        print()
        print("2. 数据库不存在")
        print("   - 创建数据库: psql -U postgres -c \"CREATE DATABASE it_asset;\"")
        print()
        print("3. PostgreSQL未启动")
        print("   - Windows: 检查服务 'postgresql-x64-15'")
        print("   - 命令: Get-Service postgresql*")
        print()
        print("4. 连接被拒绝")
        print("   - 检查 pg_hba.conf 配置")
        print("   - 确保允许本地连接")
        print()
        
        response = input("是否重试? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            print()
            main()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("已取消")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
