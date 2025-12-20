"""
审批系统增强 - 数据库迁移
添加维修金额、工作流金额条件、审批操作类型等字段
"""

def upgrade_database(db):
    """升级数据库"""
    from sqlalchemy import text
    
    print("开始数据库升级...")
    
    # 1. RepairOrder 添加维修金额字段
    try:
        db.session.execute(text("""
            ALTER TABLE repair_order 
            ADD COLUMN repair_cost DECIMAL(10, 2) DEFAULT 0.00
        """))
        print("✓ 添加 repair_order.repair_cost 字段")
    except Exception as e:
        print(f"  repair_cost 字段可能已存在: {e}")
    
    # 2. WorkflowNode 添加金额阈值字段
    try:
        db.session.execute(text("""
            ALTER TABLE workflow_node 
            ADD COLUMN amount_threshold DECIMAL(10, 2)
        """))
        print("✓ 添加 workflow_node.amount_threshold 字段")
    except Exception as e:
        print(f"  amount_threshold 字段可能已存在: {e}")
    
    try:
        db.session.execute(text("""
            ALTER TABLE workflow_node 
            ADD COLUMN skip_if_below_threshold BOOLEAN DEFAULT 0
        """))
        print("✓ 添加 workflow_node.skip_if_below_threshold 字段")
    except Exception as e:
        print(f"  skip_if_below_threshold 字段可能已存在: {e}")
    
    # 3. ApprovalWorkflow 添加更多审批操作字段
    try:
        db.session.execute(text("""
            ALTER TABLE approval_workflow 
            ADD COLUMN action_type VARCHAR(32) DEFAULT 'approve'
        """))
        print("✓ 添加 approval_workflow.action_type 字段")
    except Exception as e:
        print(f"  action_type 字段可能已存在: {e}")
    
    try:
        db.session.execute(text("""
            ALTER TABLE approval_workflow 
            ADD COLUMN transferred_from_id INTEGER
        """))
        print("✓ 添加 approval_workflow.transferred_from_id 字段")
    except Exception as e:
        print(f"  transferred_from_id 字段可能已存在: {e}")
    
    try:
        db.session.execute(text("""
            ALTER TABLE approval_workflow 
            ADD COLUMN admin_action VARCHAR(32)
        """))
        print("✓ 添加 approval_workflow.admin_action 字段")
    except Exception as e:
        print(f"  admin_action 字段可能已存在: {e}")
    
    try:
        db.session.execute(text("""
            ALTER TABLE approval_workflow 
            ADD COLUMN admin_operator_id INTEGER
        """))
        print("✓ 添加 approval_workflow.admin_operator_id 字段")
    except Exception as e:
        print(f"  admin_operator_id 字段可能已存在: {e}")
    
    try:
        db.session.execute(text("""
            ALTER TABLE approval_workflow 
            ADD COLUMN repair_cost_input DECIMAL(10, 2)
        """))
        print("✓ 添加 approval_workflow.repair_cost_input 字段")
    except Exception as e:
        print(f"  repair_cost_input 字段可能已存在: {e}")
    
    db.session.commit()
    print("\n数据库升级完成!")

if __name__ == '__main__':
    from app import create_app, db
    app = create_app()
    with app.app_context():
        upgrade_database(db)
