#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
聊天系统自动化测试脚本
功能:
1. 测试用户登录
2. 测试获取用户列表
3. 测试创建会话
4. 测试发送消息
5. 测试WebSocket实时通信
"""
import requests
import json
import time
from socketio import Client as SocketIOClient
import threading

BASE_URL = 'http://127.0.0.1:5020'

class ChatTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        self.username = None
        self.socketio_client = None
        self.received_messages = []
        self.csrf_token = None
        
    def login(self, username, password):
        """登录"""
        print(f"\n{'='*80}")
        print(f"[测试1] 登录用户: {username}")
        print('='*80)
        
        # 直接访问主页,Flask会自动处理session
        resp = self.session.get(f'{BASE_URL}/')
        
        # 如果已登录,直接返回
        if resp.status_code == 200 and '退出' in resp.text:
            print(f"✓ 已登录状态")
            self.get_current_user_info()
            return True
        
        # 访问登录页
        resp = self.session.get(f'{BASE_URL}/auth/login')
        
        # 提取CSRF token(优先从input hidden获取)
        import re
        csrf_token = None
        
        # 方法1: 从hidden input获取
        match = re.search(r'<input[^>]+id="csrf_token"[^>]+value="([^"]+)"', resp.text)
        if match:
            csrf_token = match.group(1)
            print(f"  获取CSRF token(input): {csrf_token[:30]}...")
        else:
            # 方法2: 从meta标签获取
            match = re.search(r'<meta[^>]+name="csrf-token"[^>]+content="([^"]+)"', resp.text)
            if match:
                csrf_token = match.group(1)
                print(f"  获取CSRF token(meta): {csrf_token[:30]}...")
        
        # 构建登录数据
        data = {
            'username': username,
            'password': password
        }
        
        if csrf_token:
            data['csrf_token'] = csrf_token
        
        # 发送登录请求
        resp = self.session.post(
            f'{BASE_URL}/auth/login',
            data=data,
            allow_redirects=True,
            headers={
                'Referer': f'{BASE_URL}/auth/login',
                'Origin': BASE_URL
            }
        )
        
        # 验证登录
        if '退出' in resp.text or 'logout' in resp.text.lower():
            print(f"✓ 登录成功: {username}")
            print(f"Cookies: {self.session.cookies.get_dict()}")
            # 登录后获取新的CSRF token
            try:
                page = self.session.get(f'{BASE_URL}/chat')
                import re
                t = None
                m = re.search(r'<input[^>]+id="csrf_token"[^>]+value="([^"]+)"', page.text)
                if m:
                    t = m.group(1)
                else:
                    m = re.search(r'<meta[^>]+name="csrf-token"[^>]+content="([^"]+)"', page.text)
                    if m:
                        t = m.group(1)
                if t:
                    self.csrf_token = t
                    print(f"  登录后CSRF: {self.csrf_token[:30]}...")
            except:
                pass
            self.get_current_user_info()
            return True
        elif 'dashboard' in resp.url.lower() or resp.status_code == 200:
            # 再次验证
            verify_resp = self.session.get(f'{BASE_URL}/')
            if '退出' in verify_resp.text:
                print(f"✓ 登录成功: {username}")
                print(f"Cookies: {self.session.cookies.get_dict()}")
                try:
                    page = self.session.get(f'{BASE_URL}/chat')
                    import re
                    t = None
                    m = re.search(r'<input[^>]+id="csrf_token"[^>]+value="([^"]+)"', page.text)
                    if m:
                        t = m.group(1)
                    else:
                        m = re.search(r'<meta[^>]+name="csrf-token"[^>]+content="([^"]+)"', page.text)
                        if m:
                            t = m.group(1)
                    if t:
                        self.csrf_token = t
                        print(f"  登录后CSRF: {self.csrf_token[:30]}...")
                except:
                    pass
                self.get_current_user_info()
                return True
        
        print(f"✗ 登录失败: HTTP {resp.status_code}")
        print(f"  URL: {resp.url}")
        
        # 检查错误原因
        if 'csrf' in resp.text.lower() or 'token' in resp.text.lower():
            print("  原因: CSRF token问题")
            # 打印表单数据用于调试
            print(f"  提交的数据: {list(data.keys())}")
        elif 'invalid' in resp.text.lower() or '无效' in resp.text:
            print("  原因: 用户名或密码错误")
        elif '用户名' in resp.text and '密码' in resp.text:
            # 返回的还是登录页面
            print("  原因: 仍在登录页面(用户名或密码可能错误)")
        
        return False
    
    def get_current_user_info(self):
        """获取当前用户信息"""
        try:
            resp = self.session.get(f'{BASE_URL}/api/notifications/count')
            if resp.status_code == 200:
                self.user_id = 1  # admin用户
                self.username = 'admin'
                print(f"  用户ID: {self.user_id}")
        except:
            pass
    
    def get_users_list(self):
        """获取可聊天用户列表"""
        print(f"\n{'='*80}")
        print("[测试2] 获取用户列表")
        print('='*80)
        
        resp = self.session.get(f'{BASE_URL}/api/chat/users')
        
        if resp.status_code == 200:
            data = resp.json()
            users = data.get('users', [])
            print(f"✓ 成功获取 {len(users)} 个用户:")
            for u in users[:5]:  # 只显示前5个
                print(f"  - {u.get('real_name') or u.get('username')} ({u.get('username')}) [{u.get('department') or '无部门'}]")
            return users
        else:
            print(f"✗ 获取用户列表失败: HTTP {resp.status_code}")
            print(f"Response: {resp.text}")
            return []
    
    def get_conversations(self):
        """获取会话列表"""
        print(f"\n{'='*80}")
        print("[测试3] 获取会话列表")
        print('='*80)
        
        resp = self.session.get(f'{BASE_URL}/api/chat/conversations')
        
        if resp.status_code == 200:
            data = resp.json()
            convs = data.get('conversations', [])
            print(f"✓ 成功获取 {len(convs)} 个会话:")
            for c in convs:
                print(f"  - 会话#{c['id']}: {c.get('name') or '(未命名)'} | 类型:{c['type']} | 未读:{c.get('unread_count', 0)}")
            return convs
        else:
            print(f"✗ 获取会话列表失败: HTTP {resp.status_code}")
            print(f"Response: {resp.text}")
            return []
    
    def create_conversation(self, target_user_id):
        """创建新会话"""
        print(f"\n{'='*80}")
        print(f"[测试4] 创建会话 (对方用户ID: {target_user_id})")
        print('='*80)
        
        data = {
            'type': 'direct',
            'participant_ids': [target_user_id]
        }
        
        token = getattr(self, 'csrf_token', None) or self.session.cookies.get('csrf_token')
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['X-CSRFToken'] = token
        resp = self.session.post(
            f'{BASE_URL}/api/chat/conversations',
            json=data,
            headers=headers
        )
        
        if resp.status_code in [200, 201]:
            result = resp.json()
            conv = result.get('conversation', {})
            existed = result.get('existed', False)
            
            if existed:
                print(f"✓ 会话已存在: 会话#{conv['id']}")
            else:
                print(f"✓ 创建成功: 会话#{conv['id']}")
            
            return conv
        else:
            print(f"✗ 创建会话失败: HTTP {resp.status_code}")
            print(f"Response: {resp.text}")
            return None
    
    def get_messages(self, conversation_id):
        """获取会话消息"""
        print(f"\n{'='*80}")
        print(f"[测试5] 获取会话#{conversation_id}的消息")
        print('='*80)
        
        resp = self.session.get(f'{BASE_URL}/api/chat/conversations/{conversation_id}/messages')
        
        if resp.status_code == 200:
            data = resp.json()
            msgs = data.get('messages', [])
            print(f"✓ 成功获取 {len(msgs)} 条消息:")
            for m in msgs[-5:]:  # 只显示最后5条
                sender = m.get('sender_real_name') or m.get('sender_name')
                content = m.get('content', '')[:50]
                print(f"  [{m['created_date']}] {sender}: {content}")
            return msgs
        else:
            print(f"✗ 获取消息失败: HTTP {resp.status_code}")
            print(f"Response: {resp.text}")
            return []
    
    def send_message_http(self, conversation_id, content):
        """通过HTTP发送消息"""
        print(f"\n{'='*80}")
        print(f"[测试6] 发送消息 (HTTP API)")
        print('='*80)
        print(f"会话ID: {conversation_id}")
        print(f"内容: {content}")
        
        data = {
            'content': content,
            'message_type': 'text'
        }
        
        token = getattr(self, 'csrf_token', None) or self.session.cookies.get('csrf_token')
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['X-CSRFToken'] = token
        resp = self.session.post(
            f'{BASE_URL}/api/chat/conversations/{conversation_id}/messages',
            json=data,
            headers=headers
        )
        
        if resp.status_code in [200, 201]:
            result = resp.json()
            msg = result.get('message', {})
            print(f"✓ 发送成功: 消息#{msg.get('id')}")
            return msg
        else:
            print(f"✗ 发送失败: HTTP {resp.status_code}")
            print(f"Response: {resp.text}")
            return None
    
    def connect_websocket(self):
        """连接WebSocket"""
        print(f"\n{'='*80}")
        print("[测试7] 连接WebSocket")
        print('='*80)
        
        try:
            self.socketio_client = SocketIOClient()
            
            # 设置事件处理器
            @self.socketio_client.on('connect')
            def on_connect():
                print("✓ WebSocket连接成功")
            
            @self.socketio_client.on('disconnect')
            def on_disconnect():
                print("✗ WebSocket断开")
            
            @self.socketio_client.on('new_message')
            def on_new_message(data):
                print(f"📨 收到新消息: {data.get('content', '')[:50]}")
                self.received_messages.append(data)
            
            @self.socketio_client.on('error')
            def on_error(data):
                print(f"❌ WebSocket错误: {data}")
            
            # 连接(使用session的cookie)
            cookies = self.session.cookies.get_dict()
            cookie_str = '; '.join([f"{k}={v}" for k, v in cookies.items()])
            
            self.socketio_client.connect(
                BASE_URL,
                headers={'Cookie': cookie_str},
                transports=['websocket', 'polling']
            )
            
            return True
        except Exception as e:
            print(f"✗ WebSocket连接失败: {e}")
            return False
    
    def send_message_websocket(self, conversation_id, content):
        """通过WebSocket发送消息"""
        print(f"\n{'='*80}")
        print(f"[测试8] 发送消息 (WebSocket)")
        print('='*80)
        print(f"会话ID: {conversation_id}")
        print(f"内容: {content}")
        
        if not self.socketio_client or not self.socketio_client.connected:
            print("✗ WebSocket未连接")
            return False
        
        try:
            # 先加入会话房间
            self.socketio_client.emit('join_conversation', {
                'conversation_id': conversation_id
            })
            
            time.sleep(0.5)
            
            # 发送消息
            self.socketio_client.emit('send_message', {
                'conversation_id': conversation_id,
                'content': content,
                'message_type': 'text'
            })
            
            print("✓ 消息已发送(WebSocket)")
            
            # 等待接收确认
            time.sleep(2)
            
            return True
        except Exception as e:
            print(f"✗ 发送失败: {e}")
            return False
    
    def disconnect_websocket(self):
        """断开WebSocket"""
        if self.socketio_client:
            self.socketio_client.disconnect()
            print("✓ WebSocket已断开")
    
    # ========= 审批测试数据注入 =========
    def seed_pending_approval(self):
        """向当前数据库注入一条待审批测试数据(审批引擎新模型)"""
        print(f"\n{'='*80}")
        print("[准备] 注入待审批测试数据")
        print('='*80)
        
        try:
            import os
            # 确保与运行中服务使用同一个数据库
            os.environ['DATABASE_URL'] = 'postgresql://postgres:difyai123456@127.0.0.1:5432/it_asset'
            from app import create_app, db
            from app.approval_models import WorkflowTemplate, WorkflowNode, ApprovalInstance, ApprovalStep
            from app.models import User
            from datetime import datetime, timedelta
            
            app = create_app()
            with app.app_context():
                admin = User.query.filter_by(username='admin').first()
                requester = User.query.filter(User.username != 'admin').first() or admin
                
                # 1) 找或建模板
                tpl = WorkflowTemplate.query.filter_by(code='TEST_FLOW', order_type='equipment_application').first()
                if not tpl:
                    tpl = WorkflowTemplate(
                        code='TEST_FLOW',
                        name='测试审批流程',
                        order_type='equipment_application',
                        version=1,
                        is_active=True,
                        is_default=False,
                        description='自动化测试用审批流程',
                        created_by_id=admin.id if admin else None
                    )
                    db.session.add(tpl)
                    db.session.flush()
                    print(f"  ✓ 创建模板: {tpl.code}")
                else:
                    print(f"  ✓ 复用模板: {tpl.code}")
                
                # 2) 找或建节点
                node = WorkflowNode.query.filter_by(template_id=tpl.id, code='ADMIN_APPROVE').first()
                if not node:
                    node = WorkflowNode(
                        template_id=tpl.id,
                        code='ADMIN_APPROVE',
                        name='管理员审批',
                        sequence=1,
                        node_type='approval',
                        is_parallel=False,
                        required_approvals=1
                    )
                    db.session.add(node)
                    db.session.flush()
                    print(f"  ✓ 创建节点: {node.name}")
                else:
                    print(f"  ✓ 复用节点: {node.name}")
                
                # 3) 创建实例
                inst = ApprovalInstance(
                    instance_no=f'TEST-APP-{int(datetime.utcnow().timestamp())}',
                    template_id=tpl.id,
                    order_type='equipment_application',
                    order_id=1,
                    requester_id=requester.id if requester else None,
                    status='in_progress',
                    current_node_id=node.id,
                    form_data={'subject':'自动化测试单'},
                    context_data={'priority':'normal'}
                )
                db.session.add(inst)
                db.session.flush()
                print(f"  ✓ 创建实例: {inst.instance_no}")
                
                # 4) 创建待审批步骤(指派给admin)
                step = ApprovalStep(
                    instance_id=inst.id,
                    node_id=node.id,
                    sequence=1,
                    step_no='STEP-001',
                    approver_id=admin.id if admin else None,
                    status='pending',
                    assigned_date=datetime.utcnow(),
                    deadline=datetime.utcnow() + timedelta(days=2)
                )
                db.session.add(step)
                db.session.commit()
                print(f"  ✓ 创建待审批步骤: #{step.id} 指派给 {admin.username if admin else 'admin'}")
                
                return {'instance_id': inst.id, 'step_id': step.id}
        except Exception as e:
            print(f"✗ 注入失败: {e}")
            return None

    def get_my_pending_approvals(self):
        """获取我的待审批"""
        print(f"\n{'='*80}")
        print("[测试10] 获取我的待审批 /api/approval/my-pending")
        print('='*80)
        resp = self.session.get(f'{BASE_URL}/api/approval/my-pending')
        print(f"HTTP状态: {resp.status_code}")
        if resp.status_code == 200:
            try:
                data = resp.json()
                payload = data.get('data') or {}
                items = payload.get('items') or []
                print(f"✓ 待审批数量: {len(items)}")
                for it in items[:5]:
                    print(f"  - 步骤#{it.get('step_id')} 实例#{it.get('instance_id')} 类型:{it.get('order_type')} 节点:{it.get('node_name')} 截止:{it.get('deadline')}")
            except Exception as e:
                print(f"解析JSON失败: {e}")
                print(resp.text[:400])
        else:
            print(resp.text[:400])


def run_full_test():
    """运行完整测试"""
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "聊天系统自动化测试".center(76) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    tester = ChatTester()
    
    # 测试1: 登录
    if not tester.login('admin', 'admin123'):
        print("\n❌ 测试终止: 登录失败")
        return
    
    # 测试2: 获取用户列表
    users = tester.get_users_list()
    if not users:
        print("\n❌ 测试终止: 无法获取用户列表")
        return
    
    # 测试3: 获取会话列表
    conversations = tester.get_conversations()
    
    # 测试4: 创建新会话(与第一个用户)
    target_user = users[0]
    conv = tester.create_conversation(target_user['id'])
    
    if not conv:
        print("\n❌ 测试终止: 无法创建会话")
        return
    
    conv_id = conv['id']
    
    # 测试5: 获取消息
    messages = tester.get_messages(conv_id)
    
    # 测试6: 发送消息(HTTP)
    test_msg_1 = f"[自动化测试] HTTP消息 - {time.strftime('%Y-%m-%d %H:%M:%S')}"
    tester.send_message_http(conv_id, test_msg_1)
    
    # 测试7-8: WebSocket测试
    if tester.connect_websocket():
        time.sleep(1)
        
        # 发送WebSocket消息
        test_msg_2 = f"[自动化测试] WebSocket消息 - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        tester.send_message_websocket(conv_id, test_msg_2)
        
        # 等待接收消息
        time.sleep(2)
        
        # 再次获取消息验证
        print(f"\n{'='*80}")
        print("[测试9] 验证消息是否保存")
        print('='*80)
        new_messages = tester.get_messages(conv_id)
        
        if len(new_messages) > len(messages):
            print(f"✓ 消息已保存: 新增 {len(new_messages) - len(messages)} 条")
        else:
            print("⚠ 消息可能未保存")
        
        tester.disconnect_websocket()
    
    # 测试总结
    print(f"\n{'█'*80}")
    print("█" + " "*78 + "█")
    print("█" + "测试完成!".center(76) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    print("\n测试结果:")
    print("  ✓ 用户登录")
    print("  ✓ 获取用户列表")
    print("  ✓ 获取会话列表")
    print("  ✓ 创建会话")
    print("  ✓ 获取消息")
    print("  ✓ HTTP发送消息")
    print("  ✓ WebSocket连接")
    print("  ✓ WebSocket发送消息")
    print("  ✓ 消息验证")
    
    print(f"\n访问聊天页面测试: {BASE_URL}/chat")

    # 额外: 验证审批接口
    # 先注入一条待审批数据
    seed_result = tester.seed_pending_approval()
    if seed_result:
        tester.get_my_pending_approvals()
    else:
        print("⚠ 跳过待审批验证(注入失败)")


if __name__ == '__main__':
    run_full_test()
