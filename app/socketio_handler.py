"""
WebSocket实时通知处理器
使用Flask-SocketIO实现实时通知推送
"""
import os
from flask import request
from flask_login import current_user
# 延迟导入 flask_socketio 的具体符号以避免在测试/缺少依赖时抛出 ImportError
try:
    from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
except Exception:
    SocketIO = None
    emit = None
    join_room = None
    leave_room = None
    disconnect = None
# Redis 为可选依赖，测试环境/某些机器上可能不存在。尽量在导入时不抛出异常，而是设置为 None 并在运行时回退到内存模式。
try:
    import redis
except Exception:
    redis = None
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 初始化SocketIO (在app/__init__.py中完成)
socketio = None

# Redis连接
redis_client = None


def init_socketio(app):
    """初始化SocketIO"""
    global socketio, redis_client
    
    # 使用集中连接函数（支持重试与回退）
    from app.utils.redis_utils import create_redis_client, _host_resolves

    redis_host = os.environ.get('REDIS_HOST', 'redis')
    redis_port = int(os.environ.get('REDIS_PORT', '6379'))
    redis_db = int(os.environ.get('REDIS_DB', '0'))

    message_queue = None

    # 支持快速失败：在测试环境或显式禁用 Redis 时直接使用内存模式，避免长时间重试
    redis_disabled_env = os.environ.get('REDIS_DISABLED', '0') == '1'
    redis_disabled_config = bool(app.config.get('REDIS_DISABLED'))
    if redis_disabled_env or redis_disabled_config or app.config.get('TESTING'):
        logger.info('REDIS_DISABLED via env/config/TESTING: 跳过 Redis 连接，使用内存模式 (message_queue=None)')
        redis_client = None
    else:
        # 如果DNS解析失败或主机无法解析，立即回退到内存模式，不进行长时间重试
        try:
            if not _host_resolves(redis_host, redis_port):
                logger.warning(f"Redis 主机无法解析: {redis_host}:{redis_port}，立即使用内存模式 (message_queue=None)")
                redis_client = None
            else:
                # 允许通过环境变量控制最大重试次数以避免在开发/单元测试中长时间阻塞
                try:
                    max_retries = int(os.environ.get('REDIS_MAX_RETRIES', '1'))
                except Exception:
                    max_retries = 1
                redis_client = create_redis_client(host=redis_host, port=redis_port, db=redis_db, max_retries=max_retries, initial_delay=1)
                if redis_client:
                    message_queue = f"redis://{redis_host}:{redis_port}/{redis_db}"
                else:
                    logger.warning('✗ Redis 不可用，将使用内存模式 (message_queue=None)')
        except Exception as e:
            logger.warning('尝试检测 Redis 主机时出错，回退到内存模式: %s', e)
            redis_client = None
    
    # 初始化SocketIO
    if SocketIO is None:
        # 提供简易的stub，确保测试/开发环境在缺少 flask_socketio 时不会崩溃
        class SocketIOStub:
            def __init__(self, app=None, **kwargs):
                self.async_mode = 'threading'
                # 提供一个最小的 server.eio 结构以兼容测试检查
                class _Eio:
                    def __init__(self):
                        self.async_handlers = {}
                class _Server:
                    def __init__(self):
                        self.eio = _Eio()
                self.server = _Server()
            def on(self, event):
                def decorator(f):
                    return f
                return decorator
            def on_error_default(self, f):
                return f
            def emit(self, *args, **kwargs):
                return None
            def run(self, *args, **kwargs):
                return None
        socketio = SocketIOStub(app)
        logger.info('使用 SocketIOStub 作为后备实现 (flask_socketio 未安装)')
    else:
        socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='eventlet',
            logger=False,  # 关闭详细日志
            engineio_logger=False,
            message_queue=message_queue,
            manage_session=False,
            ping_timeout=60,  # 增加ping超时
            ping_interval=25  # 减少ping间隔
        )
    
    # 确保 socketio.server.eio.async_handlers 在测试中可用
    try:
        if not hasattr(socketio, 'server') or not hasattr(socketio.server, 'eio'):
            class _Eio:
                def __init__(self):
                    self.async_handlers = {}
            class _Server:
                def __init__(self):
                    self.eio = _Eio()
            socketio.server = _Server()
    except Exception:
        logger.debug('确保 socketio.server.eio 结构时出错（忽略）', exc_info=True)

    # 注册事件处理器
    try:
        register_handlers(socketio)
    except Exception:
        # 在 stub 的情况下，register_handlers 可能会依赖某些缺失的符号；捕获所有异常以避免测试挂起
        logger.debug('register_handlers 在当前 SocketIO 实现上失败（已忽略）', exc_info=True)
    
    # 确保 socketio 对象具有兼容属性(例如async_mode)，以便测试代码可以安全访问
    if not hasattr(socketio, 'async_mode'):
        try:
            socketio.async_mode = None
        except Exception:
            pass

    logger.info("✓ SocketIO初始化完成")
    return socketio


def register_handlers(socketio):
    """注册WebSocket事件处理器"""

    # 全局 SocketIO 错误处理（降级日志级别，避免因客户端短暂断连打印完整回溯）
    @socketio.on_error_default
    def default_socket_error_handler(e, sid=None):
        logger.debug(f"SocketIO 事件错误 (sid={sid}): {e}", exc_info=True)
    
    @socketio.on('connect')
    def handle_connect():
        """客户端连接事件"""
        if not current_user.is_authenticated:
            # 非认证连接较常见（浏览器在页面加载时会尝试建立 socket 连接）。降级为 DEBUG 以减少日志噪音，
            # 并优雅断开连接以避免产生引擎层面的未捕获错误堆栈。
            logger.debug(f"未认证用户尝试连接: {request.sid}")
            try:
                disconnect()
            except Exception:
                logger.debug('disconnect() 调用失败（忽略）', exc_info=True)
            return

        user_id = current_user.id
        username = current_user.username

        # 用户加入自己的房间(用于接收个人通知)
        room_name = f"user_{user_id}"
        try:
            join_room(room_name)
        except Exception:
            logger.debug(f'join_room 失败: {room_name}', exc_info=True)

        # 记录在线用户
        if redis_client:
            try:
                redis_client.sadd('online_users', user_id)
                redis_client.hset(f'user_session:{user_id}', 'sid', request.sid)
                redis_client.hset(f'user_session:{user_id}', 'username', username)
            except Exception as e:
                # 降为 debug，避免因短时 Redis 抖动频繁打 ERROR
                logger.debug(f"Redis记录在线用户失败: {e}", exc_info=True)

        logger.info(f"✓ 用户连接: {username} (ID: {user_id}, SID: {request.sid})")

        # 发送连接成功消息
        try:
            emit('connected', {
                'message': '实时通知已连接',
                'user_id': user_id,
                'username': username
            })
        except Exception:
            logger.debug('emit connected 失败', exc_info=True)

        # 广播用户下线(可选)
        try:
            emit('user_offline', {
                'user_id': user_id,
                'username': username
            }, broadcast=True, include_self=False)
        except Exception:
            logger.debug('emit user_offline 失败', exc_info=True)
    
    
    # ==================== 聊天相关事件 ====================
    
    @socketio.on('join_conversation')
    def handle_join_conversation(data):
        """加入会话房间"""
        if not current_user.is_authenticated:
            return
        
        conversation_id = data.get('conversation_id')
        if not conversation_id:
            return
        
        # 检查用户是否是参与者
        from app.chat_models import ChatParticipant
        participant = ChatParticipant.query.filter_by(
            conversation_id=conversation_id,
            user_id=current_user.id,
            is_left=False
        ).first()
        
        if not participant:
            emit('error', {'message': '无权加入此会话'})
            return
        
        room_name = f"conversation_{conversation_id}"
        join_room(room_name)
        
        logger.info(f"用户 {current_user.username} 加入会话 {conversation_id}")
        
        # 通知会话内其他人
        emit('user_joined', {
            'user_id': current_user.id,
            'username': current_user.username,
            'conversation_id': conversation_id
        }, room=room_name, include_self=False)
    
    
    @socketio.on('leave_conversation')
    def handle_leave_conversation(data):
        """离开会话房间"""
        if not current_user.is_authenticated:
            return
        
        conversation_id = data.get('conversation_id')
        if not conversation_id:
            return
        
        room_name = f"conversation_{conversation_id}"
        leave_room(room_name)
        
        logger.info(f"用户 {current_user.username} 离开会话 {conversation_id}")
    
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """实时发送消息"""
        if not current_user.is_authenticated:
            emit('error', {'message': '未登录'})
            return
        
        try:
            from app import db
            from app.chat_models import ChatConversation, ChatParticipant, ChatMessage
            
            conversation_id = data.get('conversation_id')
            content = data.get('content', '').strip()
            message_type = data.get('message_type', 'text')
            
            if not conversation_id or not content:
                emit('error', {'message': '参数不完整'})
                return
            
            # 检查权限
            participant = ChatParticipant.query.filter_by(
                conversation_id=conversation_id,
                user_id=current_user.id,
                is_left=False
            ).first()
            
            if not participant:
                emit('error', {'message': '无权在此会话中发送消息'})
                return
            
            # 创建消息
            message = ChatMessage(
                conversation_id=conversation_id,
                sender_id=current_user.id,
                content=content,
                message_type=message_type
            )
            db.session.add(message)
            
            # 更新会话的last_message
            conversation = ChatConversation.query.get(conversation_id)
            if conversation:
                conversation.last_message_id = message.id
                conversation.last_message_time = message.created_date
            
            db.session.commit()
            
            # 构建消息数据
            message_data = message.to_dict()
            
            logger.info(f"消息已保存: ID={message.id}, 会话={conversation_id}")
            
            # 实时广播到会话房间 (使用统一的消息结构: 包含 message 与 conversation_id)
            room_name = f"conversation_{conversation_id}"
            try:
                emit('new_message', {'message': message_data, 'conversation_id': conversation_id}, room=room_name)
            except Exception:
                # 回退到直接广播消息体, 保证兼容旧客户端
                emit('new_message', message_data, room=room_name)
            
            # 发送成功确认
            emit('message_sent', {
                'message_id': message.id,
                'conversation_id': conversation_id,
                'created_date': message.created_date.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            db.session.rollback()
            emit('error', {'message': f'发送失败: {str(e)}'})
    
    
    @socketio.on('typing')
    def handle_typing(data):
        """正在输入状态"""
        if not current_user.is_authenticated:
            return
        
        conversation_id = data.get('conversation_id')
        is_typing = data.get('is_typing', True)
        
        if conversation_id:
            room_name = f"conversation_{conversation_id}"
            emit('user_typing', {
                'user_id': current_user.id,
                'username': current_user.username,
                'is_typing': is_typing
            }, room=room_name, include_self=False)
    
    
    # ==================== 原有通知事件 ====================
    
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """客户端断开连接事件"""
        if not current_user.is_authenticated:
            return
        
        user_id = current_user.id
        username = current_user.username
        
        # 离开房间
        room_name = f"user_{user_id}"
        leave_room(room_name)
        
        # 移除在线用户记录
        if redis_client:
            try:
                redis_client.srem('online_users', user_id)
                redis_client.delete(f'user_session:{user_id}')
            except Exception as e:
                logger.error(f"Redis移除在线用户失败: {e}")
        
        logger.info(f"✗ 用户断开: {username} (ID: {user_id})")
        
        # 广播用户下线(可选)
        emit('user_offline', {
            'user_id': user_id,
            'username': username
        }, broadcast=True)
    
    
    @socketio.on('join_department')
    def handle_join_department(data):
        """加入部门房间"""
        if not current_user.is_authenticated:
            return
        
        department_id = data.get('department_id')
        if department_id:
            room_name = f"department_{department_id}"
            join_room(room_name)
            logger.info(f"用户 {current_user.username} 加入部门房间: {room_name}")
            emit('joined_department', {'department_id': department_id})
    
    
    @socketio.on('leave_department')
    def handle_leave_department(data):
        """离开部门房间"""
        if not current_user.is_authenticated:
            return
        
        department_id = data.get('department_id')
        if department_id:
            room_name = f"department_{department_id}"
            leave_room(room_name)
            logger.info(f"用户 {current_user.username} 离开部门房间: {room_name}")
            emit('left_department', {'department_id': department_id})
    
    
    @socketio.on('ping')
    def handle_ping():
        """心跳检测"""
        emit('pong', {'timestamp': int(time.time())})
    
    
    # ==================== 聊天事件 ====================
    
    @socketio.on('join_conversation')
    def handle_join_conversation(data):
        """加入会话房间"""
        if not current_user.is_authenticated:
            return
        
        conversation_id = data.get('conversation_id')
        if conversation_id:
            room_name = f"conversation_{conversation_id}"
            join_room(room_name)
            logger.info(f"用户 {current_user.username} 加入会话房间: {room_name}")
            emit('joined_conversation', {'conversation_id': conversation_id})
    
    
    @socketio.on('leave_conversation')
    def handle_leave_conversation(data):
        """离开会话房间"""
        if not current_user.is_authenticated:
            return
        
        conversation_id = data.get('conversation_id')
        if conversation_id:
            room_name = f"conversation_{conversation_id}"
            leave_room(room_name)
            logger.info(f"用户 {current_user.username} 离开会话房间: {room_name}")
            emit('left_conversation', {'conversation_id': conversation_id})
    
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """发送聊天消息"""
        if not current_user.is_authenticated:
            return
        
        try:
            from app import db
            from app.chat_models import ChatMessage, ChatConversation, ChatParticipant, ChatAttachment
            
            conversation_id = data.get('conversation_id')
            content = data.get('content')
            message_type = data.get('message_type', 'text')
            reply_to_id = data.get('reply_to_id')
            attachment_id = data.get('attachment_id')  # 附件ID(可选)
            
            if not conversation_id or not content:
                emit('error', {'message': '会话ID和内容不能为空'})
                return
            
            # 检查用户是否是会话参与者
            participant = ChatParticipant.query.filter_by(
                conversation_id=conversation_id,
                user_id=current_user.id,
                is_left=False
            ).first()
            
            if not participant:
                emit('error', {'message': '您不是该会话的参与者'})
                return
            
            # 创建消息
            message = ChatMessage(
                conversation_id=conversation_id,
                sender_id=current_user.id,
                message_type=message_type,
                content=content,
                reply_to_message_id=reply_to_id
            )
            db.session.add(message)
            db.session.flush()  # 获取message.id
            
            # 如果有附件,关联到消息
            if attachment_id:
                attachment = ChatAttachment.query.get(attachment_id)
                if attachment:
                    attachment.message_id = message.id
            
            # 更新会话的最后消息
            conversation = ChatConversation.query.get(conversation_id)
            if conversation:
                conversation.last_message_id = message.id
                conversation.last_message_time = message.created_date
            
            # 更新其他参与者的未读数
            other_participants = ChatParticipant.query.filter(
                ChatParticipant.conversation_id == conversation_id,
                ChatParticipant.user_id != current_user.id,
                ChatParticipant.is_left == False
            ).all()
            
            for p in other_participants:
                p.unread_count += 1
            
            db.session.commit()
            
            # 广播消息到会话房间
            room_name = f"conversation_{conversation_id}"
            emit('new_message', message.to_dict(), room=room_name, include_self=True)
            
            logger.info(f"消息已发送: 用户{current_user.username} -> 会话{conversation_id}")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"发送消息失败: {e}")
            emit('error', {'message': f'发送失败: {str(e)}'})
    
    
    @socketio.on('typing')
    def handle_typing(data):
        """正在输入提示"""
        if not current_user.is_authenticated:
            return
        
        conversation_id = data.get('conversation_id')
        is_typing = data.get('is_typing', True)
        
        if conversation_id:
            room_name = f"conversation_{conversation_id}"
            emit('user_typing', {
                'conversation_id': conversation_id,
                'user_id': current_user.id,
                'username': current_user.username,
                'is_typing': is_typing
            }, room=room_name, include_self=False)
    
    
    @socketio.on('mark_read')
    def handle_mark_read(data):
        """标记消息为已读"""
        if not current_user.is_authenticated:
            return
        
        try:
            from app import db
            from app.chat_models import ChatParticipant
            
            conversation_id = data.get('conversation_id')
            message_id = data.get('message_id')
            
            if not conversation_id:
                return
            
            # 更新参与者的最后阅读消息
            participant = ChatParticipant.query.filter_by(
                conversation_id=conversation_id,
                user_id=current_user.id
            ).first()
            
            if participant:
                if message_id:
                    participant.last_read_message_id = message_id
                participant.unread_count = 0
                db.session.commit()
                
                # 通知发送者消息已读
                emit('messages_read', {
                    'conversation_id': conversation_id,
                    'reader_id': current_user.id,
                    'message_id': message_id
                }, room=f"conversation_{conversation_id}", include_self=False)
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"标记已读失败: {e}")
    
    
    @socketio.on('recall_message')
    def handle_recall_message(data):
        """撤回消息"""
        if not current_user.is_authenticated:
            return
        
        try:
            from app import db
            from app.chat_models import ChatMessage
            from datetime import datetime, timedelta
            
            message_id = data.get('message_id')
            
            if not message_id:
                emit('error', {'message': '消息ID不能为空'})
                return
            
            # 获取消息
            message = ChatMessage.query.get(message_id)
            
            if not message:
                emit('error', {'message': '消息不存在'})
                return
            
            # 只能撤回自己的消息
            if message.sender_id != current_user.id:
                emit('error', {'message': '只能撤回自己的消息'})
                return
            
            # 检查是否超过撤回时限(2分钟)
            time_limit = datetime.now() - timedelta(minutes=2)
            if message.created_date < time_limit:
                emit('error', {'message': '消息发送超过2分钟,无法撤回'})
                return
            
            # 撤回消息
            message.is_recalled = True
            message.recalled_date = datetime.now()
            db.session.commit()
            
            # 广播撤回事件
            room_name = f"conversation_{message.conversation_id}"
            emit('message_recalled', {
                'message_id': message_id,
                'conversation_id': message.conversation_id
            }, room=room_name, include_self=True)
            
            logger.info(f"消息已撤回: ID={message_id}, 用户={current_user.username}")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"撤回消息失败: {e}")
            emit('error', {'message': f'撤回失败: {str(e)}'})


# ==================== 通知功能 ====================

def send_notification_to_user(user_id, notification_data):
    """
    发送通知给指定用户
    
    Args:
        user_id: 用户ID
        notification_data: 通知数据字典
            {
                'title': '通知标题',
                'message': '通知内容',
                'type': 'info|success|warning|error',
                'link': '点击跳转的URL(可选)',
                'data': 额外数据(可选)
            }
    """
    if not socketio:
        logger.warning("SocketIO未初始化,无法发送通知")
        return False
    
    try:
        room_name = f"user_{user_id}"
        
        # 添加时间戳
        import time
        notification_data['timestamp'] = int(time.time())
        
        # 发送通知
        socketio.emit('notification', notification_data, room=room_name)
        
        logger.info(f"✓ 通知已发送给用户 {user_id}: {notification_data.get('title')}")
        return True
        
    except Exception as e:
        logger.error(f"发送通知失败: {e}")
        return False


def send_notification_to_department(department_id, notification_data):
    """
    发送通知给整个部门
    
    Args:
        department_id: 部门ID
        notification_data: 通知数据字典
    """
    if not socketio:
        logger.warning("SocketIO未初始化,无法发送通知")
        return False
    
    try:
        room_name = f"department_{department_id}"
        
        # 添加时间戳
        import time
        notification_data['timestamp'] = int(time.time())
        
        # 发送通知
        socketio.emit('notification', notification_data, room=room_name)
        
        logger.info(f"✓ 通知已发送给部门 {department_id}: {notification_data.get('title')}")
        return True
        
    except Exception as e:
        logger.error(f"发送部门通知失败: {e}")
        return False


def broadcast_notification(notification_data, exclude_user_id=None):
    """
    广播通知给所有在线用户
    
    Args:
        notification_data: 通知数据字典
        exclude_user_id: 排除的用户ID(可选)
    """
    if not socketio:
        logger.warning("SocketIO未初始化,无法发送通知")
        return False
    
    try:
        # 添加时间戳
        import time
        notification_data['timestamp'] = int(time.time())
        
        # 广播通知
        socketio.emit('notification', notification_data, broadcast=True)
        
        logger.info(f"✓ 广播通知: {notification_data.get('title')}")
        return True
        
    except Exception as e:
        logger.error(f"广播通知失败: {e}")
        return False


def get_online_users():
    """获取在线用户列表"""
    if not redis_client:
        return []
    
    try:
        user_ids = redis_client.smembers('online_users')
        return [int(uid) for uid in user_ids]
    except Exception as e:
        logger.error(f"获取在线用户失败: {e}")
        return []


def is_user_online(user_id):
    """检查用户是否在线"""
    if not redis_client:
        return False
    
    try:
        return redis_client.sismember('online_users', user_id)
    except Exception as e:
        logger.error(f"检查用户在线状态失败: {e}")
        return False


# 导入time模块
import time
