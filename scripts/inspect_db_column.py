from app import create_app, db
app = create_app()
with app.app_context():
    res = db.engine.execute("SELECT column_default, is_nullable FROM information_schema.columns WHERE table_name='chat_attachment' AND column_name='message_id'")
    for row in res:
        print('message_id column info:', row)
