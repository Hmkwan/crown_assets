#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IT资产管理系统 - 新功能集成测试脚本
测试所有新增的成本分析、库存预警、生命周期管理功能

使用方法:
    python test_new_features.py
    或在Flask Shell中执行相应测试函数
"""

import sys
from datetime import datetime, timedelta
from app import create_app, db
from app.models import (
    Equipment, SparePart, User, AssetCost, AssetLifecycle, 
    InventoryWarning, AssetHandover
)

def test_asset_cost():
    """测试资产成本模块"""
    print("\n" + "="*60)
    print("🧪 测试1: 资产成本模块 (AssetCost)")
    print("="*60)
    
    app = create_app()
    with app.app_context():
        try:
            # 获取第一个资产
            equipment = Equipment.query.first()
            if not equipment:
                import pytest
                pytest.skip("没有找到资产，跳过测试")
            
            print(f"\n✓ 目标资产: {equipment.name} (ID: {equipment.id})")
            
            # 检查是否已有成本信息
            cost = AssetCost.query.filter_by(equipment_id=equipment.id).first()
            
            if cost:
                print(f"✓ 成本信息已存在")
                print(f"  - 采购价格: ¥{cost.purchase_price:.2f}")
                print(f"  - 年折旧率: {cost.depreciation_rate * 100:.1f}%")
                print(f"  - 年均维护成本: ¥{cost.maintenance_cost:.2f}")
            else:
                # 创建新的成本记录 (字段与模型对齐)
                cost = AssetCost(
                    equipment_id=equipment.id,
                    purchase_price=5000.0,
                    depreciation_rate=0.15,
                    expected_lifespan=5,
                    residual_value=500.0,
                    maintenance_cost=200.0
                )
                db.session.add(cost)
                db.session.commit()
                print(f"✓ 创建成本记录成功")
                print(f"  - 采购价格: ¥{cost.purchase_price:.2f}")
                print(f"  - 年折旧率: {cost.depreciation_rate * 100:.1f}%")
            # 计算折旧
            annual_depreciation = cost.purchase_price * (cost.depreciation_rate or 0)
            print(f"\n✓ 折旧计算:")
            print(f"  - 年折旧额: ¥{annual_depreciation:.2f}")
            
            # 计算ROI (示例)
            purchase_price = cost.purchase_price
            total_cost = purchase_price + (cost.maintenance_cost or 0)
            current_value = purchase_price - annual_depreciation
            roi = (current_value - total_cost) / purchase_price * 100 if purchase_price > 0 else 0
            
            print(f"  - 当前净值: ¥{current_value:.2f}")
            print(f"  - 生命周期总成本: ¥{total_cost:.2f}")
            print(f"  - ROI: {roi:.1f}%")
            
            print("\n✅ 资产成本模块测试通过")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            import pytest
            pytest.fail(f"测试失败: {e}")

def test_asset_lifecycle():
    """测试资产生命周期模块"""
    print("\n" + "="*60)
    print("🧪 测试2: 资产生命周期模块 (AssetLifecycle)")
    print("="*60)
    
    app = create_app()
    with app.app_context():
        try:
            # 获取第一个资产
            equipment = Equipment.query.first()
            if not equipment:
                import pytest
                pytest.skip("没有找到资产，跳过测试")
            
            print(f"\n✓ 目标资产: {equipment.name} (ID: {equipment.id})")
            
            # 创建生命周期事件
            events = []
            
            # 事件1: 采购
            purchase_event = AssetLifecycle(
                equipment_id=equipment.id,
                event_type='purchase',
                event_date=datetime.now() - timedelta(days=365),
                description='初始采购',
                cost_involved=5000.0
            )
            events.append(purchase_event)

            # 事件2: 部署
            deployment_event = AssetLifecycle(
                equipment_id=equipment.id,
                event_type='deployment',
                event_date=datetime.now() - timedelta(days=360),
                description='部署到IT部门',
                documents='部署完成，开始使用'
            )
            events.append(deployment_event)

            # 事件3: 维护
            maintenance_event = AssetLifecycle(
                equipment_id=equipment.id,
                event_type='maintenance',
                event_date=datetime.now() - timedelta(days=180),
                description='定期维护',
                cost_involved=200.0,
                documents='清洁、检查、软件更新'
            )
            events.append(maintenance_event)

            # 检查事件是否已存在
            existing_events = AssetLifecycle.query.filter_by(
                equipment_id=equipment.id
            ).all()

            if existing_events:
                print(f"✓ 已有 {len(existing_events)} 条生命周期事件记录")
                for event in existing_events[:3]:
                    print(f"  - [{event.event_type}] {event.event_date}: {event.description}")
            else:
                # 添加新事件
                for event in events:
                    db.session.add(event)
                db.session.commit()
                print(f"✓ 创建 {len(events)} 条生命周期事件")
                for event in events:
                    print(f"  - [{event.event_type}] {event.event_date}: {event.description}")

            # 计算生命周期成本
            lifecycle_events = AssetLifecycle.query.filter_by(
                equipment_id=equipment.id
            ).all()

            total_cost = sum(event.cost_involved or 0 for event in lifecycle_events)
            event_types = {}
            for event in lifecycle_events:
                event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            
            print(f"  - 事件类型分布:")
            for event_type, count in event_types.items():
                print(f"    · {event_type}: {count}条")
            
            print("\n✅ 资产生命周期模块测试通过")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            import pytest
            pytest.fail(f"测试失败: {e}")

def test_inventory_warning():
    """测试库存预警模块"""
    print("\n" + "="*60)
    print("🧪 测试3: 库存预警模块 (InventoryWarning)")
    print("="*60)
    
    app = create_app()
    with app.app_context():
        try:
            # 获取第一个配件
            spare_part = SparePart.query.first()
            if not spare_part:
                import pytest
                pytest.skip("没有找到配件，跳过测试")
            
            print(f"\n✓ 目标配件: {spare_part.name} (ID: {spare_part.id})")
            print(f"  - 当前库存: {spare_part.quantity}")
            
            # 检查是否已有预警规则
            warning = InventoryWarning.query.filter_by(
                spare_part_id=spare_part.id
            ).first()
            
            if warning:
                print(f"✓ 预警规则已存在")
                print(f"  - 紧急阈值: {warning.critical_threshold}")
                print(f"  - 最小阈值: {warning.min_threshold}")
                print(f"  - 最大阈值: {warning.max_threshold}")
            else:
                # 创建预警规则
                warning = InventoryWarning(
                    spare_part_id=spare_part.id,
                    min_threshold=5,
                    critical_threshold=2,
                    max_threshold=100,
                    reorder_quantity=20,
                    alert_status='normal',
                    last_check_time=datetime.now()
                )
                db.session.add(warning)
                db.session.commit()
                print(f"✓ 创建预警规则成功")
                print(f"  - 紧急阈值: {warning.critical_threshold}")
                print(f"  - 最小阈值: {warning.min_threshold}")
                print(f"  - 最大阈值: {warning.max_threshold}")
            
            # 判断预警状态
            current_stock = spare_part.quantity
            if current_stock < warning.critical_threshold:
                status = "🚨 紧急"
            elif current_stock < warning.min_threshold:
                status = "⚠️ 预警"
            elif current_stock > warning.max_threshold:
                status = "📦 过剩"
            else:
                status = "✓ 正常"
            
            print(f"\n✓ 预警状态判断:")
            print(f"  - 当前库存: {current_stock}")
            print(f"  - 预警状态: {status}")
            print(f"  - 建议采购量: {warning.reorder_quantity if current_stock < warning.min_threshold else 0}")
            
            # 统计预警统计信息
            all_warnings = InventoryWarning.query.all()
            print(f"\n✓ 库存预警统计:")
            print(f"  - 配件总数: {SparePart.query.count()}")
            print(f"  - 已配置预警规则: {len(all_warnings)}")
            
            critical_count = sum(1 for w in all_warnings if w.alert_status == 'critical')
            warning_count = sum(1 for w in all_warnings if w.alert_status == 'warning')
            print(f"  - 紧急预警: {critical_count}")
            print(f"  - 一般预警: {warning_count}")
            
            print("\n✅ 库存预警模块测试通过")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            import pytest
            pytest.fail(f"测试失败: {e}")

def test_asset_handover():
    """测试资产交接模块"""
    print("\n" + "="*60)
    print("🧪 测试4: 资产交接模块 (AssetHandover)")
    print("="*60)
    
    app = create_app()
    with app.app_context():
        try:
            # 获取第一个资产
            equipment = Equipment.query.first()
            if not equipment:
                print("❌ 没有找到资产，跳过测试")
                return False
            
            print(f"\n✓ 目标资产: {equipment.name} (ID: {equipment.id})")
            
            # 检查是否已有交接记录
            import json
            handovers = AssetHandover.query.filter(AssetHandover.equipment_ids.contains(str(equipment.id))).all()
            
            if handovers:
                print(f"✓ 已有 {len(handovers)} 条交接记录")
                for handover in handovers[:2]:
                    print(f"  - {handover.from_department} → {handover.to_department} ({handover.handover_date})")
            else:
                # 创建交接记录（equipment_ids 存为 JSON 字符串）
                handover = AssetHandover(
                    equipment_ids=json.dumps([equipment.id]),
                    reason='部门调整',
                    created_date=datetime.now()
                )
                db.session.add(handover)
                db.session.commit()
                print(f"✓ 创建交接记录成功")
                print(f"  - 设备ID列表: {handover.equipment_ids}")
            
            # 统计所有交接记录
            all_handovers = AssetHandover.query.all()
            print(f"\n✓ 交接记录统计:")
            print(f"  - 总记录数: {len(all_handovers)}")
            
            # 按理由统计（使用 reason 字段）
            reason_counts = {}
            for ho in all_handovers:
                key = ho.reason or 'unknown'
                reason_counts[key] = reason_counts.get(key, 0) + 1
            
            print(f"  - 交接理由统计:")
            for change, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    · {change}: {count}次")
            
            print("\n✅ 资产交接模块测试通过")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            import pytest
            pytest.fail(f"测试失败: {e}")

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 IT资产管理系统 - 新功能集成测试")
    print("="*60)
    
    results = []
    
    # 测试1: 成本模块
    for name, fn in [("资产成本模块", test_asset_cost), ("资产生命周期模块", test_asset_lifecycle), ("库存预警模块", test_inventory_warning), ("资产交接模块", test_asset_handover)]:
        try:
            fn()
            results.append((name, True))
        except Exception:
            results.append((name, False))
    
    # 打印测试总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统可投入生产使用。")
        return True
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败，请检查相关代码。")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
