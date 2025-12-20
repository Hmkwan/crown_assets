"""
数据库迁移：为配件表添加type_id字段，并创建配件类型表
"""
from app import create_app, db
from sqlalchemy import text

def migrate_spare_part_type():
    app = create_app()
    with app.app_context():
        try:
            # 创建配件类型表
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS spare_part_type (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(120) UNIQUE NOT NULL,
                    description TEXT,
                    created_date DATETIME
                )
            """))
            print("✓ 配件类型表创建成功")
            
            # 检查spare_part表是否已有type_id字段
            result = db.session.execute(text("PRAGMA table_info(spare_part)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'type_id' not in columns:
                # 添加type_id字段
                db.session.execute(text("""
                    ALTER TABLE spare_part ADD COLUMN type_id INTEGER
                """))
                print("✓ spare_part表添加type_id字段成功")
            else:
                print("! spare_part表已存在type_id字段，跳过")
            
            db.session.commit()
            print("\n数据库迁移完成！")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ 迁移失败: {str(e)}")

if __name__ == '__main__':
    migrate_spare_part_type()
