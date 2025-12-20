from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # 使用SQL直接更新
    sql = """
    UPDATE chat_conversation c
    SET last_message_id = m.id,
        last_message_time = m.created_date
    FROM (
        SELECT DISTINCT ON (conversation_id) 
            id, conversation_id, created_date
        FROM chat_message
        WHERE is_deleted = false
        ORDER BY conversation_id, created_date DESC
    ) m
    WHERE c.id = m.conversation_id
    """
    
    result = db.session.execute(text(sql))
    db.session.commit()
    
    print(f"更新了 {result.rowcount} 个会话的last_message")
