"""全面测试所有审批流程"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import (User, Equipment, SparePart, Department, 
                        RepairOrder, PartRequestOrder, EquipmentApplication,
                        EquipmentLoan, EquipmentTransfer, EquipmentScrap)
from app.approval_models import WorkflowTemplate, WorkflowNode
from app.approval_roles import ApprovalRole, UserApprovalRole
from datetime import datetime, timedelta

app = create_app()

def print_section(title):
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")

with app.app_context():
    print_section("审批流程全面检查")
    
    # 1. 检查所有工作流模板
    print_section("1. 工作流模板检查")
    templates = WorkflowTemplate.query.all()
    print(f"共有 {len(templates)} 个工作流模板:\n")
    
    for template in templates:
        nodes = WorkflowNode.query.filter_by(
            template_id=template.id,
            is_active=True
        ).order_by(WorkflowNode.sequence).all()
        
        print(f"模板: {template.name}")
        print(f"  - 工单类型: {template.order_type}")
        print(f"  - 状态: {'启用' if template.is_active else '禁用'}")
        print(f"  - 节点数: {len(nodes)}")
        
        if nodes:
            print(f"  - 审批流程:")
            for node in nodes:
                role_info = f"角色ID:{node.approval_role_id}" if node.approval_role_id else f"旧角色:{node.role_required}"
                print(f"      {node.sequence}. {node.name} ({role_info})")
        else:
            print(f"  ⚠️ 警告: 没有活跃的审批节点!")
        print()
    
    # 2. 检查审批角色配置
    print_section("2. 审批角色配置检查")
    roles = ApprovalRole.query.filter_by(is_active=True).all()
    print(f"共有 {len(roles)} 个审批角色:\n")
    
    for role in roles:
        print(f"角色: {role.name} ({role.code})")
        print(f"  - 描述: {role.description}")
        
        # 检查分配的用户
        assignments = UserApprovalRole.query.filter_by(
            role_id=role.id,
            is_active=True
        ).all()
        
        if assignments:
            print(f"  - 分配用户 ({len(assignments)}):")
            for assignment in assignments:
                if assignment.user:
                    print(f"      • {assignment.user.username} ({assignment.user.department})")
        else:
            print(f"  ⚠️ 警告: 没有用户被分配到此角色!")
        print()
    
    # 3. 检查基础数据
    print_section("3. 基础数据检查")
    
    users = User.query.filter_by(is_active=True).all()
    print(f"活跃用户: {len(users)}")
    for user in users:
        print(f"  • {user.username} - {user.department} - {user.role}")
    
    print(f"\n设备: {Equipment.query.count()}")
    equipments = Equipment.query.limit(5).all()
    for eq in equipments:
        category = eq.category.name if hasattr(eq, 'category') and eq.category else 'N/A'
        print(f"  • {eq.name} ({category}) - {eq.department} - {eq.status}")
    
    print(f"\n配件: {SparePart.query.count()}")
    parts = SparePart.query.limit(5).all()
    for part in parts:
        print(f"  • {part.name} ({part.part_number}) - 库存:{part.stock_quantity}")
    
    # 4. 检查各类工单数量
    print_section("4. 工单数据统计")
    
    print(f"维修工单: {RepairOrder.query.count()}")
    print(f"配件申请: {PartRequestOrder.query.count()}")
    print(f"设备申请: {EquipmentApplication.query.count()}")
    print(f"设备借用: {EquipmentLoan.query.count()}")
    print(f"设备调拨: {EquipmentTransfer.query.count()}")
    print(f"设备报废: {EquipmentScrap.query.count()}")
    
    # 5. 检查问题
    print_section("5. 潜在问题汇总")
    
    issues = []
    
    # 检查是否有模板没有节点
    for template in templates:
        if template.is_active:
            node_count = WorkflowNode.query.filter_by(
                template_id=template.id,
                is_active=True
            ).count()
            if node_count == 0:
                issues.append(f"⚠️ 模板 '{template.name}' 没有活跃的审批节点")
    
    # 检查是否有角色没有用户
    for role in roles:
        user_count = UserApprovalRole.query.filter_by(
            role_id=role.id,
            is_active=True
        ).count()
        if user_count == 0:
            issues.append(f"⚠️ 角色 '{role.name}' 没有分配用户")
    
    # 检查节点是否都有审批角色
    all_nodes = WorkflowNode.query.filter_by(is_active=True).all()
    for node in all_nodes:
        if not node.approval_role_id and not node.role_required:
            issues.append(f"⚠️ 节点 '{node.name}' (模板:{node.template.name}) 没有配置审批角色")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("✓ 未发现配置问题")
    
    print_section("检查完成")
