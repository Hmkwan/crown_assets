"""
添加 approval_role_id 到 WorkflowNode
"""
from app import create_app, db
from sqlalchemy import text

def migrate():
    """执行迁移"""
    app = create_app()
    with app.app_context():
        print("开始数据库迁移: 添加 approval_role_id 到 workflow_node...")
        
        try:
            # 检查列是否已存在
            result = db.session.execute(text("PRAGMA table_info(workflow_node)")).fetchall()
            columns = [row[1] for row in result]
            
            if 'approval_role_id' in columns:
                print("✓ approval_role_id 列已存在,跳过迁移")
                return True
            
            # 添加新列
            db.session.execute(text(
                "ALTER TABLE workflow_node ADD COLUMN approval_role_id INTEGER"
            ))
            db.session.commit()
            print("✓ 成功添加 approval_role_id 列")
            
            # 可选:为现有数据迁移角色映射
            print("\n开始迁移现有数据...")
            from app.approval_roles import ApprovalRole
            
            # 角色映射
            role_mapping = {
                'admin': 'admin',
                'department_head': 'department_head',
                'technician': 'technician',
                'warehouse': 'warehouse',
                'finance': 'finance'
            }
            
            migrated_count = 0
            for old_role, new_role_code in role_mapping.items():
                # 查找新角色
                new_role = ApprovalRole.query.filter_by(code=new_role_code).first()
                if new_role:
                    # 更新所有使用旧角色的节点
                    result = db.session.execute(
                        text(f"UPDATE workflow_node SET approval_role_id = :role_id WHERE role_required = :old_role"),
                        {'role_id': new_role.id, 'old_role': old_role}
                    )
                    count = result.rowcount
                    if count > 0:
                        print(f"  ✓ {old_role} -> {new_role.name}: {count} 个节点")
                        migrated_count += count
            
            db.session.commit()
            print(f"\n✓ 成功迁移 {migrated_count} 个工作流节点")
            print("\n✅ 数据库迁移完成!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ 迁移失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = migrate()
    if not success:
        print("\n迁移失败,请检查错误信息")
        exit(1)
