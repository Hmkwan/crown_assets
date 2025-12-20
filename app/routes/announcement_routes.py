from flask import Blueprint, request, jsonify, send_file
from app import db
from app.models import Announcement, AnnouncementAttachment
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from datetime import datetime

announcement_bp = Blueprint('announcement', __name__)

@announcement_bp.route('/create_announcement', methods=['POST'])
@login_required
def create_announcement():
    """创建公告"""
    try:
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        valid_until = data.get('valid_until')

        if not title or not content:
            return jsonify({'error': '标题和内容不能为空'}), 400

        announcement = Announcement(
            title=title,
            content=content,
            creator_id=current_user.id,
            valid_until=valid_until
        )
        db.session.add(announcement)
        db.session.commit()

        return jsonify({'message': '公告创建成功', 'announcement_id': announcement.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@announcement_bp.route('/get_announcements', methods=['GET'])
@login_required
def get_announcements():
    """获取公告列表"""
    try:
        announcements = Announcement.query.filter(
            (Announcement.valid_until == None) | (Announcement.valid_until >= db.func.now())
        ).all()

        result = [
            {
                'id': a.id,
                'title': a.title,
                'content': a.content,
                'creator_id': a.creator_id,
                'created_at': a.created_at,
                'valid_until': a.valid_until
            } for a in announcements
        ]

        return jsonify({'announcements': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@announcement_bp.route('/upload_attachment', methods=['POST'])
@login_required
def upload_attachment():
    """上传公告附件"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    # 确保上传目录存在
    upload_folder = 'app/static/uploads/announcements'
    os.makedirs(upload_folder, exist_ok=True)

    # 生成安全的文件名
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    stored_filename = f"{timestamp}_{filename}"
    file_path = os.path.join(upload_folder, stored_filename)

    # 保存文件
    file.save(file_path)

    attachment = AnnouncementAttachment(
        file_name=filename,
        file_path=file_path
    )
    db.session.add(attachment)
    db.session.commit()

    return jsonify({
        'attachment_id': attachment.id,
        'file_name': attachment.file_name,
        'file_path': attachment.file_path
    }), 201

@announcement_bp.route('/attachments/<int:attachment_id>/download', methods=['GET'])
@login_required
def download_attachment(attachment_id):
    """下载公告附件"""
    attachment = AnnouncementAttachment.query.get_or_404(attachment_id)
    return send_file(
        attachment.file_path,
        as_attachment=True,
        download_name=attachment.file_name
    )

@announcement_bp.route('/api/announcements/<int:announcement_id>', methods=['GET'])
@login_required
def get_announcement(announcement_id):
    """获取单个公告的详细信息"""
    try:
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return jsonify({'error': '公告不存在'}), 404

        result = {
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'creator_id': announcement.creator_id,
            'created_at': announcement.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'valid_until': announcement.valid_until.strftime('%Y-%m-%d %H:%M:%S') if announcement.valid_until else None
        }

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500