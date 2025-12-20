from app import create_app, db
from app.chat_models import ChatConversation, ChatMessage, ChatParticipant, ChatAttachment

app = create_app()
with app.app_context():
    print("创建聊天表...")
    db.create_all()
    print("✓ 表创建完成")
    
    # 验证
    result = db.session.execute(db.text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' AND table_name LIKE 'chat%'
    """))
    
    tables = [r[0] for r in result]
    print(f"\n找到 {len(tables)} 个聊天表:")
    for t in tables:
        print(f"  ✓ {t}")
