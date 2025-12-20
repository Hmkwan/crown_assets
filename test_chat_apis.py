#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试聊天API"""
from app import create_app
import json

app = create_app()

with app.test_client() as client:
    # 模拟登录
    with client.session_transaction() as sess:
        sess['_user_id'] = '1'
        sess['_fresh'] = True
    
    # 测试获取用户列表
    print('=== 测试 GET /api/chat/users ===')
    rv = client.get('/api/chat/users')
    print(f'状态码: {rv.status_code}')
    if rv.status_code == 200:
        data = json.loads(rv.data)
        print(f'用户数量: {len(data.get("users", []))}')
        if data.get('users'):
            print(f'第一个用户: {data["users"][0]}')
    else:
        print(f'错误: {rv.data.decode()[:200]}')
    
    # 测试获取会话列表
    print('\n=== 测试 GET /api/chat/conversations ===')
    rv = client.get('/api/chat/conversations')
    print(f'状态码: {rv.status_code}')
    if rv.status_code == 200:
        data = json.loads(rv.data)
        print(f'会话数量: {len(data.get("conversations", []))}')
        print(f'会话数据: {json.dumps(data, ensure_ascii=False, indent=2)}')
    else:
        print(f'错误: {rv.data.decode()[:200]}')
