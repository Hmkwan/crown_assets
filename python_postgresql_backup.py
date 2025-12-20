#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
纯Python实现的PostgreSQL备份（不需要pg_dump）

这是一个临时解决方案，使用psycopg2直接从数据库导出数据
注意：这个方案不如pg_dump完整，但可以在没有PostgreSQL客户端工具的情况下使用
"""
import os
import gzip
from datetime import datetime
from urllib.parse import urlparse

def python_backup_postgresql(db_uri, compress=True):
    """
    使用纯Python实现PostgreSQL备份
    
    Args:
        db_uri: 数据库连接URI
        compress: 是否压缩
    """
    try:
        import psycopg2
        from psycopg2 import sql
    except ImportError:
        return {
            'success': False,
            'message': '需要安装 psycopg2: pip install psycopg2-binary'
        }
    
    # 解析数据库URI
    parsed = urlparse(db_uri)
    
    try:
        # 连接数据库
        conn = psycopg2.connect(
            host=parsed.hostname or 'localhost',
            port=parsed.port or 5432,
            user=parsed.username or 'postgres',
            password=parsed.password,
            database=parsed.path.lstrip('/')
        )
        
        # 创建备份目录
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if compress:
            backup_filename = f'python_postgresql_backup_{timestamp}.sql.gz'
        else:
            backup_filename = f'python_postgresql_backup_{timestamp}.sql'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # 打开文件
        if compress:
            f = gzip.open(backup_path, 'wt', encoding='utf-8')
        else:
            f = open(backup_path, 'w', encoding='utf-8')
        
        cursor = conn.cursor()
        
        # 写入SQL头部
        f.write("-- PostgreSQL database dump (Python implementation)\n")
        f.write(f"-- Dump date: {datetime.now()}\n\n")
        
        # 获取所有表
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        tables = cursor.fetchall()
        
        print(f"找到 {len(tables)} 个表")
        
        for (table_name,) in tables:
            print(f"正在导出表: {table_name}")
            
            # 获取表结构
            cursor.execute(sql.SQL("""
                SELECT column_name, data_type, character_maximum_length,
                       is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s AND table_schema = 'public'
                ORDER BY ordinal_position
            """), [table_name])
            
            columns = cursor.fetchall()
            
            # 生成CREATE TABLE语句
            f.write(f"\n-- Table: {table_name}\n")
            f.write(f"DROP TABLE IF EXISTS {table_name} CASCADE;\n")
            f.write(f"CREATE TABLE {table_name} (\n")
            
            col_defs = []
            for col_name, data_type, max_len, nullable, default in columns:
                col_def = f"    {col_name} "
                
                # 数据类型
                if max_len:
                    col_def += f"{data_type}({max_len})"
                else:
                    col_def += data_type
                
                # 默认值
                if default:
                    col_def += f" DEFAULT {default}"
                
                # NOT NULL
                if nullable == 'NO':
                    col_def += " NOT NULL"
                
                col_defs.append(col_def)
            
            f.write(",\n".join(col_defs))
            f.write("\n);\n\n")
            
            # 获取数据
            cursor.execute(sql.SQL("SELECT * FROM {}").format(
                sql.Identifier(table_name)
            ))
            
            rows = cursor.fetchall()
            if rows:
                col_names = [desc[0] for desc in cursor.description]
                
                for row in rows:
                    # 生成INSERT语句
                    values = []
                    for val in row:
                        if val is None:
                            values.append('NULL')
                        elif isinstance(val, str):
                            # 转义单引号
                            escaped = val.replace("'", "''")
                            values.append(f"'{escaped}'")
                        elif isinstance(val, (int, float)):
                            values.append(str(val))
                        elif isinstance(val, datetime):
                            values.append(f"'{val.isoformat()}'")
                        else:
                            values.append(f"'{str(val)}'")
                    
                    f.write(f"INSERT INTO {table_name} ({', '.join(col_names)}) ")
                    f.write(f"VALUES ({', '.join(values)});\n")
                
                f.write("\n")
        
        # 关闭连接
        cursor.close()
        conn.close()
        f.close()
        
        # 获取文件大小
        file_size = os.path.getsize(backup_path)
        
        print(f"\n✓ 备份完成!")
        print(f"  文件: {backup_filename}")
        print(f"  大小: {file_size / 1024 / 1024:.2f} MB")
        print(f"  路径: {backup_path}")
        
        return {
            'success': True,
            'message': 'Python备份成功（注意：不包含索引、约束等）',
            'backup_filename': backup_filename,
            'backup_path': backup_path,
            'file_size': file_size
        }
        
    except Exception as e:
        import traceback
        return {
            'success': False,
            'message': f'备份失败: {str(e)}',
            'trace': traceback.format_exc()
        }


if __name__ == '__main__':
    # 测试备份
    from app import create_app
    
    app = create_app()
    with app.app_context():
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        
        print("="*70)
        print("纯Python PostgreSQL备份测试")
        print("="*70)
        print()
        
        result = python_backup_postgresql(db_uri, compress=True)
        
        if result.get('success'):
            print("\n✓ 备份成功!")
        else:
            print(f"\n✗ 备份失败: {result.get('message')}")
            if result.get('trace'):
                print(result['trace'])
