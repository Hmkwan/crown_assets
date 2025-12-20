#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新base.html模板，使用本地CDN资源
运行此脚本将自动修改app/templates/base.html，替换所有CDN链接为本地路径
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, 'app', 'templates', 'base.html')
BACKUP_PATH = TEMPLATE_PATH + '.cdn_backup'

# CDN替换映射
REPLACEMENTS = [
    # Bootstrap CSS
    (
        r'https://cdn\.jsdelivr\.net/npm/bootstrap@4\.6\.2/dist/css/bootstrap\.min\.css',
        "{{ url_for('static', filename='vendor/bootstrap/css/bootstrap.min.css') }}"
    ),
    # Bootstrap JS
    (
        r'https://cdn\.jsdelivr\.net/npm/bootstrap@4\.6\.2/dist/js/bootstrap\.bundle\.min\.js',
        "{{ url_for('static', filename='vendor/bootstrap/js/bootstrap.bundle.min.js') }}"
    ),
    # jQuery
    (
        r'https://cdn\.jsdelivr\.net/npm/jquery@1\.12\.4/dist/jquery\.min\.js',
        "{{ url_for('static', filename='vendor/jquery/jquery-1.12.4.min.js') }}"
    ),
    # Moment.js
    (
        r'https://cdn\.jsdelivr\.net/npm/moment@2\.29\.4/moment\.min\.js',
        "{{ url_for('static', filename='vendor/moment/moment.min.js') }}"
    ),
    (
        r'https://cdn\.jsdelivr\.net/npm/moment@2\.29\.4/locale/zh-cn\.js',
        "{{ url_for('static', filename='vendor/moment/locale/zh-cn.js') }}"
    ),
    # Moment Timezone
    (
        r'https://cdn\.jsdelivr\.net/npm/moment-timezone@0\.5\.43/builds/moment-timezone-with-data\.min\.js',
        "{{ url_for('static', filename='vendor/moment-timezone/moment-timezone-with-data.min.js') }}"
    ),
    # html5shiv
    (
        r'https://cdn\.jsdelivr\.net/npm/html5shiv@3\.7\.3/dist/html5shiv\.min\.js',
        "{{ url_for('static', filename='vendor/polyfills/html5shiv.min.js') }}"
    ),
    # respond.js
    (
        r'https://cdn\.jsdelivr\.net/npm/respond\.js@1\.4\.2/dest/respond\.min\.js',
        "{{ url_for('static', filename='vendor/polyfills/respond.min.js') }}"
    ),
    # es6-promise
    (
        r'https://cdn\.jsdelivr\.net/npm/es6-promise@4\.2\.8/dist/es6-promise\.auto\.min\.js',
        "{{ url_for('static', filename='vendor/polyfills/es6-promise.auto.min.js') }}"
    ),
    # whatwg-fetch
    (
        r'https://cdn\.jsdelivr\.net/npm/whatwg-fetch@3\.6\.2/dist/fetch\.umd\.js',
        "{{ url_for('static', filename='vendor/polyfills/fetch.min.js') }}"
    ),
]


def update_template():
    """更新模板文件"""
    print("=" * 60)
    print("更新base.html模板 - 使用本地CDN资源")
    print("=" * 60)
    
    # 检查文件是否存在
    if not os.path.exists(TEMPLATE_PATH):
        print(f"错误: 找不到模板文件 {TEMPLATE_PATH}")
        return False
    
    # 读取原始内容
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份原始文件
    print(f"备份原始文件到: {BACKUP_PATH}")
    with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 应用替换
    updated_content = content
    replacement_count = 0
    
    for pattern, replacement in REPLACEMENTS:
        if re.search(pattern, updated_content):
            updated_content = re.sub(pattern, replacement, updated_content)
            replacement_count += 1
            print(f"✓ 替换: {pattern[:50]}...")
    
    # 保存更新后的文件
    if replacement_count > 0:
        with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("\n" + "=" * 60)
        print(f"更新完成: 共替换 {replacement_count} 个CDN链接")
        print("=" * 60)
        print("\n下一步:")
        print("1. 重启Flask应用")
        print("2. 清除浏览器缓存")
        print("3. 测试页面加载速度")
        print("\n如需恢复CDN版本，可以使用备份文件:")
        print(f"   {BACKUP_PATH}")
        return True
    else:
        print("\n警告: 没有找到需要替换的CDN链接")
        print("可能已经使用本地资源，或模板格式已更改")
        return False


def main():
    """主函数"""
    try:
        success = update_template()
        if success:
            print("\n✓ 模板更新成功!")
        else:
            print("\n✗ 模板更新失败或无需更新")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
