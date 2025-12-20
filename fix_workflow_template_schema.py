"""
检查并修复workflow_template表结构
"""

from app import create_app, db
from sqlalchemy import inspect, text

app = create_app()

def check_and_fix_workflow_template():
    """检查并修复workflow_template表"""
    with app.app_context():
        inspector = inspect(db.engine)
        
        if 'workflow_template' not in inspector.get_table_names():
            print("❌ workflow_template表不存在")
            return False
        
        print("检查workflow_template表结构...")
        columns = {c['name']: c for c in inspector.get_columns('workflow_template')}
        print(f"现有字段: {list(columns.keys())}")
        
        # 需要添加的新字段
        new_columns = {
            'code': ("VARCHAR(64)", ""),  # (type, default)
            'version': ("INTEGER", "1")
        }
        
        for col_name, (col_type, default_val) in new_columns.items():
            if col_name not in columns:
                try:
                    print(f"添加字段: {col_name}")
                    # SQLite不支持添加UNIQUE约束,先添加普通字段
                    db.session.execute(text(f"ALTER TABLE workflow_template ADD COLUMN {col_name} {col_type}"))
                    
                    # 为现有记录设置默认值
                    if col_name == 'code':
                        # 生成唯一的code
                        result = db.session.execute(text("SELECT id, order_type FROM workflow_template"))
                        for row in result:
                            tid, order_type = row[0], row[1]
                            code = f"{order_type.lower().replace(' ', '_')}_v1"
                            db.session.execute(text(f"UPDATE workflow_template SET code = '{code}' WHERE id = {tid}"))
                    elif default_val:
                        db.session.execute(text(f"UPDATE workflow_template SET {col_name} = {default_val} WHERE {col_name} IS NULL"))
                    
                    db.session.commit()
                    print(f"  ✓ 成功添加 {col_name}")
                except Exception as e:
                    print(f"  ✗ 添加 {col_name} 失败: {e}")
                    db.session.rollback()
            else:
                print(f"  • {col_name} 已存在")
        
        # 重新检查
        columns = {c['name']: c for c in inspector.get_columns('workflow_template')}
        print(f"\n修复后的字段: {list(columns.keys())}")
        
        # 检查数据
        result = db.session.execute(text("SELECT id, name, code, version FROM workflow_template"))
        print("\n现有模板:")
        for row in result:
            print(f"  ID={row[0]}, name={row[1]}, code={row[2]}, version={row[3]}")
        
        return True

if __name__ == '__main__':
    import sys
    try:
        success = check_and_fix_workflow_template()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
