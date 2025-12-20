#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
聊天系统API路由
提供会话管理、消息发送、用户列表等接口
"""
from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required, current_user
from app import db
from app.chat_models import ChatConversation, ChatMessage, ChatParticipant, ChatAttachment
from app.models import User
from datetime import datetime
import os
from werkzeug.utils import secure_filename

bp = Blueprint('chat_api', __name__, url_prefix='/api/chat')

UPLOAD_FOLDER = 'app/static/uploads/chat'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/users', methods=['GET'])
@login_required
def get_users():
    """获取可以聊天的用户列表(排除自己)"""
    users = User.query.filter(User.id != current_user.id).all()
    return jsonify({
        'users': [{
            'id': u.id,
            'username': u.username,
            'real_name': u.real_name,
            'department': u.department,
            'avatar': None  # 可以后续添加头像功能
        } for u in users]
    })


@bp.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    """获取当前用户的所有会话"""
    # 查询用户参与的所有会话
    participant_records = ChatParticipant.query.filter_by(user_id=current_user.id).all()
    conversation_ids = [p.conversation_id for p in participant_records]
    if not conversation_ids:
        return jsonify({'conversations': []})
    conversations = ChatConversation.query.filter(ChatConversation.id.in_(conversation_ids)).order_by(ChatConversation.last_message_time.desc()).all()
    
    result = []
    for conv in conversations:
        # 获取最后一条消息
        last_msg = ChatMessage.query.filter_by(
            conversation_id=conv.id
        ).order_by(ChatMessage.created_date.desc()).first()
        
        # 获取未读消息数
        participant = ChatParticipant.query.filter_by(
            conversation_id=conv.id,
            user_id=current_user.id
        ).first()
        
        unread_count = 0
        if participant and participant.last_read_message_id:
            unread_count = ChatMessage.query.filter(
                ChatMessage.conversation_id == conv.id,
                ChatMessage.id > participant.last_read_message_id,
                ChatMessage.sender_id != current_user.id
            ).count()
        elif participant:
            unread_count = ChatMessage.query.filter(
                ChatMessage.conversation_id == conv.id,
                ChatMessage.sender_id != current_user.id
            ).count()
        
        # 对于私聊,获取对方用户信息
        other_user = None
        if conv.conversation_type == 'direct':
            other_participant = ChatParticipant.query.filter(
                ChatParticipant.conversation_id == conv.id,
                ChatParticipant.user_id != current_user.id
            ).first()
            if other_participant:
                other_user = {
                    'id': other_participant.user.id,
                    'username': other_participant.user.username,
                    'real_name': other_participant.user.real_name
                }
        
        # 获取所有参与者数量
        participant_count = ChatParticipant.query.filter_by(
            conversation_id=conv.id
        ).count()
        
        result.append({
            'id': conv.id,
            'type': conv.conversation_type,
            'name': conv.name,
            'created_date': conv.created_date.strftime('%Y-%m-%d %H:%M:%S') if conv.created_date else None,
            'last_message': last_msg.content if last_msg else None,
            'last_message_time': conv.last_message_time.strftime('%Y-%m-%d %H:%M:%S') if conv.last_message_time else None,
            'unread_count': unread_count,
            'other_user': other_user,
            'participant_count': participant_count
        })
    
    return jsonify({'conversations': result})


@bp.route('/conversations', methods=['POST'])
@login_required
def create_conversation():
    """创建新会话"""
    data = request.get_json()
    conv_type = data.get('type', 'direct')  # direct 或 group
    participant_ids = data.get('participant_ids', [])
    name = data.get('name')
    
    # 验证参数
    if not participant_ids:
        return jsonify({'error': '请选择聊天对象'}), 400
    
    # 如果是私聊,检查是否已存在会话
    if conv_type == 'direct':
        if len(participant_ids) != 1:
            return jsonify({'error': '私聊只能选择一个用户'}), 400
        
        other_user_id = participant_ids[0]
        
        # 查找是否已存在与该用户的私聊
        existing_conv = db.session.query(ChatConversation).join(
            ChatParticipant, ChatConversation.id == ChatParticipant.conversation_id
        ).filter(
            ChatConversation.conversation_type == 'direct',
            ChatParticipant.user_id.in_([current_user.id, other_user_id])
        ).group_by(ChatConversation.id).having(
            db.func.count(ChatParticipant.user_id) == 2
        ).first()
        
        if existing_conv:
            # 返回已存在的会话
            return jsonify({
                'conversation': {
                    'id': existing_conv.id,
                    'type': existing_conv.conversation_type,
                    'name': existing_conv.name
                },
                'existed': True
            })
    
    # 创建新会话
    conversation = ChatConversation(
        conversation_type=conv_type,
        name=name,
        creator_id=current_user.id
    )
    db.session.add(conversation)
    db.session.flush()  # 获取conversation.id
    
    # 添加参与者(包括创建者自己)
    all_participant_ids = list(set([current_user.id] + participant_ids))
    for user_id in all_participant_ids:
        participant = ChatParticipant(
            conversation_id=conversation.id,
            user_id=user_id
        )
        db.session.add(participant)
    
    db.session.commit()
    
    return jsonify({
        'conversation': {
            'id': conversation.id,
            'type': conversation.conversation_type,
            'name': conversation.name
        },
        'existed': False
    }), 201


@bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
@login_required
def get_messages(conversation_id):
    """获取会话的消息列表"""
    # 验证用户是否是该会话的参与者
    participant = ChatParticipant.query.filter_by(
        conversation_id=conversation_id,
        user_id=current_user.id
    ).first()
    
    if not participant:
        return jsonify({'error': '无权访问该会话'}), 403
    
    # 获取消息
    messages = ChatMessage.query.filter_by(
        conversation_id=conversation_id,
        is_deleted=False
    ).order_by(ChatMessage.created_date.asc()).all()
    
    result = []
    for msg in messages:
        result.append({
            'id': msg.id,
            'conversation_id': msg.conversation_id,
            'sender_id': msg.sender_id,
            'sender_name': msg.sender.username if msg.sender else 'Unknown',
            'sender_real_name': msg.sender.real_name if msg.sender else None,
            'message_type': msg.message_type,
            'content': msg.content if not msg.is_recalled else '[消息已撤回]',
            'is_recalled': msg.is_recalled,
            'created_date': msg.created_date.strftime('%Y-%m-%d %H:%M:%S') if msg.created_date else None,
            'attachments': [
                {
                    'id': att.id,
                    'filename': att.filename,
                    'file_size': att.file_size,
                    'file_type': att.file_type
                } for att in msg.attachments
            ] if msg.attachments else []
        })
    
    # 更新已读状态
    if messages:
        last_message = messages[-1]
        participant.last_read_message_id = last_message.id
        participant.last_read_time = datetime.now()
        db.session.commit()
    
    return jsonify({'messages': result})


@bp.route('/conversations/<int:conversation_id>/messages', methods=['POST'])
@login_required
def send_message(conversation_id):
    """发送消息(HTTP API,用于非WebSocket场景)"""
    # 验证用户是否是该会话的参与者
    participant = ChatParticipant.query.filter_by(
        conversation_id=conversation_id,
        user_id=current_user.id
    ).first()
    
    if not participant:
        return jsonify({'error': '无权访问该会话'}), 403
    
    data = request.get_json()
    content = data.get('content', '').strip()
    message_type = data.get('message_type', 'text')
    
    if not content and message_type == 'text':
        return jsonify({'error': '消息内容不能为空'}), 400
    
    # 创建消息
    message = ChatMessage(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=content,
        message_type=message_type
    )
    db.session.add(message)
    
    # 更新会话的最后消息时间
    conversation = ChatConversation.query.get(conversation_id)
    conversation.last_message_time = datetime.now()
    conversation.last_message_id = message.id
    
    db.session.commit()
    
    return jsonify({
        'message': {
            'id': message.id,
            'conversation_id': message.conversation_id,
            'sender_id': message.sender_id,
            'sender_name': current_user.username,
            'content': message.content,
            'created_date': message.created_date.strftime('%Y-%m-%d %H:%M:%S')
        }
    }), 201


@bp.route('/messages/<int:message_id>/recall', methods=['POST'])
@login_required
def recall_message(message_id):
    """撤回消息"""
    message = ChatMessage.query.get_or_404(message_id)
    
    # 只能撤回自己的消息
    if message.sender_id != current_user.id:
        return jsonify({'error': '只能撤回自己的消息'}), 403
    
    # 检查是否超过2分钟
    if (datetime.now() - message.created_date).total_seconds() > 120:
        return jsonify({'error': '超过2分钟无法撤回'}), 400
    
    message.is_recalled = True
    message.recalled_date = datetime.now()
    db.session.commit()
    
    return jsonify({'success': True})


@bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """上传文件/图片"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件类型'}), 400
    
    # 确保上传目录存在
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # 生成安全的文件名
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    stored_filename = f"{timestamp}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, stored_filename)
    
    # 保存文件
    file.save(file_path)
    
    return jsonify({
        'filename': filename,
        'stored_filename': stored_filename,
        'file_path': file_path,
        'file_size': os.path.getsize(file_path),
        'url': f'/static/uploads/chat/{stored_filename}'
    })


@bp.route('/attachments/<int:attachment_id>/download', methods=['GET'])
@login_required
def download_attachment(attachment_id):
    """下载附件"""
    attachment = ChatAttachment.query.get_or_404(attachment_id)
    
    # 验证权限
    message = attachment.message
    participant = ChatParticipant.query.filter_by(
        conversation_id=message.conversation_id,
        user_id=current_user.id
    ).first()
    
    if not participant:
        return jsonify({'error': '无权访问'}), 403
    
    return send_file(
        attachment.file_path,
        as_attachment=True,
        download_name=attachment.filename
    )
