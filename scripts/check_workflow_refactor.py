"""验证审批流配置重构"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.approval_models import WorkflowNode

app = create_app()

with app.app_context():
    # 工单类型配置
    order_types = {
        'repair_order': {'name': '维修工单', 'icon': '🔧'},
        'part_request_order': {'name': '配件申请', 'icon': '📦'},
        'equipment_application': {'name': '设备申请', 'icon': '💻'},
        'equipment_loan': {'name': '设备借用', 'icon': '🤝'},
        'equipment_transfer': {'name': '设备调拨', 'icon': '🚚'},
        'equipment_scrap': {'name': '设备报废', 'icon': '🗑️'}
    }
    
    print("\n" + "="*70)
    print("✓ 审批流程配置重构验证 (端口5020)")
    print("="*70)
    
    print("\n📋 工单类型审批流统计:")
    print("-" * 70)
    total_nodes = 0
    
    for type_key, type_info in order_types.items():
        nodes = WorkflowNode.query.filter_by(
            order_type=type_key, 
            is_active=True
        ).order_by(WorkflowNode.sequence).all()
        
        count = len(nodes)
        total_nodes += count
        
        status_icon = "✅" if count > 0 else "⚠️"
        print(f"{status_icon} {type_info['icon']} {type_info['name']:<12} | {count:2d} 个审批节点", end="")
        
        if nodes:
            print(f" | 顺序: {', '.join([str(n.sequence) for n in nodes])}")
            for node in nodes:
                role_map = {
                    'department_head': '部门负责人',
                    'admin': '管理员',
                    'procurement': '采购',
                    'warehouse': '仓库',
                    'finance': '财务',
                    'executive': '高层'
                }
                role = role_map.get(node.role_required, node.role_required)
                print(f"      {node.sequence}. {node.name} ({role})")
        else:
            print(" | ⚠️ 未配置")
    
    print("-" * 70)
    print(f"总计: {total_nodes} 个活动审批节点")
    
    print("\n🌐 访问地址:")
    print("  主界面: http://localhost:5020/admin/workflow_config")
    print("\n  各工单类型配置:")
    for type_key, type_info in order_types.items():
        url = f"http://localhost:5020/admin/workflow_config/{type_key}"
        print(f"    {type_info['icon']} {type_info['name']}: {url}")
    
    print("\n✨ 新界面特性:")
    print("  ✓ 按工单类型组织（6个类型卡片）")
    print("  ✓ 可视化流程图（起点→节点→终点）")
    print("  ✓ 卡片式导航（点击进入详情）")
    print("  ✓ 节点详细列表（编辑/删除操作）")
    print("  ✓ 空状态友好提示")
    print("  ✓ 自动计算下一序号")
    
    print("\n🎯 使用建议:")
    print("  1. 访问主界面查看所有工单类型")
    print("  2. 点击卡片进入具体类型配置")
    print("  3. 查看流程图了解审批链路")
    print("  4. 使用添加/编辑功能配置节点")
    print("  5. 未配置的类型会显示空状态提示")
    
    print("\n" + "="*70)
