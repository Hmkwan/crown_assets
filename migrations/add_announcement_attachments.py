"""添加公告附件表"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import AnnouncementAttachment

app = create_app()

with app.app_context():
    print("创建公告附件表...")
    
    try:
        # 创建表
        db.create_all()
        print("✓ 公告附件表创建成功")
        
        # 验证表是否存在
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        if 'announcement_attachment' in inspector.get_table_names():
            print("✓ 验证: announcement_attachment 表已存在")
            
            # 显示表结构
            columns = inspector.get_columns('announcement_attachment')
            print("\n表结构:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("✗ 错误: 表创建失败")
    
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
