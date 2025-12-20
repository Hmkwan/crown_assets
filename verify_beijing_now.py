#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证 beijing_now 函数使用情况"""

import os
import re

print('\n' + '='*70)
print('  验证 beijing_now() 函数使用情况')
print('='*70 + '\n')

# 检查所有Python文件
app_dir = r'C:\Users\it03.GD\Desktop\TEST\app'
issues_found = []
files_checked = 0

for root, dirs, files in os.walk(app_dir):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            files_checked += 1
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # 检查是否使用了错误的 beijing_now()
                if 'beijing_now()' in content and 'get_beijing_now()' not in content:
                    # 可能是错误使用
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if 'beijing_now()' in line and 'get_beijing_now' not in line:
                            rel_path = os.path.relpath(filepath, r'C:\Users\it03.GD\Desktop\TEST')
                            issues_found.append({
                                'file': rel_path,
                                'line': i,
                                'content': line.strip()
                            })

print(f'已检查文件: {files_checked} 个\n')

if issues_found:
    print('❌ 发现问题:\n')
    for issue in issues_found:
        print(f'  文件: {issue["file"]}')
        print(f'  行号: {issue["line"]}')
        print(f'  代码: {issue["content"]}')
        print()
    print(f'总计: {len(issues_found)} 个问题\n')
else:
    print('✅ 没有发现 beijing_now() 使用错误!\n')

# 检查正确使用
print('='*70)
print('  正确使用统计')
print('='*70 + '\n')

correct_usage = 0
for root, dirs, files in os.walk(app_dir):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                correct_usage += content.count('get_beijing_now()')

print(f'get_beijing_now() 使用次数: {correct_usage}\n')

print('='*70)
print('  ✓ 检查完成!')
print('='*70 + '\n')
