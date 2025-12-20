#!/usr/bin/env python3
"""
Export SQLite database to a SQL Server-compatible SQL dump.
Usage:
  python scripts/sqlite_to_mssql.py --sqlite app.db --out migrations/app_db_mssql_dump.sql --src-tz UTC --dst-tz Asia/Shanghai

Notes:
- Attempts to map common SQLite types to SQL Server types.
- Converts datetime-like string columns between timezones when possible.
- Review the output before importing into production SQL Server.
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


def map_type_to_mssql(declared_type, pk, is_autoinc):
    if not declared_type:
        return 'NVARCHAR(MAX)'
    t = declared_type.upper()
    if 'INT' in t:
        if pk and is_autoinc:
            return 'INT IDENTITY(1,1)'
        return 'INT'
    if 'CHAR' in t or 'CLOB' in t or 'TEXT' in t:
        return 'NVARCHAR(MAX)'
    if 'BLOB' in t:
        return 'VARBINARY(MAX)'
    if 'REAL' in t or 'FLOA' in t or 'DOUB' in t:
        return 'FLOAT'
    if 'BOOL' in t:
        return 'BIT'
    if 'DATE' in t or 'TIME' in t:
        return 'DATETIME2'
    return 'NVARCHAR(MAX)'


def quote_sql_value(val):
    if val is None:
        return 'NULL'
    if isinstance(val, bool):
        return '1' if val else '0'
    if isinstance(val, (int, float)):
        return str(val)
    s = str(val)
    s = s.replace("'", "''")
    return "'{}'".format(s)


def try_parse_dt(s):
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
    vals = []
    for val, col in zip(row, col_infos):
        declared = col['type'] or ''
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
    p.add_argument('--sqlite', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--src-tz', default='UTC')
    p.add_argument('--dst-tz', default='Asia/Shanghai')
    args = p.parse_args()

    conn = sqlite3.connect(args.sqlite)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()]

    with open(args.out, 'w', encoding='utf-8') as f:
        f.write('-- SQL Server dump generated from SQLite by sqlite_to_mssql.py\n')
        f.write('-- Review the dump before importing. BACKUP your target DB.\n\n')

        for tbl in tables:
            cols = cur.execute(f"PRAGMA table_info('{tbl}')").fetchall()
            f.write(f"IF OBJECT_ID(N'dbo.{tbl}', N'U') IS NOT NULL DROP TABLE dbo.{tbl};\n")
            f.write(f"CREATE TABLE dbo.{tbl} (\n")
            col_defs = []
            pk_cols = [c['name'] for c in cols if c['pk']]
            for c in cols:
                name = c['name']
                declared = c['type'] or ''
                pk = bool(c['pk'])
                mssql_type = map_type_to_mssql(declared, pk, False)
                part = f"  [{name}] {mssql_type}"
                if c['notnull']:
                    part += ' NOT NULL'
                if c['dflt_value'] is not None:
                    part += f" DEFAULT {c['dflt_value']}"
                col_defs.append(part)
            if pk_cols:
                col_defs.append(f"  CONSTRAINT PK_{tbl} PRIMARY KEY ({', '.join('['+p+']' for p in pk_cols)})")
            f.write(',\n'.join(col_defs))
            f.write('\n);\n\n')

            rows = cur.execute(f"SELECT * FROM `{tbl}`").fetchall()
            if not rows:
                continue
            col_infos = [{'name':c['name'], 'type':c['type']} for c in cols]
            for row in rows:
                vals = convert_row_values(row, col_infos, args.src_tz, args.dst_tz)
                qvals = ', '.join(quote_sql_value(v) for v in vals)
                f.write(f"INSERT INTO dbo.{tbl} ({', '.join('['+c['name']+']' for c in cols)}) VALUES ({qvals});\n")
            f.write('\n')

    print('SQL Server dump written to', args.out)

if __name__ == '__main__':
    main()
