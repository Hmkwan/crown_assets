"""检查管理员评估金额节点的配置"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.approval_models import WorkflowNode, WorkflowTemplate

app = create_app()

with app.app_context():
    print("="*70)
    print("检查管理员评估金额节点")
    print("="*70)
    
    # 查找节点
    node = WorkflowNode.query.filter(
        WorkflowNode.name.like('%管理员%评估%')
    ).first()
    
    if node:
        print(f"\n节点: {node.name}")
        print(f"  ID: {node.id}")
        print(f"  顺序: {node.sequence}")
        print(f"  审批角色ID: {node.approval_role_id}")
        print(f"  旧role_required: {node.role_required}")
        print(f"  需要评论: {node.require_comment}")
        print(f"  表单字段: {node.form_fields}")
        print(f"  节点类型: {node.node_type if hasattr(node, 'node_type') else 'N/A'}")
        
        template = node.template
        if template:
            print(f"\n所属模板:")
            print(f"  名称: {template.name}")
            print(f"  工单类型: {template.order_type}")
    else:
        print("\n未找到'管理员评估金额'节点")
        print("\n所有节点:")
        for n in WorkflowNode.query.all():
            print(f"  - {n.name} (ID:{n.id})")
