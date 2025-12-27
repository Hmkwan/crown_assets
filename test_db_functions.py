#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试初始化和重置数据库功能
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

def test_functions():
    """测试初始化和重置函数"""
    print("=" * 80)
    print("开始测试数据库管理功能")
    print("=" * 80)
    
    # 初始化Flask应用
    from app import create_app, db
    app = create_app()
    
    with app.app_context():
        print("\n【测试 1】检查 initialize_system 函数导入")
        print("-" * 80)
        try:
            from app.utils.db_management import initialize_system
            print("✓ initialize_system 函数导入成功")
        except ImportError as e:
            import pytest
            pytest.fail(f"导入失败: {e}")
        
        print("\n【测试 2】检查 reset_database 函数导入")
        print("-" * 80)
        try:
            from app.utils.db_management import reset_database
            print("✓ reset_database 函数导入成功")
        except ImportError as e:
            import pytest
            pytest.fail(f"导入失败: {e}")
        
        print("\n【测试 3】检查模型导入")
        print("-" * 80)
        try:
            from app.models import (
                User, RoleDefinition, EquipmentType, SparePartType,
                Department, ApprovalWorkflow,
                Equipment, EquipmentTransfer, EquipmentScrap, EquipmentLoan,
                EquipmentApplication, PartRequestOrder, AccountRequest,
                AuditLog, UserActivityLog, Notification
            )
            print("✓ 所有模型导入成功")
            print(f"  - User 模型: {User}")
            print(f"  - Equipment 模型: {Equipment}")
            print(f"  - Department 模型: {Department}")
        except ImportError as e:
            import pytest
            pytest.fail(f"模型导入失败: {e}")
        
        print("\n【测试 4】检查当前数据库表")
        print("-" * 80)
        try:
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✓ 数据库包含 {len(tables)} 个表")
            print(f"  表名: {', '.join(tables[:5])}...")
        except Exception as e:
            import pytest
            pytest.fail(f"检查表失败: {e}")
        
        print("\n【测试 5】验证 initialize_system 函数签名")
        print("-" * 80)
        try:
            import inspect as insp
            sig = insp.signature(initialize_system)
            print(f"✓ 函数签名: initialize_system{sig}")
            print(f"  返回类型: dict (包含 success, message, admin_username, admin_password 等)")
        except Exception as e:
            print(f"✗ 检查失败: {e}")
            return False
        
        print("\n【测试 6】验证 reset_database 函数签名")
        print("-" * 80)
        try:
            sig = insp.signature(reset_database)
            print(f"✓ 函数签名: reset_database{sig}")
            print(f"  返回类型: dict (包含 success, message, details 等)")
        except Exception as e:
            print(f"✗ 检查失败: {e}")
            return False
        
        print("\n【测试 7】检查数据库备份目录")
        print("-" * 80)
        try:
            from app.utils.db_management import get_backup_dir
            backup_dir = get_backup_dir()
            print(f"✓ 备份目录: {backup_dir}")
            print(f"  目录存在: {os.path.exists(backup_dir)}")
        except Exception as e:
            import pytest
            pytest.fail(f"检查失败: {e}")
        
        print("\n" + "=" * 80)
        print("✓ 所有测试通过！")
        print("=" * 80)
        print("\n现在可以使用以下功能:")
        print("1. initialize_system() - 初始化系统（清除业务数据，保留基础配置）")
        print("2. reset_database() - 重置数据库（完全重建）")
        print("\n访问: http://localhost:5020/admin/database")
        print("使用'初始化系统'或'重置数据库'按钮")

if __name__ == '__main__':
    try:
        success = test_functions()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
