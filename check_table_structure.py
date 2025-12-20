from app import create_app, db
app = create_app()
with app.app_context():
    result = db.session.execute(db.text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name='chat_conversation' 
        ORDER BY ordinal_position
    """))
    print("chat_conversation表结构:")
    for row in result:
        print(f"  {row[0]} - {row[1]}")
    
    result = db.session.execute(db.text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name='chat_message' 
        ORDER BY ordinal_position
        LIMIT 15
    """))
    print("\nchat_message表结构:")
    for row in result:
        print(f"  {row[0]} - {row[1]}")
