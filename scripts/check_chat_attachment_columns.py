from sqlalchemy import create_engine, text
url = 'postgresql://postgres:difyai123456@localhost:15432/it_asset'
eng = create_engine(url)
with eng.connect() as conn:
    res = conn.execute(text("SELECT column_name, is_nullable FROM information_schema.columns WHERE table_name='chat_attachment' ORDER BY ordinal_position"))
    for row in res.fetchall():
        print(f"{row[0]}\t{row[1]}")
