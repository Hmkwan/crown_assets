"""
测试聊天API端点
"""
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://10.168.93.93:5020"

# 先登录获取session
session = requests.Session()
login_data = {
    'username': 'admin',
    'password': 'admin'
}

print("=" * 80)
print("1. 测试登录")
print("=" * 80)
resp = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
print(f"状态码: {resp.status_code}")
print(f"Cookies: {session.cookies}")

print("\n" + "=" * 80)
print("2. 测试获取会话列表 GET /api/chat/conversations")
print("=" * 80)
resp = session.get(f"{BASE_URL}/api/chat/conversations")
print(f"状态码: {resp.status_code}")
print(f"Content-Type: {resp.headers.get('Content-Type')}")
print(f"响应内容: {resp.text[:500]}")
try:
    data = resp.json()
    print(f"会话数量: {len(data.get('conversations', []))}")
    for conv in data.get('conversations', []):
        print(f"  - ID:{conv['id']} 名称:{conv.get('name', 'N/A')} 类型:{conv['type']}")
except Exception as e:
    print(f"解析JSON失败: {e}")

print("\n" + "=" * 80)
print("3. 测试获取用户列表 GET /api/chat/users")
print("=" * 80)
resp = session.get(f"{BASE_URL}/api/chat/users")
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"用户数量: {len(data.get('users', []))}")
    for user in data.get('users', [])[:5]:
        print(f"  - ID:{user['id']} 用户名:{user['username']}")
else:
    print(f"错误: {resp.text[:200]}")

print("\n" + "=" * 80)
print("4. 测试管理统计 GET /api/chat/admin/statistics")
print("=" * 80)
resp = session.get(f"{BASE_URL}/api/chat/admin/statistics")
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"统计数据: {data}")
else:
    print(f"错误: {resp.text[:200]}")

print("\n" + "=" * 80)
print("5. 测试获取会话消息 GET /api/chat/conversations/5/messages")
print("=" * 80)
resp = session.get(f"{BASE_URL}/api/chat/conversations/5/messages")
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"消息数量: {len(data.get('messages', []))}")
    for msg in data.get('messages', [])[:3]:
        print(f"  - {msg.get('sender_name')}: {msg.get('content')[:30]}")
else:
    print(f"错误: {resp.text[:200]}")
