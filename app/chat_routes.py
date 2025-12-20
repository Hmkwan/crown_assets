"""
聊天系统路由
包括会话管理、消息发送、附件上传等API
"""
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from app import db
from app.chat_models import (
    ChatConversation, ChatParticipant, ChatMessage, 
    ChatAttachment, ChatPermission
)
from app.socketio_handler import socketio
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from PIL import Image
import os
import uuid
import mimetypes

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')


# ==================== 用户列表 ====================

@chat_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    """获取可聊天的用户列表"""
    try:
        from app.models import User
        
        # 获取所有激活的用户(排除当前用户)
        users = User.query.filter(
            User.id != current_user.id,
            User.is_active == True
        ).all()
        
        user_list = []
        for user in users:
            # 处理department - 可能是对象或字符串
            if hasattr(user, 'department') and user.department:
                dept_name = user.department.name if hasattr(user.department, 'name') else str(user.department)
            else:
                dept_name = '未分配'
            
            user_list.append({
                'id': user.id,
                'username': user.username,
                'real_name': getattr(user, 'real_name', user.username),
                'department': dept_name,
                'role': user.role
            })
        
        return jsonify({'users': user_list})
    except Exception as e:
        current_app.logger.error(f'获取用户列表失败: {str(e)}')
        return jsonify({'error': '获取用户列表失败'}), 500


# ==================== 会话管理 ====================

@chat_bp.route('/conversations', methods=['POST'])
@login_required
def create_conversation():
    """创建新会话"""
    try:
        data = request.get_json()
        conversation_type = data.get('type', 'direct')  # direct 或 group
        participant_ids = data.get('participant_ids', [])  # 参与者ID列表
        name = data.get('name')
        description = data.get('description')
        
        if not participant_ids:
            return jsonify({'error': '参与者不能为空'}), 400
        
        # 对于一对一会话,检查是否已存在
        if conversation_type == 'direct':
            if len(participant_ids) != 1:
                return jsonify({'error': '一对一会话只能有两个参与者'}), 400
            
            other_user_id = participant_ids[0]
            
            # 查找现有会话
            existing = db.session.query(ChatConversation).join(
                ChatParticipant, ChatConversation.id == ChatParticipant.conversation_id
            ).filter(
                ChatConversation.conversation_type == 'direct',
                ChatParticipant.user_id.in_([current_user.id, other_user_id])
            ).group_by(ChatConversation.id).having(
                db.func.count(ChatParticipant.id) == 2
            ).first()
            
            if existing:
                return jsonify({'conversation': existing.to_dict(current_user.id)}), 200
        
        # 创建新会话
        conversation = ChatConversation(
            conversation_type=conversation_type,
            name=name,
            description=description,
            creator_id=current_user.id
        )
        db.session.add(conversation)
        db.session.flush()
        
        # 添加创建者为参与者
        creator_participant = ChatParticipant(
            conversation_id=conversation.id,
            user_id=current_user.id,
            role='owner' if conversation_type == 'group' else 'member'
        )
        db.session.add(creator_participant)
        
        # 添加其他参与者
        for user_id in participant_ids:
            if user_id != current_user.id:
                participant = ChatParticipant(
                    conversation_id=conversation.id,
                    user_id=user_id,
                    role='member'
                )
                db.session.add(participant)
        
        db.session.commit()
        
        # 通知所有参与者
        from app.socketio_handler import send_notification_to_user
        for user_id in participant_ids:
            if user_id != current_user.id:
                send_notification_to_user(user_id, {
                    'type': 'new_conversation',
                    'conversation': conversation.to_dict(user_id)
                })
        
        return jsonify({'conversation': conversation.to_dict(current_user.id)}), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建会话失败: {e}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    """获取当前用户的所有会话"""
    try:
        # 查询用户参与的所有会话
        participants = ChatParticipant.query.filter_by(
            user_id=current_user.id,
            is_left=False
        ).all()
        
        conversations = []
        for p in participants:
            conv_dict = p.conversation.to_dict(current_user.id)
            conv_dict['is_pinned'] = p.is_pinned
            conv_dict['is_muted'] = p.is_muted
            
            # 获取最后一条消息
            if p.conversation.last_message:
                conv_dict['last_message'] = {
                    'content': p.conversation.last_message.content if not p.conversation.last_message.is_recalled else '[消息已撤回]',
                    'sender_name': p.conversation.last_message.sender.username if p.conversation.last_message.sender else 'Unknown',
                    'created_date': p.conversation.last_message.created_date.strftime('%Y-%m-%d %H:%M:%S')
                }
            
            conversations.append(conv_dict)
        
        # 按置顶和最后消息时间排序
        conversations.sort(key=lambda x: (
            not x.get('is_pinned', False),
            x.get('last_message_time') or ''
        ), reverse=True)
        
        return jsonify({'conversations': conversations}), 200
        
    except Exception as e:
        current_app.logger.error(f"获取会话列表失败: {e}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/conversations/<int:conversation_id>', methods=['GET'])
@login_required
def get_conversation(conversation_id):
    """获取会话详情"""
    try:
        # 检查用户是否是参与者
        participant = ChatParticipant.query.filter_by(
            conversation_id=conversation_id,
            user_id=current_user.id,
            is_left=False
        ).first()
        
        if not participant:
            return jsonify({'error': '无权访问此会话'}), 403
        
        conversation = participant.conversation
        conv_dict = conversation.to_dict(current_user.id)
        
        # 获取参与者信息
        conv_dict['participants'] = [
            {
                'id': p.user.id,
                'username': p.user.username,
                'real_name': getattr(p.user, 'real_name', p.user.username),
                'role': p.role,
                'joined_date': p.joined_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            for p in conversation.participants if not p.is_left
        ]
        
        return jsonify({'conversation': conv_dict}), 200
        
    except Exception as e:
        current_app.logger.error(f"获取会话详情失败: {e}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/conversations/<int:conversation_id>', methods=['PATCH'])
@login_required
def update_conversation(conversation_id):
    """更新会话信息（群名/描述），仅群主或群管理员可操作"""
    try:
        participant = ChatParticipant.query.filter_by(
            conversation_id=conversation_id,
            user_id=current_user.id,
            is_left=False
        ).first_or_404()
        conversation = participant.conversation

        # 仅允许群聊被重命名
        if conversation.conversation_type != 'group':
            return jsonify({'error': '仅支持群聊修改'}), 400

        # 权限检查
        if participant.role not in ('owner', 'admin'):
            return jsonify({'error': '需要群主或管理员权限'}), 403

        data = request.get_json() or {}
        name = data.get('name')
        description = data.get('description')

        updated = False
        if name is not None and name.strip() != '':
            conversation.name = name.strip()
            updated = True
        if description is not None:
            conversation.description = description
            updated = True

        if updated:
            db.session.commit()

            # 通知其他成员
            from app.socketio_handler import send_notification_to_user
            for p in conversation.participants:
                if p.user_id != current_user.id:
                    send_notification_to_user(p.user_id, {
                        'type': 'conversation_updated',
                        'conversation': conversation.to_dict(p.user_id)
                    })

        return jsonify({'conversation': conversation.to_dict(current_user.id)}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新会话失败: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== 消息管理 ====================

@chat_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
@login_required
def get_messages(conversation_id):
    """获取会话消息历史"""
    try:
        # 检查用户是否是参与者
        participant = ChatParticipant.query.filter_by(
            conversation_id=conversation_id,
            user_id=current_user.id,
            is_left=False
        ).first()
        
        if not participant:
            return jsonify({'error': '无权访问此会话'}), 403
        
        # 分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        before_id = request.args.get('before_id', type=int)  # 获取某条消息之前的消息
        
        # 构建查询
        query = ChatMessage.query.filter_by(
            conversation_id=conversation_id,
            is_deleted=False
        )
        
        if before_id:
            query = query.filter(ChatMessage.id < before_id)
        
        # 按时间倒序
        query = query.order_by(ChatMessage.created_date.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        messages = [msg.to_dict() for msg in pagination.items]
        
        # 反转消息顺序(前端显示时从旧到新)
        messages.reverse()
        
        return jsonify({
            'messages': messages,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'has_more': pagination.has_next
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取消息历史失败: {e}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/messages', methods=['POST'])
@login_required
def send_message():
    """发送消息(HTTP轮询方式)，支持附件关联"""
    try:
        data = request.get_json()
        conversation_id = data.get('conversation_id')
        content = data.get('content')
        message_type = data.get('message_type', 'text')
        attachment_ids = data.get('attachment_ids', []) or []
        
        if not conversation_id:
            return jsonify({'error': '缺少会话ID'}), 400
        
        # 验证用户是会话参与者
        participant = ChatParticipant.query.filter_by(
            conversation_id=conversation_id,
            user_id=current_user.id
        ).first()
        
        if not participant:
            return jsonify({'error': '您不是该会话的参与者'}), 403
        
        # 如果内容为空但有附件, 将 message_type 设为 file
        if (not content or content.strip() == '') and attachment_ids:
            message_type = 'file'
        
        # 创建消息
        message = ChatMessage(
            conversation_id=conversation_id,
            sender_id=current_user.id,
            content=content,
            message_type=message_type
        )
        db.session.add(message)
        db.session.flush()
        
        # 将已上传的附件关联到消息
        if attachment_ids:
            attachments = ChatAttachment.query.filter(ChatAttachment.id.in_(attachment_ids)).all()
            for att in attachments:
                att.message_id = message.id
            db.session.add_all(attachments)
        
        # 更新会话的最后消息时间与引用
        conversation = ChatConversation.query.get(conversation_id)
        if conversation:
            conversation.updated_date = datetime.utcnow()
            conversation.last_message_id = message.id
            conversation.last_message_time = message.created_date
        
        db.session.commit()
        
        # 准备响应数据, 包含附件信息
        return jsonify({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'message_type': message.message_type,
                'created_date': message.created_date.isoformat(),
                'attachments': [att.to_dict() for att in getattr(message, 'attachments', [])]
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"发送消息失败: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== 附件管理 ====================

@chat_bp.route('/attachments', methods=['POST'])
@login_required
def upload_attachment():
    """上传聊天附件"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        conversation_id = request.form.get('conversation_id')
        if not conversation_id:
            return jsonify({'error': '会话ID不能为空'}), 400
        
        # 检查用户是否是参与者
        participant = ChatParticipant.query.filter_by(
            conversation_id=conversation_id,
            user_id=current_user.id,
            is_left=False
        ).first()
        
        if not participant:
            return jsonify({'error': '无权上传文件到此会话'}), 403
        
        # 检查权限
        permission = ChatPermission.query.filter_by(user_id=current_user.id).first()
        if permission and not permission.can_send_file:
            return jsonify({'error': '您没有发送文件的权限'}), 403
        
        # 保存文件
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        stored_filename = f"{uuid.uuid4().hex}{file_ext}"
        
        # 创建上传目录
        upload_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'chat')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, stored_filename)
        file.save(file_path)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 获取MIME类型
        file_type, _ = mimetypes.guess_type(filename)
        
        # 创建附件记录(暂不关联消息)，记录上传用户
        attachment = ChatAttachment(
            message_id=0,  # 临时值,发送消息时更新
            filename=filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            upload_user_id=current_user.id
        )
        
        # 生成缩略图(如果是图片)
        if file_type and file_type.startswith('image/'):
            try:
                thumbnail_filename = f"thumb_{stored_filename}"
                thumbnail_path = os.path.join(upload_folder, thumbnail_filename)
                
                with Image.open(file_path) as img:
                    # 限制缩略图大小
                    img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                    img.save(thumbnail_path, quality=85, optimize=True)
                    attachment.thumbnail_path = thumbnail_path
            except Exception as e:
                current_app.logger.warning(f"生成缩略图失败: {e}")
        
        db.session.add(attachment)
        db.session.commit()
        
        return jsonify({
            'attachment': attachment.to_dict(),
            'attachment_id': attachment.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"上传附件失败: {e}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/attachments/<int:attachment_id>/download', methods=['GET'])
@login_required
def download_attachment(attachment_id):
    """下载聊天附件"""
    try:
        attachment = ChatAttachment.query.get_or_404(attachment_id)
        
        # 检查权限(确保用户是会话参与者)
        message = attachment.message
        if message:
            participant = ChatParticipant.query.filter_by(
                conversation_id=message.conversation_id,
                user_id=current_user.id,
                is_left=False
            ).first()
            
            if not participant:
                return jsonify({'error': '无权下载此文件'}), 403
        
        return send_file(
            attachment.file_path,
            as_attachment=True,
            download_name=attachment.filename
        )
        
    except Exception as e:
        current_app.logger.error(f"下载附件失败: {e}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/attachments/<int:attachment_id>/thumbnail', methods=['GET'])
@login_required
def get_thumbnail(attachment_id):
    """获取附件缩略图"""
    try:
        attachment = ChatAttachment.query.get_or_404(attachment_id)
        
        if not attachment.thumbnail_path:
            return jsonify({'error': '该文件没有缩略图'}), 404
        
        # 检查权限
        message = attachment.message
        if message:
            participant = ChatParticipant.query.filter_by(
                conversation_id=message.conversation_id,
                user_id=current_user.id,
                is_left=False
            ).first()
            
            if not participant:
                return jsonify({'error': '无权访问此文件'}), 403
        
        return send_file(
            attachment.thumbnail_path,
            mimetype=attachment.file_type
        )
        
    except Exception as e:
        current_app.logger.error(f"获取缩略图失败: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== 会话操作 ====================

@chat_bp.route('/conversations/<int:conversation_id>/pin', methods=['POST'])
@login_required
def pin_conversation(conversation_id):
    """置顶/取消置顶会话"""
    try:
        participant = ChatParticipant.query.filter_by(
            conversation_id=conversation_id,
            user_id=current_user.id
        ).first_or_404()
        
        is_pinned = request.get_json().get('is_pinned', True)
        participant.is_pinned = is_pinned
        db.session.commit()
        
        return jsonify({'success': True, 'is_pinned': is_pinned}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"置顶会话失败: {e}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/conversations/<int:conversation_id>/mute', methods=['POST'])
@login_required
def mute_conversation(conversation_id):
    """静音/取消静音会话"""
    try:
        participant = ChatParticipant.query.filter_by(
            conversation_id=conversation_id,
            user_id=current_user.id
        ).first_or_404()
        
        is_muted = request.get_json().get('is_muted', True)
        participant.is_muted = is_muted
        db.session.commit()
        
        return jsonify({'success': True, 'is_muted': is_muted}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"静音会话失败: {e}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/conversations/<int:conversation_id>/leave', methods=['POST'])
@login_required
def leave_conversation(conversation_id):
    """退出会话"""
    try:
        participant = ChatParticipant.query.filter_by(
            conversation_id=conversation_id,
            user_id=current_user.id
        ).first_or_404()
        
        participant.is_left = True
        participant.left_date = datetime.now()
        db.session.commit()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"退出会话失败: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== 管理员功能 ====================

def admin_required(f):
    """管理员权限装饰器"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function


@chat_bp.route('/admin/statistics', methods=['GET'])
@login_required
@admin_required
def get_chat_statistics():
    """获取聊天系统统计数据"""
    try:
        from sqlalchemy import func
        from app.models import User
        
        # 总会话数
        total_conversations = ChatConversation.query.count()
        
        # 活跃会话数(有消息的)
        active_conversations = db.session.query(ChatConversation.id).join(
            ChatMessage, ChatConversation.id == ChatMessage.conversation_id
        ).distinct().count()
        
        # 总消息数
        total_messages = ChatMessage.query.count()
        
        # 今天消息数
        today = datetime.now().date()
        today_messages = ChatMessage.query.filter(
            func.date(ChatMessage.created_date) == today
        ).count()
        
        # 活跃用户数(发过消息的)
        active_users = db.session.query(ChatMessage.sender_id).distinct().count()
        
        # 附件总数
        total_attachments = ChatAttachment.query.count()
        
        # 按类型统计会话
        conversation_types = db.session.query(
            ChatConversation.conversation_type,
            func.count(ChatConversation.id)
        ).group_by(ChatConversation.conversation_type).all()
        
        # 消息趋势(最近7天)
        message_trend = []
        for i in range(7):
            date = datetime.now().date() - timedelta(days=i)
            count = ChatMessage.query.filter(
                func.date(ChatMessage.created_date) == date
            ).count()
            message_trend.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        message_trend.reverse()
        
        return jsonify({
            'total_conversations': total_conversations,
            'active_conversations': active_conversations,
            'total_messages': total_messages,
            'today_messages': today_messages,
            'active_users': active_users,
            'total_attachments': total_attachments,
            'conversation_types': {ct: count for ct, count in conversation_types},
            'message_trend': message_trend
        })
        
    except Exception as e:
        current_app.logger.error(f'获取统计数据失败: {str(e)}')
        return jsonify({'error': '获取统计数据失败'}), 500


@chat_bp.route('/admin/conversations', methods=['GET'])
@login_required
@admin_required
def get_all_conversations():
    """管理员获取所有会话列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        conversation_type = request.args.get('type')  # direct/group
        
        query = ChatConversation.query
        
        if conversation_type:
            query = query.filter_by(conversation_type=conversation_type)
        
        query = query.order_by(ChatConversation.last_message_time.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        conversations = pagination.items
        
        result = []
        for conv in conversations:
            # 获取参与者数量
            participant_count = ChatParticipant.query.filter_by(
                conversation_id=conv.id,
                is_left=False
            ).count()
            
            # 获取消息数量
            message_count = ChatMessage.query.filter_by(
                conversation_id=conv.id,
                is_deleted=False
            ).count()
            
            conv_data = conv.to_dict()
            conv_data['participant_count'] = participant_count
            conv_data['message_count'] = message_count
            result.append(conv_data)
        
        return jsonify({
            'conversations': result,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
        
    except Exception as e:
        current_app.logger.error(f'获取会话列表失败: {str(e)}')
        return jsonify({'error': '获取会话列表失败'}), 500


@chat_bp.route('/admin/conversations/<int:conversation_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_conversation_admin(conversation_id):
    """管理员删除会话"""
    try:
        conversation = ChatConversation.query.get_or_404(conversation_id)
        
        # 删除所有消息
        ChatMessage.query.filter_by(conversation_id=conversation_id).delete()
        
        # 删除所有参与者
        ChatParticipant.query.filter_by(conversation_id=conversation_id).delete()
        
        # 删除会话
        db.session.delete(conversation)
        db.session.commit()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'删除会话失败: {str(e)}')
        return jsonify({'error': '删除会话失败'}), 500


@chat_bp.route('/admin/messages', methods=['GET'])
@login_required
@admin_required
def get_all_messages():
    """管理员获取所有消息(用于审计)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        conversation_id = request.args.get('conversation_id', type=int)
        sender_id = request.args.get('sender_id', type=int)
        keyword = request.args.get('keyword')
        
        query = ChatMessage.query.filter_by(is_deleted=False)
        
        if conversation_id:
            query = query.filter_by(conversation_id=conversation_id)
        
        if sender_id:
            query = query.filter_by(sender_id=sender_id)
        
        if keyword:
            query = query.filter(ChatMessage.content.ilike(f'%{keyword}%'))
        
        query = query.order_by(ChatMessage.created_date.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        messages = pagination.items
        
        result = []
        for msg in messages:
            msg_data = msg.to_dict()
            # 添加发送者信息
            from app.models import User
            sender = User.query.get(msg.sender_id)
            if sender:
                msg_data['sender_name'] = getattr(sender, 'real_name', sender.username)
            result.append(msg_data)
        
        return jsonify({
            'messages': result,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
        
    except Exception as e:
        current_app.logger.error(f'获取消息列表失败: {str(e)}')
        return jsonify({'error': '获取消息列表失败'}), 500


@chat_bp.route('/admin/messages/<int:message_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_message_admin(message_id):
    """管理员删除消息"""
    try:
        message = ChatMessage.query.get_or_404(message_id)
        message.is_deleted = True
        message.deleted_at = datetime.now()
        db.session.commit()
        
        # 通知相关用户
        socketio.emit('message_deleted', {
            'message_id': message_id,
            'conversation_id': message.conversation_id
        }, room=f'conversation_{message.conversation_id}')
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'删除消息失败: {str(e)}')
        return jsonify({'error': '删除消息失败'}), 500


@chat_bp.route('/admin/users/chat-active', methods=['GET'])
@login_required
@admin_required
def get_chat_active_users():
    """获取聊天活跃用户列表"""
    try:
        from sqlalchemy import func, distinct
        from app.models import User
        
        # 获取发过消息的用户
        active_users = db.session.query(
            User,
            func.count(ChatMessage.id).label('message_count'),
            func.max(ChatMessage.created_date).label('last_message_time')
        ).join(
            ChatMessage, User.id == ChatMessage.sender_id
        ).group_by(User.id).order_by(
            func.count(ChatMessage.id).desc()
        ).limit(100).all()
        
        result = []
        for user, msg_count, last_time in active_users:
            # 处理department - 可能是对象或字符串
            if hasattr(user, 'department') and user.department:
                dept_name = user.department.name if hasattr(user.department, 'name') else str(user.department)
            else:
                dept_name = '未分配'
            
            result.append({
                'id': user.id,
                'username': user.username,
                'real_name': getattr(user, 'real_name', user.username),
                'department': dept_name,
                'message_count': msg_count,
                'last_message_time': last_time.isoformat() if last_time else None
            })
        
        return jsonify({'users': result})
        
    except Exception as e:
        current_app.logger.error(f'获取活跃用户失败: {str(e)}')
        return jsonify({'error': '获取活跃用户失败'}), 500


# ==================== 测试页面 ====================

@chat_bp.route('/test', methods=['GET'])
@login_required
def test_page():
    """测试页面"""
    from flask import render_template
    return render_template('test_chat_api.html')
