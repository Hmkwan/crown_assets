#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证备份文件完整性
"""
import zipfile
import os

backup_file = r"C:\Users\it03.GD\Desktop\TEST\project_backups\project_backup_20251130_001405.zip"

print("=" * 70)
print("备份文件验证")
print("=" * 70)
print(f"文件: {os.path.basename(backup_file)}")
print(f"大小: {os.path.getsize(backup_file) / 1024:.2f} KB")

with zipfile.ZipFile(backup_file, 'r') as zf:
    names = zf.namelist()
    
    print(f"\n总文件数: {len(names)}")
    print(f"压缩包完整性: {'✓ 通过' if zf.testzip() is None else '✗ 失败'}")
    
    # 统计各类文件
    app_files = [n for n in names if n.startswith('app/')]
    py_files = [n for n in names if n.endswith('.py')]
    html_files = [n for n in names if n.endswith('.html')]
    js_files = [n for n in names if n.endswith('.js')]
    css_files = [n for n in names if n.endswith('.css')]
    md_files = [n for n in names if n.endswith('.md')]
    
    print("\n文件统计:")
    print(f"  ├─ app目录文件: {len(app_files)}")
    print(f"  ├─ Python文件: {len(py_files)}")
    print(f"  ├─ HTML模板: {len(html_files)}")
    print(f"  ├─ JavaScript: {len(js_files)}")
    print(f"  ├─ CSS样式: {len(css_files)}")
    print(f"  ├─ 文档文件: {len(md_files)}")
    print(f"  └─ 数据库: {'✓ 包含 app.db' if 'app.db' in names else '✗ 未包含'}")
    
    print("\n关键文件检查:")
    critical_files = [
        'app.py',
        'config.py',
        'requirements.txt',
        'app.db',
        'app/__init__.py',
        'app/models.py',
        'README_RESTORE.md',
        'BACKUP_INFO.json',
    ]
    
    for cf in critical_files:
        status = '✓' if cf in names else '✗'
        print(f"  {status} {cf}")
    
    print("\n=" * 70)
    print("✓ 备份文件验证完成！")
    print("=" * 70)
