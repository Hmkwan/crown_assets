"""创建聊天系统数据库表"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.chat_models import ChatConversation, ChatParticipant, ChatMessage, ChatAttachment, ChatPermission

app = create_app()

with app.app_context():
    print("创建聊天系统数据库表...")
    
    try:
        # 创建表
        db.create_all()
        print("✓ 聊天系统表创建成功")
        
        # 验证表是否存在
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        required_tables = [
            'chat_conversation',
            'chat_participant',
            'chat_message',
            'chat_attachment',
            'chat_permission'
        ]
        
        print("\n验证表结构:")
        for table_name in required_tables:
            if table_name in inspector.get_table_names():
                print(f"  ✓ {table_name}")
                columns = inspector.get_columns(table_name)
                print(f"    字段数: {len(columns)}")
            else:
                print(f"  ✗ {table_name} - 未找到")
        
        print("\n✓ 聊天系统数据库初始化完成")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
