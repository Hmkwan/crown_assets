#!/usr/bin/env python3
"""
Ensure minimal schema updates for SQLite app.db (adds missing columns used by models).
Run from project root: ./.venv/Scripts/python.exe scripts/ensure_schema.py --db app.db
"""
import argparse
import sqlite3

parser = argparse.ArgumentParser()
parser.add_argument('--db', default='app.db')
args = parser.parse_args()

conn = sqlite3.connect(args.db)
cur = conn.cursor()

def has_column(table, col):
    cur.execute(f"PRAGMA table_info('{table}')")
    cols = [r[1] for r in cur.fetchall()]
    return col in cols

changed = False
if not has_column('equipment', 'price'):
    print('Adding column equipment.price')
    cur.execute("ALTER TABLE equipment ADD COLUMN price REAL DEFAULT 0.0")
    changed = True
else:
    print('equipment.price exists')

if changed:
    conn.commit()
    print('Schema updated, committed')
else:
    print('No changes')

conn.close()
