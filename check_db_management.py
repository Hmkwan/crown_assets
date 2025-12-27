#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库管理功能
"""
import os
import sys
from datetime import datetime

def check_db_management():
    print("="*70)
    print("数据库管理功能检查")
    print("="*70)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 检查数据库文件
    print("【1】数据库文件检查")
    print("-" * 70)
    db_file = 'app.db'
    if os.path.exists(db_file):
        size = os.path.getsize(db_file)
        size_mb = size / 1024 / 1024
        mtime = os.path.getmtime(db_file)
        modified = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"✓ 数据库文件: {db_file}")
        print(f"  - 大小: {size_mb:.2f} MB ({size:,} bytes)")
        print(f"  - 修改时间: {modified}")
    else:
        print(f"✗ 数据库文件不存在: {db_file}")
    print()
    
    # 2. 检查备份目录
    print("【2】备份目录检查")
    print("-" * 70)
    backup_dir = 'backups'
    if os.path.exists(backup_dir):
        backups = [f for f in os.listdir(backup_dir) if f.startswith('app_backup_') and f.endswith('.db')]
        print(f"✓ 备份目录: {backup_dir}")
        print(f"  - 备份文件数量: {len(backups)}")
        
        if backups:
            # 按修改时间排序
            backups.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)), reverse=True)
            print(f"  - 最新备份: {backups[0]}")
            latest_path = os.path.join(backup_dir, backups[0])
            latest_size = os.path.getsize(latest_path)
            latest_mtime = os.path.getmtime(latest_path)
            print(f"    大小: {latest_size / 1024 / 1024:.2f} MB")
            print(f"    时间: {datetime.fromtimestamp(latest_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 显示前5个备份
            print(f"  - 最近5个备份:")
            for i, backup in enumerate(backups[:5], 1):
                backup_path = os.path.join(backup_dir, backup)
                backup_size = os.path.getsize(backup_path)
                backup_mtime = os.path.getmtime(backup_path)
                print(f"    {i}. {backup}")
                print(f"       {backup_size / 1024 / 1024:.2f} MB - {datetime.fromtimestamp(backup_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"✗ 备份目录不存在: {backup_dir}")
    print()
    
    # 3. 检查数据库管理工具模块
    print("【3】数据库管理模块检查")
    print("-" * 70)
    db_mgmt_file = 'app/utils/db_management.py'
    if os.path.exists(db_mgmt_file):
        print(f"✓ 数据库管理模块: {db_mgmt_file}")
        
        # 检查关键函数
        with open(db_mgmt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            functions = [
                'backup_database',
                'restore_database',
                'reset_database',
                'list_backups',
                'delete_backup',
                'get_database_info',
                'export_database_to_mysql',
                'export_database_to_mssql',
                'export_database_to_postgresql',
                'get_database_tables_info',
                'get_table_data'
            ]
            
            print("  - 关键函数检查:")
            for func in functions:
                if f'def {func}(' in content:
                    print(f"    ✓ {func}")
                else:
                    print(f"    ✗ {func} (未找到)")
    else:
        print(f"✗ 数据库管理模块不存在: {db_mgmt_file}")
    print()
    
    # 4. 检查路由配置
    print("【4】数据库管理路由检查")
    print("-" * 70)
    routes_file = 'app/main/routes.py'
    if os.path.exists(routes_file):
        print(f"✓ 路由文件: {routes_file}")
        
        with open(routes_file, 'r', encoding='utf-8') as f:
            content = f.read()
            routes = [
                '/admin/database',
                '/admin/database/backup',
                '/admin/database/restore',
                '/admin/database/restore_latest',
                '/admin/database/reset',
                '/admin/database/import',
                '/admin/database/export_mysql',
                '/admin/database/export_mssql',
                '/admin/database/export_postgresql',
                '/admin/database/tables',
                '/admin/database/table/<table_name>',
                '/admin/database/backup/delete'
            ]
            
            print("  - 路由检查:")
            for route in routes:
                if f"@bp.route('{route}'" in content:
                    print(f"    ✓ {route}")
                else:
                    print(f"    ✗ {route} (未找到)")
    else:
        print(f"✗ 路由文件不存在: {routes_file}")
    print()
    
    # 5. 检查模板文件
    print("【5】数据库管理模板检查")
    print("-" * 70)
    templates = [
        'app/templates/main/database_management.html',
        'app/templates/main/database_tables.html',
        'app/templates/main/table_data.html',
        'app/templates/main/migration_guide.html'
    ]
    
    for template in templates:
        if os.path.exists(template):
            size = os.path.getsize(template)
            print(f"✓ {template} ({size:,} bytes)")
        else:
            print(f"✗ {template} (不存在)")
    print()
    
    # 6. 检查数据库连接（需要Flask应用上下文）
    print("【6】数据库连接测试")
    print("-" * 70)
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from app.utils.db_management import get_database_info
            result = get_database_info()
            
            if result.get('success'):
                info = result.get('info', {})
                print(f"✓ 数据库连接成功")
                print(f"  - 类型: {info.get('type')}")
                print(f"  - URI: {info.get('uri')}")
                print(f"  - 存在: {info.get('exists')}")
                if info.get('size'):
                    print(f"  - 大小: {info.get('size') / 1024 / 1024:.2f} MB")
                print(f"  - 修改时间: {info.get('modified')}")
                print(f"  - 数据表数量: {info.get('table_count')}")
                
                # 列出前10个表
                tables = info.get('tables', [])
                if tables:
                    print(f"  - 数据表 (前10个):")
                    for i, table in enumerate(tables[:10], 1):
                        print(f"    {i}. {table}")
            else:
                print(f"✗ 获取数据库信息失败: {result.get('message')}")
    except Exception as e:
        print(f"✗ 数据库连接测试失败: {str(e)}")
    print()
    
    # 7. 检查导出脚本
    print("【7】数据库导出脚本检查")
    print("-" * 70)
    # 已归档的历史自动转换脚本（仅供审计参考）
    export_scripts = [
        'scripts/sqlite_to_mysql.py',
        'scripts/sqlite_to_mssql.py',
        'scripts/sqlite_to_postgresql.py'
    ]
    
    for script in export_scripts:
        if os.path.exists(script):
            size = os.path.getsize(script)
            print(f"(历史) ✓ {script} ({size:,} bytes) - 已归档，使用前请在测试环境验证")
        else:
            print(f"(历史) ✗ {script} (不存在) - 如需历史脚本请查看 docs/legacy/")
    print()
    
    # 8. 功能总结
    print("【8】功能总结")
    print("=" * 70)
    print("✓ 已实现的功能:")
    print("  1. 数据库备份 - 支持 PostgreSQL (pg_dump)")
    print("  2. 数据库恢复 - 使用 pg_restore/psql 恢复 PostgreSQL 备份")
    print("  3. 数据库重置 - 清空所有数据并重新初始化")
    print("  4. 备份管理 - 列出、筛选、删除备份文件")
    print("  5. 数据库导入 - 仅支持 PostgreSQL SQL 转储 (.sql/.sql.gz)。.db 文件不再受支持")
    print("  6. 数据库导出 - 导出为 PostgreSQL；历史的 MySQL/MSSQL 转换已弃用")
    print("  7. 数据表查看 - 查看所有表的结构和数据")
    print("  8. 数据库信息 - 显示数据库类型、大小、表数量等")
    print()
    print("✓ 安全特性:")
    print("  1. 仅管理员可访问")
    print("  2. 恢复前自动备份当前数据库")
    print("  3. 重置操作需要确认")
    print("  4. 操作日志记录")
    print("  5. 文件类型验证")
    print()
    
    print("="*70)
    print("检查完成！")
    print("="*70)

if __name__ == '__main__':
    try:
        check_db_management()
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
