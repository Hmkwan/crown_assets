"""
手动执行数据库迁移脚本
创建企业级审批系统的7个新表
"""

from app import create_app, db, get_beijing_now
from sqlalchemy import inspect, text
import sys

app = create_app()

def check_table_exists(table_name):
    """检查表是否存在"""
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

def check_column_exists(table_name, column_name):
    """检查列是否存在"""
    inspector = inspect(db.engine)
    if table_name not in inspector.get_table_names():
        return False
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns

def upgrade():
    """执行升级迁移"""
    print("开始执行数据库迁移...")
    
    with app.app_context():
        # 1. 创建 workflow_template 表
        if not check_table_exists('workflow_template'):
            print("创建 workflow_template 表...")
            db.session.execute(text("""
                CREATE TABLE workflow_template (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(128) NOT NULL,
                    code VARCHAR(64) NOT NULL,
                    order_type VARCHAR(64) NOT NULL,
                    description TEXT,
                    version INTEGER NOT NULL DEFAULT 1,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    is_default BOOLEAN NOT NULL DEFAULT 0,
                    created_by_id INTEGER,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME,
                    FOREIGN KEY (created_by_id) REFERENCES user(id) ON DELETE SET NULL,
                    UNIQUE (code, version)
                )
            """))
            db.session.execute(text("CREATE INDEX ix_workflow_template_code ON workflow_template(code)"))
            db.session.execute(text("CREATE INDEX ix_workflow_template_order_type ON workflow_template(order_type)"))
            print("✓ workflow_template 表创建成功")
        else:
            print("workflow_template 表已存在,跳过")
        
        # 2. 增强 workflow_node 表
        if check_table_exists('workflow_node'):
            print("增强 workflow_node 表...")
            
            # 添加各个新字段
            new_columns = {
                'template_id': 'INTEGER',
                'node_type': "VARCHAR(32) NOT NULL DEFAULT 'approval'",
                'condition_expression': 'TEXT',
                'parallel_mode': 'VARCHAR(16)',
                'parallel_count': 'INTEGER',
                'timeout_hours': 'INTEGER',
                'timeout_action': 'VARCHAR(32)',
                'escalate_to_user_id': 'INTEGER',
                'auto_approve_rules': 'TEXT',
                'notify_methods': 'TEXT'
            }
            
            for col_name, col_type in new_columns.items():
                if not check_column_exists('workflow_node', col_name):
                    try:
                        db.session.execute(text(f"ALTER TABLE workflow_node ADD COLUMN {col_name} {col_type}"))
                        print(f"  ✓ 添加 workflow_node.{col_name}")
                    except Exception as e:
                        print(f"  ✗ 添加 workflow_node.{col_name} 失败: {e}")
        
        # 3. 创建 approval_instance 表
        if not check_table_exists('approval_instance'):
            print("创建 approval_instance 表...")
            db.session.execute(text("""
                CREATE TABLE approval_instance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id INTEGER NOT NULL,
                    order_type VARCHAR(64) NOT NULL,
                    order_id INTEGER NOT NULL,
                    initiator_id INTEGER NOT NULL,
                    status VARCHAR(32) NOT NULL DEFAULT 'pending',
                    current_node_id INTEGER,
                    context_data TEXT,
                    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME,
                    FOREIGN KEY (template_id) REFERENCES workflow_template(id) ON DELETE RESTRICT,
                    FOREIGN KEY (initiator_id) REFERENCES user(id) ON DELETE RESTRICT,
                    FOREIGN KEY (current_node_id) REFERENCES workflow_node(id) ON DELETE SET NULL
                )
            """))
            db.session.execute(text("CREATE INDEX ix_approval_instance_order ON approval_instance(order_type, order_id)"))
            db.session.execute(text("CREATE INDEX ix_approval_instance_status ON approval_instance(status)"))
            db.session.execute(text("CREATE INDEX ix_approval_instance_initiator ON approval_instance(initiator_id)"))
            print("✓ approval_instance 表创建成功")
        else:
            print("approval_instance 表已存在,跳过")
        
        # 4. 创建 approval_step 表
        if not check_table_exists('approval_step'):
            print("创建 approval_step 表...")
            db.session.execute(text("""
                CREATE TABLE approval_step (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    instance_id INTEGER NOT NULL,
                    node_id INTEGER NOT NULL,
                    approver_id INTEGER,
                    delegated_by_id INTEGER,
                    step_order INTEGER NOT NULL,
                    status VARCHAR(32) NOT NULL DEFAULT 'pending',
                    decision VARCHAR(32),
                    comments TEXT,
                    deadline DATETIME,
                    assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    processed_at DATETIME,
                    is_parallel BOOLEAN NOT NULL DEFAULT 0,
                    parallel_group_id VARCHAR(64),
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME,
                    FOREIGN KEY (instance_id) REFERENCES approval_instance(id) ON DELETE CASCADE,
                    FOREIGN KEY (node_id) REFERENCES workflow_node(id) ON DELETE RESTRICT,
                    FOREIGN KEY (approver_id) REFERENCES user(id) ON DELETE SET NULL,
                    FOREIGN KEY (delegated_by_id) REFERENCES user(id) ON DELETE SET NULL
                )
            """))
            db.session.execute(text("CREATE INDEX ix_approval_step_instance ON approval_step(instance_id)"))
            db.session.execute(text("CREATE INDEX ix_approval_step_approver ON approval_step(approver_id, status)"))
            db.session.execute(text("CREATE INDEX ix_approval_step_deadline ON approval_step(deadline)"))
            print("✓ approval_step 表创建成功")
        else:
            print("approval_step 表已存在,跳过")
        
        # 5. 创建 approval_log 表
        if not check_table_exists('approval_log'):
            print("创建 approval_log 表...")
            db.session.execute(text("""
                CREATE TABLE approval_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    instance_id INTEGER NOT NULL,
                    step_id INTEGER,
                    action VARCHAR(64) NOT NULL,
                    actor_id INTEGER,
                    from_user_id INTEGER,
                    to_user_id INTEGER,
                    comments TEXT,
                    ip_address VARCHAR(64),
                    user_agent VARCHAR(256),
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (instance_id) REFERENCES approval_instance(id) ON DELETE CASCADE,
                    FOREIGN KEY (step_id) REFERENCES approval_step(id) ON DELETE SET NULL,
                    FOREIGN KEY (actor_id) REFERENCES user(id) ON DELETE SET NULL,
                    FOREIGN KEY (from_user_id) REFERENCES user(id) ON DELETE SET NULL,
                    FOREIGN KEY (to_user_id) REFERENCES user(id) ON DELETE SET NULL
                )
            """))
            db.session.execute(text("CREATE INDEX ix_approval_log_instance ON approval_log(instance_id)"))
            db.session.execute(text("CREATE INDEX ix_approval_log_actor ON approval_log(actor_id)"))
            db.session.execute(text("CREATE INDEX ix_approval_log_created ON approval_log(created_at)"))
            print("✓ approval_log 表创建成功")
        else:
            print("approval_log 表已存在,跳过")
        
        # 6. 创建 approval_delegate 表
        if not check_table_exists('approval_delegate'):
            print("创建 approval_delegate 表...")
            db.session.execute(text("""
                CREATE TABLE approval_delegate (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    delegator_id INTEGER NOT NULL,
                    delegate_id INTEGER NOT NULL,
                    start_date DATETIME NOT NULL,
                    end_date DATETIME NOT NULL,
                    scope VARCHAR(32) NOT NULL DEFAULT 'all',
                    order_types TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    reason TEXT,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME,
                    FOREIGN KEY (delegator_id) REFERENCES user(id) ON DELETE CASCADE,
                    FOREIGN KEY (delegate_id) REFERENCES user(id) ON DELETE CASCADE
                )
            """))
            db.session.execute(text("CREATE INDEX ix_approval_delegate_delegator ON approval_delegate(delegator_id, is_active)"))
            db.session.execute(text("CREATE INDEX ix_approval_delegate_date_range ON approval_delegate(start_date, end_date)"))
            print("✓ approval_delegate 表创建成功")
        else:
            print("approval_delegate 表已存在,跳过")
        
        # 7. 创建 approval_reminder 表
        if not check_table_exists('approval_reminder'):
            print("创建 approval_reminder 表...")
            db.session.execute(text("""
                CREATE TABLE approval_reminder (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    step_id INTEGER NOT NULL,
                    approver_id INTEGER NOT NULL,
                    reminder_type VARCHAR(32) NOT NULL,
                    notify_method VARCHAR(32) NOT NULL,
                    sent_at DATETIME,
                    status VARCHAR(32) NOT NULL DEFAULT 'pending',
                    error_message TEXT,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (step_id) REFERENCES approval_step(id) ON DELETE CASCADE,
                    FOREIGN KEY (approver_id) REFERENCES user(id) ON DELETE CASCADE
                )
            """))
            db.session.execute(text("CREATE INDEX ix_approval_reminder_step ON approval_reminder(step_id)"))
            db.session.execute(text("CREATE INDEX ix_approval_reminder_approver ON approval_reminder(approver_id, status)"))
            print("✓ approval_reminder 表创建成功")
        else:
            print("approval_reminder 表已存在,跳过")
        
        # 提交所有更改
        db.session.commit()
        print("\n✅ 数据库迁移完成!")
        print("已创建以下表:")
        print("  1. workflow_template - 工作流模板")
        print("  2. workflow_node (增强) - 工作流节点")
        print("  3. approval_instance - 审批实例")
        print("  4. approval_step - 审批步骤")
        print("  5. approval_log - 审批日志")
        print("  6. approval_delegate - 审批委托")
        print("  7. approval_reminder - 审批提醒")
        
        return True

if __name__ == '__main__':
    try:
        success = upgrade()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
