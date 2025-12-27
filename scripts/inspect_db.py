import psycopg2
conn=psycopg2.connect('postgresql://postgres:difyai123456@localhost:15432/it_asset')
cur=conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
print('tables:', [r[0] for r in cur.fetchall()])
for t in ['workflow_template','workflow_node','chat_participant','chat_attachment','app_user']:
    cur.execute("select column_name,data_type from information_schema.columns where table_name=%s",(t,))
    cols=cur.fetchall()
    print('\n',t,'cols:',cols)
cur.close(); conn.close()
