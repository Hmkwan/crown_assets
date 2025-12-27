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

# 新增: API 获取会话详情，自动恢复 is_left 用户
@bp.route('/conversations/<int:conversation_id>', methods=['GET'])
@login_required
def get_conversation(conversation_id):
    """API: 获取会话详情，自动恢复 is_left 用户"""
    try:
        # 查找参与者记录
        participant = ChatParticipant.query.filter_by(
            conversation_id=conversation_id,
            user_id=current_user.id
        ).first()
        if not participant:
            # 若未找到参与者，尝试容错性地恢复/加入：
            # 1) 对于 direct 一对一会话，若会话存在且当前仅包含另一方（或参与记录缺失但有单一参与者），尝试自动加入（修复同步或历史数据缺失）
            # 2) 若当前用户是会话创建者，恢复其参与记录
            # 3) 若当前用户曾在此会话发过消息（说明曾是参与者），恢复其参与记录
            conversation_tmp = ChatConversation.query.get(conversation_id)
            if conversation_tmp:
                try_join = False
                # 若是 direct 且目前不包含当前用户但有至少一个其他参与者
                if conversation_tmp.conversation_type == 'direct':
                    has_current = any(p.user_id == current_user.id for p in conversation_tmp.participants)
                    other_count = sum(1 for p in conversation_tmp.participants if p.user_id != current_user.id)
                    if not has_current and other_count >= 1:
                        try_join = True
                # 如果当前用户是创建者，也尝试恢复
                if conversation_tmp.creator_id == current_user.id:
                    try_join = True
                # 如果当前用户曾发送过消息到此会话，也可以恢复
                if ChatMessage.query.filter_by(conversation_id=conversation_id, sender_id=current_user.id).first():
                    try_join = True

                if try_join:
                    new_participant = ChatParticipant(conversation_id=conversation_id, user_id=current_user.id)
                    db.session.add(new_participant)
                    db.session.commit()
                    participant = new_participant

            # 如果仍未找到则返回 403
            if not participant:
                # 返回详细调试信息
                return jsonify({
                    'error': '无权访问此会话',
                    'user_id': current_user.id,
                    'conversation_id': conversation_id,
                    'participant': None
                }), 403
        # 无论 is_left 状态，均自动恢复为参与者
        if participant.is_left:
            participant.is_left = False
            participant.left_date = None
            db.session.flush()
            db.session.refresh(participant)
            db.session.commit()
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
        return jsonify({'error': str(e)}), 500


@bp.route('/users', methods=['GET'])
@login_required
def get_users():
    """获取可以聊天的用户列表(排除自己)"""
    users = User.query.filter(User.id != current_user.id).all()
    return jsonify({
        'users': [ {
            'id': u.id,
            'username': u.username,
            'real_name': getattr(u, 'real_name', u.username),
            'department': u.department,
            'avatar': None  # 可以后续添加头像功能
        } for u in users ]
    })


# 新增: 提供给聊天前端的工作流模板列表（仅 chat 类型、对已登录用户可用）
from app.approval_models import WorkflowTemplate

@bp.route('/workflow_templates', methods=['GET'])
@login_required
def get_chat_workflow_templates():
    """获取适用于聊天的工作流模板（order_type == 'chat'）"""
    try:
        templates = WorkflowTemplate.query.filter_by(order_type='chat', is_active=True).order_by(WorkflowTemplate.created_date.desc()).all()
        result = [
            {
                'id': t.id,
                'name': t.name,
                'description': t.description,
                'is_default': t.is_default
            } for t in templates
        ]
        return jsonify({'templates': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# 提供一个 /start_workflow API 的薄薄包装器，复用聊天页面路由中的实现，确保测试和前端都能通过 /api/chat/start_workflow 访问
@bp.route('/start_workflow', methods=['POST'])
@login_required
def start_workflow_api():
    """在会话中发起审批（API） - 调用已有的页面路由逻辑"""
    try:
        # 重用 chat_routes 中的实现
        from app.chat_routes import start_workflow_from_chat
        return start_workflow_from_chat()
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    """获取当前用户的所有会话"""
    # 查询用户参与的所有会话
    participant_records = ChatParticipant.query.filter_by(user_id=current_user.id, is_left=False).all()
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
                    'real_name': getattr(other_participant.user, 'real_name', other_participant.user.username)
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
        
        # 优先查找当前用户仍为参与者（未退出）的私聊
        existing_active_conv = db.session.query(ChatConversation).join(
            ChatParticipant, ChatConversation.id == ChatParticipant.conversation_id
        ).filter(
            ChatConversation.conversation_type == 'direct',
            ChatParticipant.user_id.in_([current_user.id, other_user_id]),
            ChatParticipant.is_left == False
        ).group_by(ChatConversation.id).having(
            db.func.count(ChatParticipant.user_id) == 2
        ).first()

        if existing_active_conv:
            return jsonify({
                'conversation': {
                    'id': existing_active_conv.id,
                    'type': existing_active_conv.conversation_type,
                    'name': existing_active_conv.name
                },
                'existed': True
            })

        # 若未找到活跃会话，查找历史会话（可能用户此前退出），尝试恢复当前用户参与状态
        existing_any_conv = db.session.query(ChatConversation).join(
            ChatParticipant, ChatConversation.id == ChatParticipant.conversation_id
        ).filter(
            ChatConversation.conversation_type == 'direct',
            ChatParticipant.user_id.in_([current_user.id, other_user_id])
        ).group_by(ChatConversation.id).having(
            db.func.count(ChatParticipant.user_id) == 2
        ).first()

        if existing_any_conv:
            # 检查当前用户参与记录是否被标记为已退出，若是则恢复
            participant_record = ChatParticipant.query.filter_by(conversation_id=existing_any_conv.id, user_id=current_user.id).first()
            if participant_record and participant_record.is_left:
                participant_record.is_left = False
                participant_record.left_date = None
                db.session.flush()
                db.session.refresh(participant_record)
                db.session.commit()
                return jsonify({
                    'conversation': {
                        'id': existing_any_conv.id,
                        'type': existing_any_conv.conversation_type,
                        'name': existing_any_conv.name
                    },
                    'existed': True,
                    'rejoined': True
                })
            # 如果当前用户此前从未参与该会话，则将其加入会话（避免前端选中后出现 403）
            if not participant_record:
                new_participant = ChatParticipant(conversation_id=existing_any_conv.id, user_id=current_user.id)
                db.session.add(new_participant)
                db.session.commit()
                return jsonify({
                    'conversation': {
                        'id': existing_any_conv.id,
                        'type': existing_any_conv.conversation_type,
                        'name': existing_any_conv.name
                    },
                    'existed': True,
                    'joined': True
                })
            # 否则返回已存在但当前用户未参与的会话（将导致前端 403），交由调用方判断
            return jsonify({
                'conversation': {
                    'id': existing_any_conv.id,
                    'type': existing_any_conv.conversation_type,
                    'name': existing_any_conv.name
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
