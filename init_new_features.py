#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IT资产管理系统 - 新功能数据库初始化脚本
用于创建企业级功能所需的数据库表结构

使用方法:
    python init_new_features.py

或在Flask Shell中:
    from init_new_features import init_database
    init_database()
"""

import sys
from datetime import datetime
from app import create_app, db

def init_database():
    """初始化新功能表结构"""
    print("=" * 60)
    print("IT资产管理系统 - 数据库初始化")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            print("\n1️⃣ 创建数据库表...")
            
            # 导入新模型以创建表
            from app.models import AssetCost, AssetLifecycle, InventoryWarning, AssetHandover
            
            # 创建所有表
            db.create_all()
            print("   ✅ 表结构创建成功")
            
            # 显示创建的表
            from app.models import Equipment, SparePart
            print("\n2️⃣ 已创建的表:")
            print("   - equipment (已存在)")
            print("   - spare_part (已存在)")
            print("   - asset_cost (新)")
            print("   - asset_lifecycle (新)")
            print("   - inventory_warning (新)")
            print("   - asset_handover (新)")
            
            print("\n3️⃣ 初始化库存预警规则...")
            
            # 为现有配件添加默认预警规则
            spare_parts = SparePart.query.all()
            initialized_count = 0
            
            for spare_part in spare_parts:
                # 检查是否已有预警规则
                existing_warning = InventoryWarning.query.filter_by(
                    spare_part_id=spare_part.id
                ).first()
                
                if not existing_warning:
                    # 根据配件类型设置不同的阈值
                    if '电源' in spare_part.name or '电池' in spare_part.name:
                        min_threshold = 3
                        critical_threshold = 1
                        suggested_reorder = 50
                    elif '硬盘' in spare_part.name or '内存' in spare_part.name:
                        min_threshold = 5
                        critical_threshold = 2
                        suggested_reorder = 100
                    else:
                        min_threshold = 5
                        critical_threshold = 2
                        suggested_reorder = 100

                    warning = InventoryWarning(
                        spare_part_id=spare_part.id,
                        min_threshold=min_threshold,
                        critical_threshold=critical_threshold,
                        reorder_quantity=suggested_reorder // 2,
                        lead_time_days=7,
                        enabled=True,
                        last_warned_date=datetime.now()
                    )
                    db.session.add(warning)
                    initialized_count += 1
            
            if initialized_count > 0:
                db.session.commit()
                print(f"   ✅ 为 {initialized_count} 个配件创建了默认预警规则")
            else:
                print("   ℹ️ 所有配件已有预警规则")
            
            print("\n4️⃣ 初始化资产成本信息...")
            
            # 为现有资产添加成本信息 (仅当不存在时)
            equipments = Equipment.query.all()
            cost_initialized = 0
            
            for equipment in equipments:
                # AssetCost model uses `equipment_id` and fields like `purchase_price`,
                # `depreciation_rate`, `expected_lifespan`, `residual_value`, `maintenance_cost`.
                existing_cost = AssetCost.query.filter_by(
                    equipment_id=equipment.id
                ).first()

                equipment_price = getattr(equipment, 'price', None)

                if not existing_cost:
                    # 根据设备类型设置不同的折旧率（以小数形式）
                    if '电脑' in equipment.name or '笔记本' in equipment.name:
                        depreciation_rate = 0.18
                        lifespan = 4
                    elif '服务器' in equipment.name:
                        depreciation_rate = 0.12
                        lifespan = 6
                    elif '打印机' in equipment.name or '扫描仪' in equipment.name:
                        depreciation_rate = 0.20
                        lifespan = 5
                    else:
                        depreciation_rate = 0.15
                        lifespan = 5

                    purchase_price = float(equipment_price) if equipment_price else 0.0
                    residual_value = purchase_price * 0.10 if purchase_price else 0.0

                    cost = AssetCost(
                        equipment_id=equipment.id,
                        purchase_price=purchase_price,
                        purchase_date=equipment.purchase_date if hasattr(equipment, 'purchase_date') else None,
                        maintenance_cost=0.0,
                        depreciation_rate=depreciation_rate,
                        residual_value=residual_value,
                        expected_lifespan=lifespan
                    )
                    db.session.add(cost)
                    cost_initialized += 1
            
            if cost_initialized > 0:
                db.session.commit()
                print(f"   ✅ 为 {cost_initialized} 个资产创建了成本信息")
            else:
                print("   ℹ️ 所有资产已有成本信息")
            
            print("\n5️⃣ 数据库统计信息:")
            
            # 统计数据
            asset_count = Equipment.query.count()
            spare_part_count = SparePart.query.count()
            asset_cost_count = AssetCost.query.count()
            lifecycle_count = AssetLifecycle.query.count()
            warning_count = InventoryWarning.query.count()
            handover_count = AssetHandover.query.count()
            
            print(f"   - 资产总数: {asset_count}")
            print(f"   - 配件总数: {spare_part_count}")
            print(f"   - 已配置成本信息: {asset_cost_count}")
            print(f"   - 生命周期事件: {lifecycle_count}")
            print(f"   - 库存预警规则: {warning_count}")
            print(f"   - 交接记录: {handover_count}")
            
            print("\n" + "=" * 60)
            print("✅ 数据库初始化完成！")
            print("=" * 60)
            
            print("\n📌 后续建议:")
            print("   1. 手动更新资产的成本信息（采购价、折旧率等）")
            print("   2. 配置库存预警阈值（根据实际情况调整）")
            print("   3. 添加历史资产成本和生命周期数据")
            print("   4. 测试所有新功能（成本分析、库存预警、生命周期管理）")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def verify_database():
    """验证数据库表结构"""
    print("\n🔍 验证数据库结构...")
    
    app = create_app()
    
    with app.app_context():
        from app.models import AssetCost, AssetLifecycle, InventoryWarning, AssetHandover
        
        print("\n检查表结构完整性:")
        
        # 检查AssetCost
        try:
            cost = AssetCost.query.first()
            print("   ✅ asset_cost 表正常")
        except Exception as e:
            print(f"   ❌ asset_cost 表异常: {e}")
        
        # 检查AssetLifecycle
        try:
            lifecycle = AssetLifecycle.query.first()
            print("   ✅ asset_lifecycle 表正常")
        except Exception as e:
            print(f"   ❌ asset_lifecycle 表异常: {e}")
        
        # 检查InventoryWarning
        try:
            warning = InventoryWarning.query.first()
            print("   ✅ inventory_warning 表正常")
        except Exception as e:
            print(f"   ❌ inventory_warning 表异常: {e}")
        
        # 检查AssetHandover
        try:
            handover = AssetHandover.query.first()
            print("   ✅ asset_handover 表正常")
        except Exception as e:
            print(f"   ❌ asset_handover 表异常: {e}")

def cleanup_database():
    """清空新建表的数据（不删除表）"""
    print("\n🗑️ 清空新建表的数据...")
    
    app = create_app()
    
    with app.app_context():
        from app.models import AssetCost, AssetLifecycle, InventoryWarning, AssetHandover
        
        try:
            AssetCost.query.delete()
            AssetLifecycle.query.delete()
            InventoryWarning.query.delete()
            AssetHandover.query.delete()
            db.session.commit()
            print("   ✅ 数据清空成功")
        except Exception as e:
            print(f"   ❌ 清空失败: {e}")
            db.session.rollback()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='IT资产管理系统数据库初始化工具')
    parser.add_argument('--verify', action='store_true', help='验证数据库结构')
    parser.add_argument('--cleanup', action='store_true', help='清空新建表的数据')
    parser.add_argument('--init', action='store_true', help='初始化数据库（默认行为）')
    
    args = parser.parse_args()
    
    # 如果没有指定参数，默认执行初始化
    if not any([args.verify, args.cleanup, args.init]):
        args.init = True
    
    if args.init:
        success = init_database()
        sys.exit(0 if success else 1)
    
    if args.verify:
        verify_database()
    
    if args.cleanup:
        response = input("确认清空所有新建表的数据？(y/N): ")
        if response.lower() == 'y':
            cleanup_database()
        else:
            print("已取消")
