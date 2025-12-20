#!/usr/bin/env python3
import sqlite3
conn=sqlite3.connect('app.db')
cur=conn.cursor()
rows=[]
try:
    rows.append(('equipment_count', cur.execute('SELECT COUNT(*) FROM equipment').fetchone()[0]))
except Exception as e:
    rows.append(('equipment_count_error', str(e)))
try:
    rows.append(('asset_lifecycle_count', cur.execute('SELECT COUNT(*) FROM asset_lifecycle').fetchone()[0]))
except Exception as e:
    rows.append(('asset_lifecycle_count_error', str(e)))
try:
    rows.append(('assetcost_count', cur.execute('SELECT COUNT(*) FROM asset_cost').fetchone()[0]))
except Exception as e:
    rows.append(('assetcost_count_error', str(e)))
try:
    rows.append(('purchase_events', cur.execute("SELECT COUNT(*) FROM asset_lifecycle WHERE event_type='purchase'").fetchone()[0]))
except Exception as e:
    rows.append(('purchase_events_error', str(e)))
try:
    rows.append(('nonzero_price_count', cur.execute('SELECT COUNT(*) FROM equipment WHERE price IS NOT NULL AND price>0').fetchone()[0]))
except Exception as e:
    rows.append(('nonzero_price_error', str(e)))
for k,v in rows:
    print(k, v)
conn.close()
