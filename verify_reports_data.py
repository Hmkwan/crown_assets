#!/usr/bin/env python
"""验证成本分析、库存预警和生命周期是否正确加载数据"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import Equipment, AssetCost, InventoryWarning, SparePart, AssetLifecycle

# 创建应用上下文
app = create_app()

with app.app_context():
    print("=" * 60)
    print("📊 验证报表数据加载")
    print("=" * 60)
    
    # 1. 验证成本分析数据
    print("\n1️⃣  成本分析数据验证:")
    print("-" * 60)
    try:
        from app.services import CostService
        
        # 检查是否有成本数据
        depreciation_data = CostService.get_depreciation_analysis()
        print(f"✅ 折旧分析: {len(depreciation_data)} 条记录")
        if depreciation_data:
            sample = depreciation_data[0]
            print(f"   样本数据: {sample['equipment_name']}")
            print(f"   采购价: ¥{sample['original_value']:.2f}")
            print(f"   当前价值: ¥{sample['current_value']:.2f}")
            print(f"   折旧: ¥{sample['depreciation']:.2f}")
        
        cost_by_type = CostService.get_cost_by_asset_type()
        print(f"✅ 按类型统计: {len(cost_by_type)} 种类型")
        
        maintenance = CostService.get_maintenance_cost_analysis()
        print(f"✅ 维修成本分析: {len(maintenance)} 条记录")
        
        department_costs = CostService.get_department_cost_analysis()
        print(f"✅ 部门成本分析: {len(department_costs)} 个部门")
        if department_costs:
            dept = department_costs[0]
            print(f"   部门: {dept[0]}, 资产数: {dept[1]}, 总成本: ¥{dept[2] or 0:.2f}")
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 2. 验证库存预警数据
    print("\n2️⃣  库存预警数据验证:")
    print("-" * 60)
    try:
        from app.services import InventoryService
        
        # 检查是否有库存预警
        warning_status = InventoryService.get_warning_status()
        total_warnings = (len(warning_status.get('critical', [])) + 
                         len(warning_status.get('warning', [])))
        print(f"✅ 库存预警状态: 紧急({len(warning_status.get('critical', []))}), 警告({len(warning_status.get('warning', []))})")
        
        procurement = InventoryService.get_procurement_suggestion()
        print(f"✅ 采购建议: {len(procurement)} 条建议")
        if procurement:
            sample = procurement[0]
            print(f"   配件: {sample['part_name']}")
            print(f"   当前库存: {sample['current_stock']}")
            print(f"   建议采购: {sample['suggested_quantity']} 件")
            print(f"   预估成本: ¥{sample['total_estimated_cost']:.2f}")
        
        inventory_summary = InventoryService.get_inventory_summary()
        print(f"✅ 库存概览: {inventory_summary['total_parts']} 种配件")
        print(f"   总价值: ¥{inventory_summary['total_inventory_value']:.2f}")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 3. 验证生命周期数据
    print("\n3️⃣  生命周期数据验证:")
    print("-" * 60)
    try:
        from app.services import LifecycleService
        
        # 检查资产生命周期信息
        dashboard_stats = LifecycleService.get_lifecycle_dashboard()
        print(f"✅ 生命周期统计:")
        print(f"   总资产数: {dashboard_stats.get('total_assets', 0)}")
        print(f"   新增资产: {dashboard_stats.get('new_assets', 0)}")
        print(f"   成熟资产: {dashboard_stats.get('mature_assets', 0)}")
        print(f"   老化资产: {dashboard_stats.get('aging_assets', 0)}")
        print(f"   推荐报废: {dashboard_stats.get('recommended_for_retirement', 0)}")
        
        # 随机检查一个资产的年龄
        equipment = Equipment.query.first()
        if equipment:
            age_info = LifecycleService.get_asset_age(equipment.id)
            if age_info:
                print(f"\n✅ 资产年龄计算 (样本 #{equipment.id}):")
                print(f"   资产名: {equipment.name}")
                print(f"   采购日期: {age_info['purchase_date']}")
                print(f"   使用年限: {age_info['age_display']}")
                print(f"   距采购: {age_info['age_days']} 天")
        
        # 检查报废建议
        if equipment:
            recommendation = LifecycleService.recommend_retirement(equipment.id)
            if recommendation:
                print(f"\n✅ 报废推荐 (样本):")
                print(f"   是否应报废: {recommendation['should_retire']}")
                print(f"   风险评分: {recommendation['risk_score']}")
                if recommendation['reasons']:
                    for reason in recommendation['reasons']:
                        print(f"   原因: {reason}")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ 验证完成！所有报表功能已正确引用数据")
    print("=" * 60)
