"""
模拟浏览器测试API
"""
import requests

session = requests.Session()

# 1. 登录
print("=" * 60)
print("1. 登录")
print("=" * 60)
login_url = "http://10.168.93.93:5020/auth/login"
login_data = {
    'username': 'admin',
    'password': 'admin',
    'submit': 'Login'
}

# 先GET获取CSRF token
resp = session.get(login_url)
print(f"GET /auth/login: {resp.status_code}")

# 从HTML提取CSRF token
import re
match = re.search(r'name="csrf_token" value="([^"]+)"', resp.text)
if match:
    csrf_token = match.group(1)
    login_data['csrf_token'] = csrf_token
    print(f"CSRF Token: {csrf_token[:20]}...")

# POST登录
resp = session.post(login_url, data=login_data, allow_redirects=True)
print(f"POST /auth/login: {resp.status_code}")
print(f"最终URL: {resp.url}")

# 2. 测试会话列表API
print("\n" + "=" * 60)
print("2. 测试 GET /api/chat/conversations")
print("=" * 60)
resp = session.get("http://10.168.93.93:5020/api/chat/conversations")
print(f"状态码: {resp.status_code}")
print(f"Content-Type: {resp.headers.get('Content-Type')}")

if resp.status_code == 200:
    try:
        data = resp.json()
        print(f"✓ JSON解析成功")
        print(f"会话数量: {len(data.get('conversations', []))}")
        for conv in data.get('conversations', []):
            print(f"  - 会话{conv['id']}: {conv.get('name', 'N/A')}")
    except Exception as e:
        print(f"❌ JSON解析失败: {e}")
        print(f"响应内容: {resp.text[:500]}")
else:
    print(f"❌ API失败: {resp.text[:200]}")

# 3. 测试用户列表API  
print("\n" + "=" * 60)
print("3. 测试 GET /api/chat/users")
print("=" * 60)
resp = session.get("http://10.168.93.93:5020/api/chat/users")
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"用户数量: {len(data.get('users', []))}")
