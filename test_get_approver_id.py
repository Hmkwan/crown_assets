"""测试get_approver_id函数"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.approval_models import WorkflowNode, WorkflowTemplate
from app.models import User
from app.approval_roles import UserApprovalRole

app = create_app()


def run():
    with app.app_context():
        print("="*70)
        print("测试 get_approver_id 函数")
        print("="*70)
        
        # 获取第一个节点（部门负责人初审）
        first_node = WorkflowNode.query.join(WorkflowTemplate).filter(
            WorkflowTemplate.order_type == 'repair_order',
            WorkflowNode.is_active == True
        ).order_by(WorkflowNode.sequence).first()
        
        if not first_node:
            print("未找到repair_order的第一个节点")
            return
        
        print(f"\n节点信息:")
        print(f"  - 名称: {first_node.name}")
        print(f"  - 序号: {first_node.sequence}")
        print(f"  - 审批角色ID: {first_node.approval_role_id}")
        print(f"  - role_required: {first_node.role_required}")
        
        if first_node.approval_role_id:
            print(f"\n审批角色用户:")
            assignments = UserApprovalRole.query.filter_by(
                role_id=first_node.approval_role_id,
                is_active=True
            ).all()
            
            eligible_users = [a.user for a in assignments if a.user and a.user.is_active]
            print(f"  共 {len(eligible_users)} 个用户:")
            for user in eligible_users:
                print(f"    - {user.username} (ID={user.id}, 部门={user.department})")
        
        # 测试get_approver_id
        print(f"\n测试 get_approver_id:")
        
        # 导入函数
        from app.main.routes import get_approver_id
        
        test_departments = ['企管部', '信息部', None]
        
        for dept in test_departments:
            approver_id = get_approver_id(first_node, dept)
            print(f"\n  部门='{dept}' → 审批人ID={approver_id}")
            if approver_id:
                user = User.query.get(approver_id)
                if user:
                    print(f"    审批人: {user.username} ({user.department})")
            else:
                print(f"    未找到审批人！")
                
                # 调试：逐步检查
                print(f"\n    调试信息:")
                print(f"      - node.approval_role_id = {first_node.approval_role_id}")
                
                if first_node.approval_role_id:
                    assignments = UserApprovalRole.query.filter_by(
                        role_id=first_node.approval_role_id,
                        is_active=True
                    ).all()
                    print(f"      - 角色分配数: {len(assignments)}")
                    
                    eligible_users = [a.user for a in assignments if a.user and a.user.is_active]
                    print(f"      - 符合条件的用户数: {len(eligible_users)}")
                    
                    if dept and eligible_users:
                        same_dept_users = [u for u in eligible_users if u.department == dept]
                        print(f"      - 同部门用户数: {len(same_dept_users)}")


if __name__ == '__main__':
    run()
