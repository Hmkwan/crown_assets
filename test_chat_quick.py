"""
聊天系统快速测试
使用说明:
1. 在浏览器访问 http://10.168.93.93:5020/auth/login 登录
2. 打开浏览器开发者工具 (F12)
3. 在Console中执行: document.cookie
4. 复制 session= 后面的值
5. 将值粘贴到下面的 SESSION_COOKIE 变量中
6. 运行: python test_chat_quick.py
"""
import requests
import json

BASE_URL = 'http://10.168.93.93:5020'

# ⚠️ 在这里粘贴你的session cookie值
# 例如: SESSION_COOKIE = 'eyJfZnJlc2giOnRydWUsImN...'
SESSION_COOKIE = ''  # 👈 将浏览器cookie粘贴到这里

def test_api():
    print("="*80)
    print("聊天API测试")
    print("="*80)
    
    if not SESSION_COOKIE:
        print("\n❌ 请先设置 SESSION_COOKIE!")
        print("\n步骤:")
        print("1. 浏览器登录 http://10.168.93.93:5020/auth/login")
        print("2. 按F12打开开发者工具")
        print("3. Console中执行: document.cookie")
        print("4. 复制 session= 后面的值")
        print("5. 粘贴到本文件的 SESSION_COOKIE 变量")
        return
    
    session = requests.Session()
    session.cookies.set('session', SESSION_COOKIE)
    
    print("\n[1] 测试获取用户列表...")
    resp = session.get(f'{BASE_URL}/api/chat/users')
    if resp.status_code == 200:
        users = resp.json().get('users', [])
        print(f"✓ 成功! 共 {len(users)} 个用户")
        for u in users[:3]:
            print(f"  - {u.get('real_name')} ({u.get('username')})")
    else:
        print(f"✗ 失败: HTTP {resp.status_code}")
        print(f"  {resp.text[:200]}")
        return
    
    print("\n[2] 测试获取会话列表...")
    resp = session.get(f'{BASE_URL}/api/chat/conversations')
    if resp.status_code == 200:
        convs = resp.json().get('conversations', [])
        print(f"✓ 成功! 共 {len(convs)} 个会话")
        for c in convs[:3]:
            print(f"  - 会话#{c['id']}: {c.get('name') or '(未命名)'}")
        
        # 如果有会话,测试获取消息
        if convs:
            conv_id = convs[0]['id']
            print(f"\n[3] 测试获取会话#{conv_id}的消息...")
            resp = session.get(f"{BASE_URL}/api/chat/conversations/{conv['id']}/messages")
            if resp.status_code == 200:
                msgs = resp.json().get('messages', [])
                print(f"✓ 成功! 共 {len(msgs)} 条消息")
                for m in msgs[-3:]:
                    print(f"  [{m['created_date']}] {m.get('sender_name')}: {m.get('content', '')[:40]}")
            else:
                print(f"✗ 失败: HTTP {resp.status_code}")
    else:
        print(f"✗ 失败: HTTP {resp.status_code}")
        print(f"  {resp.text[:200]}")
        return
    
    # 测试创建会话
    if users:
        print(f"\n[4] 测试创建会话...")
        data = {'type': 'direct', 'participant_ids': [users[0]['id']]}
        resp = session.post(
            f'{BASE_URL}/api/chat/conversations',
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        if resp.status_code in [200, 201]:
            conv = resp.json().get('conversation', {})
            print(f"✓ 成功! 会话#{conv['id']}")
            
            # 测试发送消息
            print(f"\n[5] 测试发送消息...")
            from datetime import datetime
            test_msg = f"[API测试] 消息测试 - {datetime.now().strftime('%H:%M:%S')}"
            data = {'content': test_msg, 'message_type': 'text'}
            resp = session.post(
                f"{BASE_URL}/api/chat/conversations/{conv['id']}/messages",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            if resp.status_code in [200, 201]:
                msg = resp.json().get('message', {})
                print(f"✓ 成功! 消息#{msg.get('id')}")
                print(f"  内容: {test_msg}")
            else:
                print(f"✗ 失败: HTTP {resp.status_code}")
        else:
            print(f"✗ 失败: HTTP {resp.status_code}")
    
    print("\n" + "="*80)
    print("✓ 所有测试完成!")
    print("="*80)

if __name__ == '__main__':
    test_api()
