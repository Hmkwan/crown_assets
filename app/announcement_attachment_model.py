"""公告附件数据模型"""
from app import db
from datetime import datetime, timezone

def get_beijing_now():
    """获取北京时间"""
    from datetime import datetime, timezone, timedelta
    utc_now = datetime.now(timezone.utc)
    beijing_tz = timezone(timedelta(hours=8))
    return utc_now.astimezone(beijing_tz).replace(tzinfo=None)


class AnnouncementAttachment(db.Model):
    """公告附件表"""
    __tablename__ = 'announcement_attachment'
    
    id = db.Column(db.Integer, primary_key=True)
    announcement_id = db.Column(db.Integer, db.ForeignKey('announcement.id'), nullable=False)
    
    # 文件信息
    filename = db.Column(db.String(255), nullable=False)  # 原始文件名
    stored_filename = db.Column(db.String(255), nullable=False)  # 存储文件名(UUID)
    file_path = db.Column(db.String(512), nullable=False)  # 文件路径
    file_size = db.Column(db.Integer, nullable=False)  # 文件大小(字节)
    file_type = db.Column(db.String(128))  # MIME类型
    
    # 预览相关
    thumbnail_path = db.Column(db.String(512))  # 缩略图路径(图片/视频)
    
    # 上传信息
    upload_user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    created_date = db.Column(db.DateTime, default=get_beijing_now)
    
    # 软删除
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)
    
    # 关系
    announcement = db.relationship('Announcement', backref='attachments')
    upload_user = db.relationship('User', foreign_keys=[upload_user_id])
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'announcement_id': self.announcement_id,
            'filename': self.filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'upload_user': self.upload_user.username if self.upload_user else None,
            'created_date': self.created_date.strftime('%Y-%m-%d %H:%M:%S') if self.created_date else None,
            'can_preview': self._can_preview()
        }
    
    def _can_preview(self):
        """判断是否可预览"""
        if not self.file_type:
            return False
        
        previewable_types = [
            'application/pdf',
            'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp',
            'video/mp4', 'video/webm', 'video/ogg',
            'audio/mpeg', 'audio/wav', 'audio/ogg'
        ]
        
        return self.file_type in previewable_types
    
    def __repr__(self):
        return f'<AnnouncementAttachment {self.filename}>'
