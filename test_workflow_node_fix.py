"""测试WorkflowNode的order_type属性修复"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.approval_models import WorkflowNode, WorkflowTemplate
from app.models import User

app = create_app()

with app.app_context():
    print("="*60)
    print("测试 WorkflowNode.order_type 属性")
    print("="*60)
    
    # 1. 查找一个有template的节点
    node = WorkflowNode.query.join(WorkflowTemplate).first()
    
    if node:
        print(f"\n✓ 找到节点: {node.name}")
        print(f"  - 节点ID: {node.id}")
        print(f"  - Template ID: {node.template_id}")
        
        if node.template:
            print(f"  - Template: {node.template.name}")
            print(f"  - Template order_type: {node.template.order_type}")
        
        # 测试order_type属性
        try:
            order_type = node.order_type
            print(f"  - Node order_type (通过属性): {order_type}")
            print("  ✓ order_type 属性工作正常!")
        except Exception as e:
            print(f"  ✗ 访问 order_type 失败: {e}")
    else:
        print("✗ 没有找到任何节点")
    
    print("\n" + "="*60)
    print("测试重新分配审批人功能所需的用户查询")
    print("="*60)
    
    # 2. 测试获取审批人列表
    from app.approval_roles import UserApprovalRole
    
    # 查找一个有approval_role的节点
    node_with_role = WorkflowNode.query.filter(
        WorkflowNode.approval_role_id.isnot(None)
    ).first()
    
    if node_with_role:
        print(f"\n✓ 找到带审批角色的节点: {node_with_role.name}")
        print(f"  - 审批角色ID: {node_with_role.approval_role_id}")
        
        if node_with_role.approval_role:
            print(f"  - 审批角色: {node_with_role.approval_role.name}")
        
        # 获取该角色的用户
        role_assignments = UserApprovalRole.query.filter_by(
            role_id=node_with_role.approval_role_id,
            is_active=True
        ).all()
        
        print(f"  - 角色分配数量: {len(role_assignments)}")
        
        eligible_users = [
            assignment.user 
            for assignment in role_assignments 
            if assignment.user and assignment.user.is_active
        ]
        
        print(f"  - 符合条件的用户数: {len(eligible_users)}")
        for user in eligible_users[:5]:  # 只显示前5个
            print(f"    * {user.username} ({user.department or '无部门'})")
        
        if len(eligible_users) > 0:
            print("  ✓ 用户列表获取正常!")
        else:
            print("  ⚠ 没有符合条件的用户，可能需要分配审批角色")
    else:
        print("✗ 没有找到带审批角色的节点")
        
        # 如果没有审批角色节点，测试获取所有活跃用户
        all_active_users = User.query.filter_by(is_active=True).all()
        print(f"\n  备选方案: 所有活跃用户数量: {len(all_active_users)}")
        for user in all_active_users[:5]:
            print(f"    * {user.username} ({user.department or '无部门'})")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
