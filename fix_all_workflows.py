"""修复所有审批流程配置"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import User
from app.approval_models import WorkflowTemplate, WorkflowNode
from app.approval_roles import ApprovalRole, UserApprovalRole

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("开始修复审批流程配置")
    print("="*80 + "\n")
    
    # 1. 修复设备调拨流程
    print("1. 修复设备调拨流程...")
    transfer_template = WorkflowTemplate.query.filter_by(order_type='equipment_transfer').first()
    if transfer_template:
        dept_head_role = ApprovalRole.query.filter_by(code='department_head').first()
        admin_role = ApprovalRole.query.filter_by(code='admin').first()
        
        # 调出部门负责人审批
        node1 = WorkflowNode.query.filter_by(
            template_id=transfer_template.id,
            sequence=1
        ).first()
        if node1 and dept_head_role:
            node1.approval_role_id = dept_head_role.id
            print(f"   - 节点1 '{node1.name}' 已配置角色: {dept_head_role.name}")
        
        # 管理员审批
        node2 = WorkflowNode.query.filter_by(
            template_id=transfer_template.id,
            sequence=2
        ).first()
        if node2 and admin_role:
            node2.approval_role_id = admin_role.id
            print(f"   - 节点2 '{node2.name}' 已配置角色: {admin_role.name}")
        
        # 调入部门负责人确认
        node3 = WorkflowNode.query.filter_by(
            template_id=transfer_template.id,
            sequence=3
        ).first()
        if node3 and dept_head_role:
            node3.approval_role_id = dept_head_role.id
            print(f"   - 节点3 '{node3.name}' 已配置角色: {dept_head_role.name}")
    
    # 2. 修复设备借用流程
    print("\n2. 修复设备借用流程...")
    loan_template = WorkflowTemplate.query.filter_by(order_type='equipment_loan').first()
    if loan_template:
        dept_head_role = ApprovalRole.query.filter_by(code='department_head').first()
        admin_role = ApprovalRole.query.filter_by(code='admin').first()
        
        # 设备所属部门负责人审批
        node1 = WorkflowNode.query.filter_by(
            template_id=loan_template.id,
            sequence=1
        ).first()
        if node1 and dept_head_role:
            node1.approval_role_id = dept_head_role.id
            print(f"   - 节点1 '{node1.name}' 已配置角色: {dept_head_role.name}")
        
        # 管理员审批
        node2 = WorkflowNode.query.filter_by(
            template_id=loan_template.id,
            sequence=2
        ).first()
        if node2 and admin_role:
            node2.approval_role_id = admin_role.id
            print(f"   - 节点2 '{node2.name}' 已配置角色: {admin_role.name}")
    
    # 3. 为仓库管理员角色分配用户
    print("\n3. 为仓库管理员角色分配用户...")
    warehouse_role = ApprovalRole.query.filter_by(code='warehouse').first()
    admin_user = User.query.filter_by(username='admin').first()
    
    if warehouse_role and admin_user:
        # 检查是否已分配
        existing = UserApprovalRole.query.filter_by(
            user_id=admin_user.id,
            role_id=warehouse_role.id
        ).first()
        
        if not existing:
            assignment = UserApprovalRole(
                user_id=admin_user.id,
                role_id=warehouse_role.id,
                is_active=True
            )
            db.session.add(assignment)
            print(f"   - 已将用户 '{admin_user.username}' 分配到角色 '{warehouse_role.name}'")
        else:
            if not existing.is_active:
                existing.is_active = True
                print(f"   - 已激活用户 '{admin_user.username}' 的角色分配")
            else:
                print(f"   - 用户 '{admin_user.username}' 已分配到角色")
    
    # 4. 为财务审批角色分配用户
    print("\n4. 为财务审批角色分配用户...")
    finance_role = ApprovalRole.query.filter_by(code='finance').first()
    
    if finance_role and admin_user:
        # 检查是否已分配
        existing = UserApprovalRole.query.filter_by(
            user_id=admin_user.id,
            role_id=finance_role.id
        ).first()
        
        if not existing:
            assignment = UserApprovalRole(
                user_id=admin_user.id,
                role_id=finance_role.id,
                is_active=True
            )
            db.session.add(assignment)
            print(f"   - 已将用户 '{admin_user.username}' 分配到角色 '{finance_role.name}'")
        else:
            if not existing.is_active:
                existing.is_active = True
                print(f"   - 已激活用户 '{admin_user.username}' 的角色分配")
            else:
                print(f"   - 用户 '{admin_user.username}' 已分配到角色")
    
    # 提交更改
    try:
        db.session.commit()
        print("\n" + "="*80)
        print("修复完成! 所有更改已保存")
        print("="*80)
    except Exception as e:
        db.session.rollback()
        print(f"\n错误: {e}")
        print("所有更改已回滚")
