#!/usr/bin/env python3
"""
Export SQLite database to a MySQL-compatible SQL dump.
Usage:
  python scripts/sqlite_to_mysql.py --sqlite app.db --out migrations/app_db_mysql_dump.sql --src-tz UTC --dst-tz Asia/Shanghai

Notes:
- Attempts to map common SQLite types to MySQL types.
- Converts datetime-like string columns between timezones when possible.
- Use this script to generate a dump file, then load into MySQL (after review and backup).
"""
import argparse
import sqlite3
import re
import sys
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

ISO_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?$")


def map_type_to_mysql(declared_type, pk, is_autoinc):
    if not declared_type:
        return 'TEXT'
    t = declared_type.upper()
    if 'INT' in t:
        if pk and is_autoinc:
            return 'INT AUTO_INCREMENT'
        return 'INT'
    if 'CHAR' in t or 'CLOB' in t or 'TEXT' in t:
        # choose VARCHAR(255) for short text, else TEXT
        return 'TEXT'
    if 'BLOB' in t:
        return 'BLOB'
    if 'REAL' in t or 'FLOA' in t or 'DOUB' in t:
        return 'DOUBLE'
    if 'BOOL' in t:
        return 'TINYINT(1)'
    if 'DATE' in t or 'TIME' in t:
        return 'DATETIME'
    # fallback
    return 'TEXT'


def quote_sql_value(val):
    if val is None:
        return 'NULL'
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
    # Try Python's fromisoformat; handle Z
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
                # treat naive as source tz
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=ZoneInfo(src_tz))
                # convert
                dt = dt.astimezone(ZoneInfo(dst_tz))
                vals.append(dt.strftime('%Y-%m-%d %H:%M:%S'))
                continue
        vals.append(val)
    return vals


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--sqlite', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--src-tz', default='UTC', help='Source timezone of stored datetimes (default UTC)')
    p.add_argument('--dst-tz', default='Asia/Shanghai', help='Target timezone for exported datetimes (default Asia/Shanghai)')
    args = p.parse_args()

    conn = sqlite3.connect(args.sqlite)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()]

    with open(args.out, 'w', encoding='utf-8') as f:
        f.write('-- MySQL dump generated from SQLite by sqlite_to_mysql.py\n')
        f.write('-- Review the dump before importing. BACKUP your target DB.\n\n')
        f.write('SET FOREIGN_KEY_CHECKS=0;\n\n')

        for tbl in tables:
            # get columns
            cols = cur.execute(f"PRAGMA table_info('{tbl}')").fetchall()
            # detect if table uses sqlite_autoincrement via sqlite_sequence
            is_autoinc = False
            pk_cols = [c['name'] for c in cols if c['pk']]
            # build create
            f.write(f"DROP TABLE IF EXISTS `{tbl}`;\n")
            f.write(f"CREATE TABLE `{tbl}` (\n")
            col_defs = []
            for c in cols:
                name = c['name']
                declared = c['type'] or ''
                pk = bool(c['pk'])
                mysql_type = map_type_to_mysql(declared, pk, False)
                dflt = c['dflt_value']
                notnull = c['notnull']
                part = f"  `{name}` {mysql_type}"
                if notnull:
                    part += ' NOT NULL'
                if dflt is not None:
                    # sqlite default may be '0' or '"str"'
                    part += f" DEFAULT {dflt}"
                col_defs.append(part)
            if pk_cols:
                pk_line = f"  PRIMARY KEY ({', '.join('`'+p+'`' for p in pk_cols)})"
                col_defs.append(pk_line)
            f.write(',\n'.join(col_defs))
            f.write('\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n\n')

            # dump rows
            rows = cur.execute(f"SELECT * FROM `{tbl}`").fetchall()
            if not rows:
                continue
            col_infos = [{'name':c['name'], 'type':c['type']} for c in cols]
            for row in rows:
                vals = convert_row_values(row, col_infos, args.src_tz, args.dst_tz)
                qvals = ', '.join(quote_sql_value(v) for v in vals)
                f.write(f"INSERT INTO `{tbl}` ({', '.join('`'+c['name']+'`' for c in cols)}) VALUES ({qvals});\n")
            f.write('\n')

        f.write('SET FOREIGN_KEY_CHECKS=1;\n')

    print('MySQL dump written to', args.out)

if __name__ == '__main__':
    main()
