import sqlite3
conn = sqlite3.connect('app.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
print("数据库中的表:")
for t in tables:
    print(f"  - {t[0]}")
    cursor.execute(f"PRAGMA table_info({t[0]})")
    cols = cursor.fetchall()
    for col in cols[:5]:  # 只显示前5列
        print(f"      {col[1]} ({col[2]})")
conn.close()
