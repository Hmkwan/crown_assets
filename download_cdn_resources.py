#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CDN资源本地化脚本 - 下载所有外部CDN资源到本地
运行此脚本将下载所有CDN依赖到 static/vendor/ 目录
"""

import os
import urllib.request
import ssl

# 创建SSL上下文（某些CDN需要）
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 要下载的CDN资源
CDN_RESOURCES = {
    # Bootstrap
    'bootstrap/css/bootstrap.min.css': 'https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css',
    'bootstrap/js/bootstrap.bundle.min.js': 'https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js',
    
    # jQuery
    'jquery/jquery-1.12.4.min.js': 'https://cdn.jsdelivr.net/npm/jquery@1.12.4/dist/jquery.min.js',
    
    # Moment.js
    'moment/moment.min.js': 'https://cdn.jsdelivr.net/npm/moment@2.29.4/moment.min.js',
    'moment/locale/zh-cn.js': 'https://cdn.jsdelivr.net/npm/moment@2.29.4/locale/zh-cn.js',
    'moment-timezone/moment-timezone-with-data.min.js': 'https://cdn.jsdelivr.net/npm/moment-timezone@0.5.43/builds/moment-timezone-with-data.min.js',
    
    # IE兼容性（可选）
    'polyfills/html5shiv.min.js': 'https://cdn.jsdelivr.net/npm/html5shiv@3.7.3/dist/html5shiv.min.js',
    'polyfills/respond.min.js': 'https://cdn.jsdelivr.net/npm/respond.js@1.4.2/dest/respond.min.js',
    'polyfills/es6-promise.auto.min.js': 'https://cdn.jsdelivr.net/npm/es6-promise@4.2.8/dist/es6-promise.auto.min.js',
    'polyfills/fetch.min.js': 'https://cdn.jsdelivr.net/npm/whatwg-fetch@3.6.2/dist/fetch.umd.js',
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENDOR_DIR = os.path.join(BASE_DIR, 'app', 'static', 'vendor')


def download_file(url, local_path):
    """下载单个文件"""
    try:
        print(f"下载: {url}")
        print(f"保存到: {local_path}")
        
        # 创建目录
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # 下载文件
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
            content = response.read()
            
        # 保存文件
        with open(local_path, 'wb') as f:
            f.write(content)
            
        print(f"✓ 下载成功: {os.path.basename(local_path)} ({len(content)} bytes)\n")
        return True
        
    except Exception as e:
        print(f"✗ 下载失败: {e}\n")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("CDN资源本地化工具")
    print("=" * 60)
    print(f"目标目录: {VENDOR_DIR}\n")
    
    success_count = 0
    failed_count = 0
    
    for local_path, url in CDN_RESOURCES.items():
        full_path = os.path.join(VENDOR_DIR, local_path)
        
        if download_file(url, full_path):
            success_count += 1
        else:
            failed_count += 1
    
    print("=" * 60)
    print(f"下载完成: 成功 {success_count} 个, 失败 {failed_count} 个")
    print("=" * 60)
    
    if success_count > 0:
        print("\n下一步:")
        print("1. 运行 python update_base_template.py 更新模板文件")
        print("2. 重启应用以使用本地资源")
        print("3. 测试页面加载速度是否改善")


if __name__ == '__main__':
    main()
