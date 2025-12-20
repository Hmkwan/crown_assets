"""
快速验证审批流引擎模型与路由
"""
from app import create_app, db
from app.approval_models import WorkflowTemplate, WorkflowNode
from app.models import ApprovalWorkflow
from app.workflow_models_new import WorkflowInstance

def test_workflow_models():
    app = create_app()
    with app.app_context():
        print("=" * 50)
        print("验证审批流引擎模型...")
        print("=" * 50)
        
        # 测试模型导入
        try:
            template = WorkflowTemplate.query.first()
            print(f"✓ WorkflowTemplate 模型正常，记录数: {WorkflowTemplate.query.count()}")
        except Exception as e:
            print(f"✗ WorkflowTemplate 错误: {e}")
        
        try:
            node = WorkflowNode.query.first()
            print(f"✓ WorkflowNode 模型正常，记录数: {WorkflowNode.query.count()}")
        except Exception as e:
            print(f"✗ WorkflowNode 错误: {e}")
        
        try:
            instance = WorkflowInstance.query.first()
            print(f"✓ WorkflowInstance 模型正常，记录数: {WorkflowInstance.query.count()}")
        except Exception as e:
            print(f"✗ WorkflowInstance 错误: {e}")
        
        try:
            approval = ApprovalWorkflow.query.first()
            print(f"✓ ApprovalWorkflow 模型正常，记录数: {ApprovalWorkflow.query.count()}")
        except Exception as e:
            print(f"✗ ApprovalWorkflow 错误: {e}")
        
        # 测试路由是否注册
        print("\n验证路由注册...")
        workflow_routes = [rule for rule in app.url_map.iter_rules() if 'workflow' in rule.rule]
        if workflow_routes:
            print(f"✓ 审批流路由已注册，共 {len(workflow_routes)} 个端点:")
            for route in workflow_routes[:5]:
                print(f"  - {route.rule} [{', '.join(route.methods - {'HEAD', 'OPTIONS'})}]")
            if len(workflow_routes) > 5:
                print(f"  ... 还有 {len(workflow_routes) - 5} 个")
        else:
            print("✗ 未找到审批流路由")
        
        print("\n" + "=" * 50)
        print("验证完成！")
        print("=" * 50)

if __name__ == '__main__':
    test_workflow_models()
