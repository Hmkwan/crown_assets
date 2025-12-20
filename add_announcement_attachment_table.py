"""添加公告附件表到数据库"""
import sys
sys.path.insert(0, '.')

from app import create_app, db

# 创建表的SQL
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS announcement_attachment (
    id SERIAL PRIMARY KEY,
    announcement_id INTEGER NOT NULL REFERENCES announcement(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(128),
    thumbnail_path VARCHAR(512),
    upload_user_id INTEGER NOT NULL REFERENCES app_user(id),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_date TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_announcement_attachment_announcement 
    ON announcement_attachment(announcement_id);
    
CREATE INDEX IF NOT EXISTS idx_announcement_attachment_upload_user 
    ON announcement_attachment(upload_user_id);
"""

app = create_app()

with app.app_context():
    print("正在创建公告附件表...")
    
    try:
        # 执行SQL
        db.session.execute(db.text(CREATE_TABLE_SQL))
        db.session.commit()
        print("✓ 公告附件表创建成功!")
        
        # 验证表是否创建
        result = db.session.execute(db.text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_name = 'announcement_attachment'"
        ))
        
        if result.fetchone():
            print("✓ 表验证成功!")
        else:
            print("✗ 表验证失败!")
            
    except Exception as e:
        db.session.rollback()
        print(f"✗ 创建失败: {e}")
