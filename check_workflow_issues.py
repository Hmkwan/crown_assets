"""简化版审批流程检查"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.approval_models import WorkflowTemplate, WorkflowNode
from app.approval_roles import ApprovalRole, UserApprovalRole

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("发现的问题汇总:")
    print("="*80 + "\n")
    
    issues = []
    
    # 1. 检查设备调拨流程
    transfer_template = WorkflowTemplate.query.filter_by(order_type='equipment_transfer').first()
    if transfer_template:
        transfer_nodes = WorkflowNode.query.filter_by(
            template_id=transfer_template.id,
            is_active=True
        ).all()
        
        for node in transfer_nodes:
            if not node.approval_role_id:
                issues.append(f"【设备调拨】节点 '{node.name}' 没有配置审批角色")
    
    # 2. 检查设备借用流程
    loan_template = WorkflowTemplate.query.filter_by(order_type='equipment_loan').first()
    if loan_template:
        loan_nodes = WorkflowNode.query.filter_by(
            template_id=loan_template.id,
            is_active=True
        ).all()
        
        for node in loan_nodes:
            if not node.approval_role_id:
                issues.append(f"【设备借用】节点 '{node.name}' 没有配置审批角色")
    
    # 3. 检查仓库管理员角色
    warehouse_role = ApprovalRole.query.filter_by(code='warehouse').first()
    if warehouse_role:
        user_count = UserApprovalRole.query.filter_by(
            role_id=warehouse_role.id,
            is_active=True
        ).count()
        if user_count == 0:
            issues.append("【仓库管理员】角色没有分配用户,配件申请流程会失败")
    
    # 4. 检查财务审批角色
    finance_role = ApprovalRole.query.filter_by(code='finance').first()
    if finance_role:
        user_count = UserApprovalRole.query.filter_by(
            role_id=finance_role.id,
            is_active=True
        ).count()
        if user_count == 0:
            issues.append("【财务审批】角色没有分配用户,设备报废流程会失败")
    
    if issues:
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    else:
        print("未发现配置问题")
    
    print("\n" + "="*80)
    print("需要修复的流程:")
    print("="*80 + "\n")
    
    print("1. 设备调拨流程 - 需要为所有节点配置审批角色")
    print("2. 设备借用流程 - 需要为所有节点配置审批角色")
    print("3. 仓库管理员角色 - 需要分配用户")
    print("4. 财务审批角色 - 需要分配用户")
