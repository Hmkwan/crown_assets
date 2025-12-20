#!/usr/bin/env python3
import sqlite3,sys
from pathlib import Path

fn = sys.argv[1] if len(sys.argv)>1 else 'backups/app_backup_20251128_150734.db'
if not Path(fn).exists():
    print('ERROR: file not found', fn)
    sys.exit(2)

try:
    conn = sqlite3.connect(fn)
    cur = conn.cursor()
    def pragma_table_info(table):
        try:
            cur.execute(f"PRAGMA table_info({table});")
            return cur.fetchall()
        except Exception as e:
            return f'ERROR: {e}'

    print('Inspecting backup:', fn)
    for t in ('equipment','asset_lifecycle','asset_cost'):
        print('\n--- TABLE:', t)
        cols = pragma_table_info(t)
        print('columns:', cols)
        try:
            cur.execute(f'SELECT COUNT(*) FROM {t}')
            c = cur.fetchone()[0]
        except Exception as e:
            c = f'ERROR: {e}'
        print('count:', c)
        try:
            cur.execute(f'SELECT * FROM {t} LIMIT 10')
            rows = cur.fetchall()
        except Exception as e:
            rows = f'ERROR: {e}'
        print('sample rows:', rows)

    # Also try selected named columns from equipment if exist
    print('\n--- Checking selected equipment columns (id,name,price,purchase_date)')
    try:
        cur.execute("SELECT id, name, price, purchase_date FROM equipment LIMIT 10")
        print('selected sample:', cur.fetchall())
    except Exception as e:
        print('selected sample error:', e)

    conn.close()
except Exception as e:
    print('ERROR:', e)
    sys.exit(1)

sys.exit(0)
