"""测试Socket.IO连接"""
import os
import sys

# 设置环境变量
os.environ['REDIS_URL'] = 'redis://redis:6379/0'

# Eventlet monkey patch
import eventlet
eventlet.monkey_patch()

from app import create_app

print("=" * 60)
print("测试Socket.IO连接")
print("=" * 60)

app = create_app()

# 测试Redis连接
print("\n1. 测试Redis连接:")
try:
    import redis
    redis_url = os.environ.get('REDIS_URL')
    r = redis.from_url(redis_url, socket_connect_timeout=5)
    r.ping()
    print(f"   ✓ Redis连接成功: {redis_url}")
except Exception as e:
    print(f"   ✗ Redis连接失败: {e}")

# 检查SocketIO实例
print("\n2. 检查SocketIO实例:")
if hasattr(app, 'socketio'):
    print(f"   ✓ app.socketio存在")
    print(f"   - async_mode: {app.socketio.async_mode}")
    print(f"   - message_queue: {app.socketio.server.eio.async_handlers}")
else:
    print(f"   ✗ app.socketio不存在")

# 测试Socket.IO连接
print("\n3. 测试Socket.IO客户端连接:")
try:
    from socketio import SimpleClient
    
    with app.app_context():
        # 创建测试用户session
        with app.test_client() as client:
            # 登录
            rv = client.post('/auth/login', data={
                'username': 'admin',
                'password': 'admin'
            }, follow_redirects=True)
            
            if rv.status_code == 200:
                print("   ✓ 登录成功")
                
                # 获取cookie
                cookies = client.cookie_jar
                cookie_str = '; '.join([f"{c.name}={c.value}" for c in cookies])
                
                # 测试Socket.IO握手
                sio = SimpleClient()
                try:
                    sio.connect(
                        'http://localhost:5020',
                        socketio_path='/socket.io',
                        headers={'Cookie': cookie_str}
                    )
                    print("   ✓ Socket.IO连接成功")
                    sio.disconnect()
                except Exception as e:
                    print(f"   ✗ Socket.IO连接失败: {e}")
            else:
                print(f"   ✗ 登录失败: {rv.status_code}")
                
except Exception as e:
    print(f"   ✗ 测试失败: {e}")

print("\n" + "=" * 60)
