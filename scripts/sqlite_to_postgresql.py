#!/usr/bin/env python3
"""
Export SQLite database to a PostgreSQL-compatible SQL dump.
Usage:
  python scripts/sqlite_to_postgresql.py --sqlite app.db --out migrations/app_db_postgresql_dump.sql --src-tz UTC --dst-tz Asia/Shanghai

Notes:
- Maps SQLite types to PostgreSQL types
- Converts datetime-like string columns between timezones
- Generates sequences for auto-increment columns
"""
import argparse
import sqlite3
import re
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

ISO_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?$")


def map_type_to_postgresql(declared_type, pk, is_autoinc):
    """Map SQLite types to PostgreSQL types"""
    if not declared_type:
        return 'TEXT'
    t = declared_type.upper()
    if 'INT' in t:
        if pk and is_autoinc:
            return 'SERIAL'  # PostgreSQL auto-increment
        return 'INTEGER'
    if 'CHAR' in t or 'CLOB' in t or 'TEXT' in t:
        return 'TEXT'
    if 'BLOB' in t:
        return 'BYTEA'
    if 'REAL' in t or 'FLOA' in t or 'DOUB' in t:
        return 'DOUBLE PRECISION'
    if 'BOOL' in t:
        return 'BOOLEAN'
    if 'DATE' in t or 'TIME' in t:
        return 'TIMESTAMP'
    return 'TEXT'


def quote_sql_value(val):
    """Quote SQL values for PostgreSQL"""
    if val is None:
        return 'NULL'
    if isinstance(val, bool):
        return 'TRUE' if val else 'FALSE'
    if isinstance(val, (int, float)):
        return str(val)
    s = str(val)
    s = s.replace("'", "''")
    return "'{}'".format(s)


def try_parse_dt(s):
    """Try to parse ISO datetime string"""
    if not isinstance(s, str):
        return None
    s = s.strip()
    if not s:
        return None
    if not ISO_DATETIME_RE.match(s):
        return None
    try:
        if s.endswith('Z'):
            s2 = s[:-1] + '+00:00'
            return datetime.fromisoformat(s2)
        return datetime.fromisoformat(s)
    except Exception:
        return None


def convert_row_values(row, col_infos, src_tz, dst_tz):
    """Convert row values with timezone adjustment"""
    vals = []
    for val, col in zip(row, col_infos):
        if isinstance(val, str):
            dt = try_parse_dt(val)
            if dt and ZoneInfo and src_tz and dst_tz:
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=ZoneInfo(src_tz))
                dt = dt.astimezone(ZoneInfo(dst_tz))
                vals.append(dt.strftime('%Y-%m-%d %H:%M:%S'))
                continue
        vals.append(val)
    return vals


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--sqlite', required=True, help='Path to SQLite database file')
    p.add_argument('--out', required=True, help='Output SQL file path')
    p.add_argument('--src-tz', default='UTC', help='Source timezone (default: UTC)')
    p.add_argument('--dst-tz', default='Asia/Shanghai', help='Target timezone (default: Asia/Shanghai)')
    args = p.parse_args()

    conn = sqlite3.connect(args.sqlite)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row['name'] for row in cur.fetchall()]

    with open(args.out, 'w', encoding='utf-8') as f:
        f.write("-- PostgreSQL dump generated from SQLite\n")
        f.write(f"-- Source: {args.sqlite}\n")
        f.write(f"-- Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-- Timezone conversion: {} -> {}\n\n".format(args.src_tz, args.dst_tz))
        f.write("-- Start transaction\n")
        f.write("BEGIN;\n\n")

        for tbl in tables:
            # Get table schema
            cur.execute(f"PRAGMA table_info({tbl})")
            columns = cur.fetchall()
            
            col_infos = []
            col_defs = []
            pk_cols = []
            
            for col in columns:
                col_name = col['name']
                col_type = col['type']
                not_null = col['notnull']
                pk = col['pk']
                
                col_infos.append({'name': col_name, 'type': col_type, 'pk': pk})
                
                # Determine if auto-increment (simplified check)
                is_autoinc = (pk == 1 and 'INT' in col_type.upper())
                pg_type = map_type_to_postgresql(col_type, pk, is_autoinc)
                
                col_def = f'  "{col_name}" {pg_type}'
                if not_null and not is_autoinc:
                    col_def += ' NOT NULL'
                col_defs.append(col_def)
                
                if pk:
                    pk_cols.append(f'"{col_name}"')
            
            # Add primary key constraint
            if pk_cols:
                col_defs.append(f'  PRIMARY KEY ({", ".join(pk_cols)})')
            
            # Write CREATE TABLE
            f.write(f'-- Table: {tbl}\n')
            f.write(f'DROP TABLE IF EXISTS "{tbl}" CASCADE;\n')
            f.write(f'CREATE TABLE "{tbl}" (\n')
            f.write(',\n'.join(col_defs))
            f.write('\n);\n\n')
            
            # Insert data
            cur.execute(f'SELECT * FROM "{tbl}"')
            rows = cur.fetchall()
            
            if rows:
                f.write(f'-- Data for table: {tbl}\n')
                for row in rows:
                    converted = convert_row_values(row, col_infos, args.src_tz, args.dst_tz)
                    values = ', '.join(quote_sql_value(v) for v in converted)
                    col_names = ', '.join(f'"{c["name"]}"' for c in col_infos)
                    f.write(f'INSERT INTO "{tbl}" ({col_names}) VALUES ({values});\n')
                f.write('\n')
            
            # Reset sequences for SERIAL columns
            serial_cols = [c['name'] for c in col_infos if c['pk'] and 'INT' in (c['type'] or '').upper()]
            if serial_cols and rows:
                for col_name in serial_cols:
                    f.write(f"-- Reset sequence for {tbl}.{col_name}\n")
                    f.write(f"SELECT setval(pg_get_serial_sequence('\"{tbl}\"', '{col_name}'), ")
                    f.write(f"COALESCE((SELECT MAX(\"{col_name}\") FROM \"{tbl}\"), 1), true);\n\n")
        
        f.write("-- Commit transaction\n")
        f.write("COMMIT;\n")
        f.write("\n-- End of dump\n")

    conn.close()
    print(f"PostgreSQL dump created: {args.out}")


if __name__ == '__main__':
    main()
