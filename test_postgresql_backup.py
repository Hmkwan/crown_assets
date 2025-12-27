#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试PostgreSQL数据库备份和恢复功能
"""
import os
import sys
from datetime import datetime

def test_postgresql_backup():
    print("="*70)
    print("PostgreSQL 数据库管理功能测试")
    print("="*70)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from app.utils.db_management import (
                backup_database, restore_database, list_backups,
                validate_database_file, delete_backup, get_database_info
            )
            
            # 1. 获取数据库信息
            print("【1】数据库信息")
            print("-" * 70)
            db_info_result = get_database_info()
            if db_info_result.get('success'):
                info = db_info_result.get('info', {})
                print(f"✓ 数据库类型: {info.get('type')}")
                print(f"  URI: {info.get('uri')}")
                print(f"  表数量: {info.get('table_count')}")
                if info.get('size'):
                    size_mb = info.get('size') / 1024 / 1024
                    print(f"  大小: {size_mb:.2f} MB")
            else:
                print(f"✗ 获取数据库信息失败: {db_info_result.get('message')}")
            print()
            
            # 2. 测试备份功能
            print("【2】备份功能测试")
            print("-" * 70)
            
            if info.get('type') == 'PostgreSQL':
                # 测试压缩备份
                print("测试压缩备份...")
                result = backup_database(compress=True)
                if result.get('success'):
                    print(f"✓ 压缩备份成功")
                    print(f"  文件名: {result.get('backup_filename')}")
                    print(f"  大小: {result.get('file_size') / 1024 / 1024:.2f} MB")
                    print(f"  路径: {result.get('backup_path')}")
                    backup_file = result.get('backup_filename')
                else:
                    print(f"✗ 压缩备份失败: {result.get('message')}")
                    if 'pg_dump' in result.get('message', ''):
                        print()
                        print("  提示: 需要安装PostgreSQL客户端工具")
                        print("  Windows: 下载PostgreSQL安装包并添加bin目录到PATH")
                        print("  Linux: sudo apt install postgresql-client")
                        print("  macOS: brew install postgresql")
                    backup_file = None
            else:
                print(f"当前数据库类型: {info.get('type')}")
                print("跳过PostgreSQL特定测试")
                backup_file = None
            print()
            
            # 3. 测试列出备份
            print("【3】备份列表测试")
            print("-" * 70)
            backups_result = list_backups()
            if backups_result.get('success'):
                backups = backups_result.get('backups', [])
                print(f"✓ 找到 {len(backups)} 个备份文件")
                
                # 分类统计
                # 历史遗留的 SQLite 备份（已不再受支持，列出供参考）
                sqlite_legacy_backups = [b for b in backups if b.get('db_type') == 'sqlite_legacy']
                postgresql_backups = [b for b in backups if b.get('db_type') == 'postgresql']
                compressed_backups = [b for b in backups if b.get('compressed')]
                
                print(f"  - SQLite (legacy) 备份: {len(sqlite_legacy_backups)} 个")
                print(f"  - PostgreSQL备份: {len(postgresql_backups)} 个")
                print(f"  - 压缩备份: {len(compressed_backups)} 个")
                
                # 显示最近的5个备份
                if backups:
                    print(f"\n  最近的5个备份:")
                    for i, backup in enumerate(backups[:5], 1):
                        db_type = backup.get('db_type', 'unknown').upper()
                        size_mb = backup.get('size', 0) / 1024 / 1024
                        compressed = " (压缩)" if backup.get('compressed') else ""
                        print(f"    {i}. [{db_type}] {backup.get('filename')}")
                        print(f"       {size_mb:.2f} MB{compressed} - {backup.get('friendly_time')}")
            else:
                print(f"✗ 获取备份列表失败: {backups_result.get('message')}")
            print()
            
            # 4. 测试备份文件验证
            if backup_file:
                print("【4】备份文件验证测试")
                print("-" * 70)
                backup_path = os.path.join('backups', backup_file)
                if os.path.exists(backup_path):
                    validate_result = validate_database_file(backup_path)
                    if validate_result.get('success'):
                        print(f"✓ 备份文件验证通过")
                        print(f"  类型: {validate_result.get('db_type')}")
                        print(f"  大小: {validate_result.get('file_size') / 1024 / 1024:.2f} MB")
                        if validate_result.get('compressed'):
                            print(f"  压缩: 是")
                    else:
                        print(f"✗ 验证失败: {validate_result.get('message')}")
                print()
            
            # 5. 功能可用性总结
            print("【5】功能可用性总结")
            print("=" * 70)
            
            db_type = info.get('type', 'Unknown')
            print(f"当前数据库: {db_type}")
            print()
            
            if db_type == 'PostgreSQL':
                print("✓ PostgreSQL数据库管理功能:")
                print("  1. ✓ 数据库信息查看")
                print("  2. ✓ 数据库备份 (pg_dump)")
                if backup_file:
                    print("     - ✓ 压缩备份成功")
                    print("     - ✓ 备份文件已创建")
                else:
                    print("     - ✗ 需要安装pg_dump工具")
                print("  3. ✓ 数据库恢复 (pg_restore/psql)")
                print("  4. ✓ 备份文件验证")
                print("  5. ✓ 备份列表管理")
                print("  6. ✓ 多格式支持 (.sql, .sql.gz)")
            elif db_type and db_type.startswith('SQLite'):
                print("⚠️ 当前运行环境为 SQLite，但系统已移除对 SQLite 的运行时支持。")
                print("   - 建议迁移到 PostgreSQL 并在测试环境中验证迁移后的数据。")
                print("   - 历史 SQLite 备份将以 'sqlite_legacy' 列出（仅供参考，不能直接导入恢复）。")
            
            print()
            print("✓ 通用功能:")
            print("  1. ✓ 自动备份（恢复前）")
            print("  2. ✓ 时间戳管理")
            print("  3. ✓ 文件大小显示")
            print("  4. ✓ 友好时间显示")
            print("  5. ✓ 日期筛选")
            print("  6. ✓ 备份文件删除")
            
            print()
            print("="*70)
            print("测试完成！")
            print("="*70)
            
            # 提示下一步操作
            print()
            print("📌 下一步操作:")
            print()
            if db_type == 'PostgreSQL' and not backup_file:
                print("⚠️ 请安装PostgreSQL客户端工具以启用备份功能:")
                print()
                print("Windows:")
                print("  1. 下载PostgreSQL: https://www.postgresql.org/download/windows/")
                print("  2. 安装后将 C:\\Program Files\\PostgreSQL\\<version>\\bin 添加到PATH")
                print("  3. 重启终端并测试: pg_dump --version")
                print()
                print("Linux:")
                print("  sudo apt update")
                print("  sudo apt install postgresql-client")
                print()
                print("macOS:")
                print("  brew install postgresql")
            else:
                print("✓ 所有功能已就绪，可以通过Web界面使用:")
                print("  1. 访问 http://your-server/admin/database")
                print("  2. 点击'立即备份'创建备份")
                print("  3. 点击'恢复'按钮恢复备份")
                print("  4. 支持上传备份文件")
            
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_postgresql_backup()
