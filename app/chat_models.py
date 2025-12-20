"""
聊天系统数据库模型
支持一对一聊天和群组聊天
"""
from app import db
from datetime import datetime, timezone, timedelta


def get_beijing_now():
    """获取北京时间"""
    utc_now = datetime.now(timezone.utc)
    beijing_tz = timezone(timedelta(hours=8))
    return utc_now.astimezone(beijing_tz).replace(tzinfo=None)


class ChatConversation(db.Model):
    """会话表 - 一对一或群组会话"""
    __tablename__ = 'chat_conversation'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 会话类型: direct(一对一), group(群组)
    conversation_type = db.Column(db.String(20), nullable=False, default='direct')
    
    # 会话名称(群组会话需要,一对一会话可为空)
    name = db.Column(db.String(200))
    
    # 会话头像(群组会话)
    avatar_url = db.Column(db.String(512))
    
    # 会话描述
    description = db.Column(db.Text)
    
    # 创建者
    creator_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    
    # 是否激活
    is_active = db.Column(db.Boolean, default=True)
    
    # 时间戳
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    updated_date = db.Column(db.DateTime, default=get_beijing_now, onupdate=get_beijing_now)
    
    # 最后一条消息(冗余字段,用于显示)
    last_message_id = db.Column(db.Integer, db.ForeignKey('chat_message.id', use_alter=True, name='fk_chat_conversation_last_message'))
    last_message_time = db.Column(db.DateTime)
    
    # 关系
    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_conversations')
    participants = db.relationship('ChatParticipant', back_populates='conversation', cascade='all, delete-orphan')
    messages = db.relationship('ChatMessage', back_populates='conversation', cascade='all, delete-orphan', foreign_keys='ChatMessage.conversation_id')
    last_message = db.relationship('ChatMessage', foreign_keys=[last_message_id], post_update=True)
    
    def to_dict(self, current_user_id=None):
        """转换为字典"""
        data = {
            'id': self.id,
            'type': self.conversation_type,
            'name': self.name,
            'avatar': self.avatar_url,
            'description': self.description,
            'created_date': self.created_date.strftime('%Y-%m-%d %H:%M:%S') if self.created_date else None,
            'last_message_time': self.last_message_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_message_time else None,
            'participant_count': len(self.participants),
            'is_active': self.is_active
        }
        
        # 对于一对一会话,获取对方信息
        if self.conversation_type == 'direct' and current_user_id:
            other_participant = next(
                (p for p in self.participants if p.user_id != current_user_id),
                None
            )
            if other_participant and other_participant.user:
                data['other_user'] = {
                    'id': other_participant.user.id,
                    'username': other_participant.user.username,
                    'real_name': getattr(other_participant.user, 'real_name', other_participant.user.username),
                    'avatar': getattr(other_participant.user, 'avatar', None)
                }
        
        # 未读消息数(如果提供了current_user_id)
        if current_user_id:
            participant = next((p for p in self.participants if p.user_id == current_user_id), None)
            data['unread_count'] = participant.unread_count if participant else 0
        
        return data
    
    def __repr__(self):
        return f'<ChatConversation {self.id}: {self.name or "Direct Chat"}>'


class ChatParticipant(db.Model):
    """会话参与者表"""
    __tablename__ = 'chat_participant'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('chat_conversation.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    
    # 加入时间
    joined_date = db.Column(db.DateTime, default=get_beijing_now)
    
    # 最后阅读的消息ID
    last_read_message_id = db.Column(db.Integer, db.ForeignKey('chat_message.id', use_alter=True, name='fk_chat_conversation_last_read'))
    
    # 未读消息数(冗余字段,提高查询性能)
    unread_count = db.Column(db.Integer, default=0)
    
    # 是否置顶
    is_pinned = db.Column(db.Boolean, default=False)
    
    # 是否静音
    is_muted = db.Column(db.Boolean, default=False)
    
    # 是否已退出
    is_left = db.Column(db.Boolean, default=False)
    left_date = db.Column(db.DateTime)
    
    # 角色: member(普通成员), admin(管理员), owner(所有者)
    role = db.Column(db.String(20), default='member')
    
    # 关系
    conversation = db.relationship('ChatConversation', back_populates='participants')
    user = db.relationship('User', backref='chat_participations')
    last_read_message = db.relationship('ChatMessage', foreign_keys=[last_read_message_id], post_update=True)
    
    def __repr__(self):
        return f'<ChatParticipant conversation={self.conversation_id} user={self.user_id}>'


class ChatMessage(db.Model):
    """消息表"""
    __tablename__ = 'chat_message'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('chat_conversation.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    
    # 消息类型: text(文本), image(图片), file(文件), system(系统消息)
    message_type = db.Column(db.String(20), nullable=False, default='text')
    
    # 消息内容
    content = db.Column(db.Text)
    
    # 是否已撤回
    is_recalled = db.Column(db.Boolean, default=False)
    recalled_date = db.Column(db.DateTime)
    
    # 是否已删除
    is_deleted = db.Column(db.Boolean, default=False)
    
    # 时间戳
    created_date = db.Column(db.DateTime, default=get_beijing_now, index=True)
    
    # 引用的消息(回复功能)
    reply_to_message_id = db.Column(db.Integer, db.ForeignKey('chat_message.id'))
    
    # 关系
    conversation = db.relationship('ChatConversation', back_populates='messages', foreign_keys=[conversation_id])
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    attachments = db.relationship('ChatAttachment', back_populates='message', cascade='all, delete-orphan')
    reply_to = db.relationship('ChatMessage', remote_side=[id], backref='replies', foreign_keys=[reply_to_message_id])
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.username if self.sender else 'Unknown',
            'sender_real_name': getattr(self.sender, 'real_name', self.sender.username) if self.sender else None,
            'message_type': self.message_type,
            'content': self.content if not self.is_recalled else '[消息已撤回]',
            'is_recalled': self.is_recalled,
            'created_date': self.created_date.strftime('%Y-%m-%d %H:%M:%S') if self.created_date else None,
            'attachments': [att.to_dict() for att in self.attachments] if self.attachments else [],
            'reply_to': self.reply_to.to_dict() if self.reply_to and not self.reply_to.is_recalled else None
        }
    
    def __repr__(self):
        return f'<ChatMessage {self.id} in conversation {self.conversation_id}>'


class ChatAttachment(db.Model):
    """聊天附件表"""
    __tablename__ = 'chat_attachment'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('chat_message.id'), nullable=False)
    
    # 文件信息
    filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(128))  # MIME类型
    
    # 缩略图(图片/视频)
    thumbnail_path = db.Column(db.String(512))
    
    # 上传时间
    created_date = db.Column(db.DateTime, default=get_beijing_now)

    # 上传用户
    upload_user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    upload_user = db.relationship('User', foreign_keys=[upload_user_id], backref='uploaded_attachments')
    
    # 关系
    message = db.relationship('ChatMessage', back_populates='attachments')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'filename': self.filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'is_image': self.file_type.startswith('image/') if self.file_type else False,
            'thumbnail_url': f'/api/chat/attachments/{self.id}/thumbnail' if self.thumbnail_path else None,
            'download_url': f'/api/chat/attachments/{self.id}/download'
        }
    
    def __repr__(self):
        return f'<ChatAttachment {self.filename}>'


class ChatPermission(db.Model):
    """聊天权限管理表"""
    __tablename__ = 'chat_permission'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    
    # 是否可以发送消息
    can_send_message = db.Column(db.Boolean, default=True)
    
    # 是否可以发送文件
    can_send_file = db.Column(db.Boolean, default=True)
    
    # 是否可以创建群组
    can_create_group = db.Column(db.Boolean, default=True)
    
    # 禁言截止时间
    muted_until = db.Column(db.DateTime)
    
    # 备注
    notes = db.Column(db.Text)
    
    # 操作管理员
    operated_by_id = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    operated_date = db.Column(db.DateTime, default=get_beijing_now)
    
    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref='chat_permission')
    operated_by = db.relationship('User', foreign_keys=[operated_by_id])
    
    def is_muted(self):
        """检查是否被禁言"""
        if not self.muted_until:
            return False
        return datetime.now() < self.muted_until
    
    def __repr__(self):
        return f'<ChatPermission user={self.user_id}>'
