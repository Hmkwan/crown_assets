"""系统公告路由"""
from datetime import datetime, timezone
import os
from flask import render_template, request, jsonify, flash, redirect, url_for, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.main import bp
from app import db
from app.models import Announcement, UserActivityLog, AnnouncementAttachment
from app.decorators import admin_required, module_permission_required
from app.file_upload_utils import (
    save_uploaded_file, 
    create_thumbnail, 
    delete_file, 
    allowed_file,
    format_file_size,
    generate_thumbnail_async
)
from app.services.announcement_service import (
    create_announcement_from_form,
    upload_announcement_image
)

# 尝试导入 bleach 做 HTML 清洗
try:
    import bleach
    HAS_BLEACH = True
except Exception:
    HAS_BLEACH = False


def sanitize_html(html_content):
    """清洗 HTML，防止 XSS。优先使用 bleach，否则做简单 script 标签移除"""
    if not html_content:
        return html_content
    if HAS_BLEACH:
        allowed_tags = bleach.sanitizer.ALLOWED_TAGS + [
            'p', 'div', 'span', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'thead', 'tbody', 'tr', 'td', 'th', 'img'
        ]
        allowed_attrs = {
            '*': ['class', 'style'],
            'a': ['href', 'title', 'target', 'rel'],
            'img': ['src', 'alt', 'title', 'width', 'height']
        }
        return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attrs, protocols=['http','https','mailto'], strip=True)
    else:
        # 简单移除 <script>...</script>
        import re
        return re.sub(r'<script[\s\S]*?>[\s\S]*?<\/script>', '', html_content, flags=re.IGNORECASE)


def _log_activity(action, description):
    """记录操作日志"""
    import logging
    logger = logging.getLogger(__name__)
    try:
        ip = request.headers.get('X-Forwarded-For') or request.headers.get('X-Real-IP') or request.remote_addr or ''
        activity_log = UserActivityLog(
            user_id=current_user.id,
            action=action,
            description=f"{description} (IP: {ip})"
        )
        db.session.add(activity_log)
        try:
            db.session.commit()
        except Exception as e:
            logger.warning('记录活动日志时提交失败: %s', e, exc_info=True)
            try:
                db.session.rollback()
            except Exception:
                logger.debug('回滚活动日志事务失败（忽略）', exc_info=True)
    except Exception as e:
        logger.warning('记录活动日志失败: %s', e, exc_info=True)


@bp.route('/announcements')
@login_required
def announcements():
    """公告列表页面 - 所有用户可见"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 获取有效公告
    announcements = Announcement.get_active_announcements()
    
    # 手动分页
    total = len(announcements)
    start = (page - 1) * per_page
    end = start + per_page
    announcements_page = announcements[start:end]
    
    # 记录访问
    if page == 1:  # 只在第一页记录,避免重复
        _log_activity('查看公告', f'访问系统公告列表')
    
    return render_template('announcements/list.html',
                         announcements=announcements_page,
                         page=page,
                         per_page=per_page,
                         total=total)


@bp.route('/announcements/<int:id>')
@login_required
def announcement_detail(id):
    """公告详情页面"""
    announcement = Announcement.query.get_or_404(id)
    
    # 检查公告是否可见
    if not announcement.is_active and not current_user.is_admin:
        flash('该公告不存在或已过期', 'warning')
        return redirect(url_for('main.announcements'))
    
    # 记录访问
    _log_activity('查看公告详情', f'查看公告: {announcement.title} (ID: {announcement.id})')
    
    return render_template('announcements/detail.html', announcement=announcement)


@bp.route('/admin/announcements')
@login_required
@module_permission_required('announcement', 'view')
def admin_announcements():
    """公告管理页面 - 仅管理员"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 获取所有公告(包括未发布的)
    pagination = Announcement.query.order_by(
        Announcement.is_pinned.desc(),
        Announcement.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # 记录访问
    if page == 1:  # 只在第一页记录
        _log_activity('管理公告', '访问公告管理页面')
    
    return render_template('admin/announcements/manage.html',
                         announcements=pagination.items,
                         pagination=pagination)


@bp.route('/admin/announcements/create', methods=['GET', 'POST'])
@login_required
@module_permission_required('announcement', 'create')
def create_announcement():
    """创建公告"""
    if request.method == 'POST':
        try:
            import logging
            logger = logging.getLogger(__name__)
            # 防止在处理表单并验证之前发生隐式 autoflush，使用 no_autoflush 做防护
            with db.session.no_autoflush:
                data = request.form

                # 优先读取已被 JS 填充的隐藏字段（防止 textarea/name 冲突导致 content 为空）
                content_raw = data.get('content') or request.form.get('content_hidden')
                data = data.copy()
                data['content'] = sanitize_html(content_raw)

                # 后端校验：禁止保存空内容（防止编辑时误把正文覆写为空）
                if not data['content'] or not data['content'].strip() or data['content'].strip() == '<p><br></p>':
                    flash('公告内容不能为空', 'danger')
                    return render_template('admin/announcements/form_new.html', announcement=None)

                files = request.files.getlist('attachments')

                announcement = create_announcement_from_form(data, files, current_user)

            # 记录日志
            _log_activity('创建公告', f'创建公告: {announcement.title} (ID: {announcement.id})')
            flash('公告创建成功!', 'success')
            return redirect(url_for('main.edit_announcement', id=announcement.id, preview=1))
        except Exception as e:
            db.session.rollback()
            logger.exception('创建公告时发生异常')
            flash('创建公告失败: 服务器发生错误，请稍后重试', 'danger')
    
    return render_template('admin/announcements/form_new.html', announcement=None)


@bp.route('/admin/announcements/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@module_permission_required('announcement', 'edit')
def edit_announcement(id):
    """编辑公告"""
    announcement = Announcement.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            import logging
            logger = logging.getLogger(__name__)
            # 防止在表单验证前发生隐式 autoflush，使用 no_autoflush
            with db.session.no_autoflush:
                data = request.form

                # 更新公告 (清洗内容以防 XSS)
                # 先从请求读取并清洗内容（不直接赋值到模型，避免在后续查询触发 autoflush 导致提前写入 NULL）
                title = data.get('title')
                content_raw = data.get('content') or request.form.get('content_hidden')
                sanitized = sanitize_html(content_raw)

                # 后端校验：禁止把内容置空
                if not sanitized or not sanitized.strip() or sanitized.strip() == '<p><br></p>':
                    flash('公告内容不能为空，保存已取消', 'danger')
                    return render_template('admin/announcements/form_new.html', announcement=announcement)

                # 校验通过后再赋值到模型
                announcement.title = title
                announcement.content = sanitized

                publish_time = data.get('publish_time')
                if publish_time:
                    try:
                        import pytz
                        local = pytz.timezone('Asia/Shanghai')
                        naive = datetime.strptime(publish_time, '%Y-%m-%dT%H:%M')
                        localized = local.localize(naive)
                        announcement.publish_time = localized.astimezone(pytz.UTC).replace(tzinfo=None)
                    except Exception:
                        # 回退到直接解析（不含时区信息）
                        announcement.publish_time = datetime.strptime(publish_time, '%Y-%m-%dT%H:%M')
                else:
                    announcement.publish_time = None

                expire_time = data.get('expire_time')
                if expire_time:
                    try:
                        import pytz
                        local = pytz.timezone('Asia/Shanghai')
                        naive = datetime.strptime(expire_time, '%Y-%m-%dT%H:%M')
                        localized = local.localize(naive)
                        announcement.expire_time = localized.astimezone(pytz.UTC).replace(tzinfo=None)
                    except Exception:
                        announcement.expire_time = datetime.strptime(expire_time, '%Y-%m-%dT%H:%M')
                else:
                    announcement.expire_time = None

                # 处理文件上传 (使用 save_uploaded_file，并在图片时生成缩略图)
                files = request.files.getlist('attachments')
                if files:
                    for file in files:
                        if file and file.filename:
                            try:
                                uploaded = save_uploaded_file(file, folder_type='announcement')
                                file_path = uploaded['file_path']
                                filename = uploaded['filename']
                                stored_filename = uploaded['stored_filename']
                                file_size = uploaded['file_size']
                                file_type = uploaded['file_type']

                                # 创建附件记录
                                attachment = AnnouncementAttachment(
                                    announcement_id=announcement.id,
                                    filename=filename,
                                    stored_filename=stored_filename,
                                    file_path=file_path,
                                    file_size=file_size,
                                    file_type=file_type,
                                    upload_user_id=current_user.id
                                )

                                # 如果是图片，创建缩略图
                                if file_type and file_type.startswith('image/'):
                                    try:
                                        thumb = create_thumbnail(file_path)
                                        if thumb:
                                            attachment.thumbnail_path = thumb
                                    except Exception:
                                        pass

                                db.session.add(attachment)
                            except Exception as e:
                                print(f"文件上传失败: {file.filename}, 错误: {str(e)}")

            db.session.commit()

            # 记录日志
            _log_activity('编辑公告', f'编辑公告: {announcement.title} (ID: {announcement.id})')

            flash('公告更新成功!', 'success')
            # 编辑后保持在编辑页面并展示预览
            return redirect(url_for('main.edit_announcement', id=announcement.id, preview=1))

        except Exception as e:
            db.session.rollback()
            logger.exception('编辑公告时发生异常')
            flash('更新公告失败: 服务器发生错误，请稍后重试', 'danger')
    
    return render_template('admin/announcements/form_new.html', announcement=announcement)


@bp.route('/admin/announcements/<int:id>/delete', methods=['POST'])
@login_required
@module_permission_required('announcement', 'delete')
def delete_announcement(id):
    """删除公告"""
    try:
        announcement = Announcement.query.get_or_404(id)
        title = announcement.title
        
        db.session.delete(announcement)
        db.session.commit()
        
        # 记录日志
        _log_activity('删除公告', f'删除公告: {title} (ID: {id})')
        
        flash('公告已删除', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/admin/announcements/<int:id>/toggle-publish', methods=['POST'])
@login_required
@module_permission_required('announcement', 'publish')
def toggle_announcement_publish(id):
    """切换公告发布状态"""
    try:
        announcement = Announcement.query.get_or_404(id)
        announcement.is_published = not announcement.is_published
        
        # 如果发布且没有发布时间,设置为当前时间
        if announcement.is_published and not announcement.publish_time:
            announcement.publish_time = datetime.now(timezone.utc)
        
        db.session.commit()
        
        status = '已发布' if announcement.is_published else '已取消发布'
        
        # 记录日志
        _log_activity('发布公告' if announcement.is_published else '取消发布公告',
                     f'{status}: {announcement.title} (ID: {announcement.id})')
        
        return jsonify({
            'success': True,
            'is_published': announcement.is_published,
            'message': f'公告{status}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/admin/announcements/<int:id>/toggle-pin', methods=['POST'])
@login_required
@module_permission_required('announcement', 'edit')
def toggle_announcement_pin(id):
    """切换公告置顶状态"""
    try:
        announcement = Announcement.query.get_or_404(id)
        announcement.is_pinned = not announcement.is_pinned
        db.session.commit()
        
        status = '已置顶' if announcement.is_pinned else '已取消置顶'
        
        # 记录日志
        _log_activity('置顶公告' if announcement.is_pinned else '取消置顶',
                     f'{status}: {announcement.title} (ID: {announcement.id})')
        
        return jsonify({
            'success': True,
            'is_pinned': announcement.is_pinned,
            'message': f'公告{status}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# API接口
@bp.route('/api/announcements/active')
@login_required
def api_active_announcements():
    """获取有效公告列表 - API接口"""
    limit = request.args.get('limit', 5, type=int)
    announcements = Announcement.get_active_announcements(limit=limit)
    
    return jsonify({
        'success': True,
        'data': [a.to_dict() for a in announcements]
    })


# ==================== 附件管理 ====================

@bp.route('/api/announcements/<int:announcement_id>/upload', methods=['POST'])
@login_required
@admin_required
def upload_announcement_file(announcement_id):
    """上传公告附件"""
    try:
        # 检查公告是否存在
        announcement = Announcement.query.get_or_404(announcement_id)
        
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '未选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '不支持的文件类型'}), 400
        
        # 保存文件
        file_info = save_uploaded_file(file, folder_type='announcement')
        
        # 如果是图片,创建缩略图
        thumbnail_path = None
        if file_info['file_type'].startswith('image/'):
            thumbnail_path = create_thumbnail(file_info['file_path'])
        
        # 创建附件记录
        attachment = AnnouncementAttachment(
            announcement_id=announcement_id,
            filename=file_info['filename'],
            stored_filename=file_info['stored_filename'],
            file_path=file_info['file_path'],
            file_size=file_info['file_size'],
            file_type=file_info['file_type'],
            thumbnail_path=thumbnail_path,
            upload_user_id=current_user.id
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        # 记录日志
        _log_activity('上传附件', f'为公告 "{announcement.title}" 上传附件: {file_info["filename"]}')
        
        return jsonify({
            'success': True,
            'data': attachment.to_dict()
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'上传失败: {str(e)}'}), 500


@bp.route('/api/announcements/<int:announcement_id>/attachments')
@login_required
def get_announcement_attachments(announcement_id):
    """获取公告附件列表"""
    try:
        announcement = Announcement.query.get_or_404(announcement_id)
        
        attachments = AnnouncementAttachment.query.filter_by(
            announcement_id=announcement_id,
            is_deleted=False
        ).order_by(AnnouncementAttachment.created_date.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [att.to_dict() for att in attachments]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/attachments/<int:attachment_id>/download')
@login_required
def download_attachment(attachment_id):
    """下载附件"""
    try:
        attachment = AnnouncementAttachment.query.get_or_404(attachment_id)
        
        if attachment.is_deleted:
            return jsonify({'success': False, 'error': '附件已删除'}), 404
        
        # 记录下载日志
        _log_activity('下载附件', f'下载附件: {attachment.filename}')
        
        return send_file(
            attachment.file_path,
            as_attachment=True,
            download_name=attachment.filename
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/attachments/<int:attachment_id>/preview')
@login_required
def preview_attachment(attachment_id):
    """预览附件"""
    try:
        attachment = AnnouncementAttachment.query.get_or_404(attachment_id)
        
        if attachment.is_deleted:
            return jsonify({'success': False, 'error': '附件已删除'}), 404
        
        # 返回文件以供预览
        return send_file(
            attachment.file_path,
            mimetype=attachment.file_type
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/announcements/<int:announcement_id>/upload_image', methods=['POST'])
@login_required
@admin_required
def upload_announcement_image(announcement_id):
    """用于富文本编辑器的图片上传接口: 将图片保存为附件并返回预览 URL"""
    try:
        announcement = Announcement.query.get_or_404(announcement_id)
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '未提供文件'}), 400
        file = request.files['file']
        if not file or not file.filename:
            return jsonify({'success': False, 'error': '文件无效'}), 400

        # delegate upload to service (service will schedule thumbnail generation asynchronously)
        attachment = upload_announcement_image(announcement.id, file, current_user)
        preview_url = url_for('main.preview_attachment', attachment_id=attachment.id)
        return jsonify({'success': True, 'url': preview_url, 'attachment_id': attachment.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/announcements/attachments/<int:attachment_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_announcement_attachment(attachment_id):
    """删除公告附件"""
    try:
        attachment = AnnouncementAttachment.query.get_or_404(attachment_id)
        
        filename = attachment.filename
        
        # 删除物理文件
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)
        
        # 删除数据库记录
        db.session.delete(attachment)
        db.session.commit()
        
        # 记录日志
        _log_activity('删除附件', f'删除附件: {filename}')
        
        return jsonify({'success': True, 'message': '附件已删除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/announcements/attachments/<int:attachment_id>/download')
@login_required
def download_announcement_attachment(attachment_id):
    """下载公告附件"""
    try:
        attachment = AnnouncementAttachment.query.get_or_404(attachment_id)
        
        # 记录下载日志
        _log_activity('下载附件', f'下载附件: {attachment.filename}')
        
        return send_file(
            attachment.file_path,
            as_attachment=True,
            download_name=attachment.filename
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/attachments/<int:attachment_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_attachment(attachment_id):
    """删除附件(软删除)"""
    try:
        attachment = AnnouncementAttachment.query.get_or_404(attachment_id)
        
        if attachment.is_deleted:
            return jsonify({'success': False, 'error': '附件已删除'}), 400
        
        # 软删除
        attachment.is_deleted = True
        attachment.deleted_date = datetime.now(timezone.utc)
        db.session.commit()
        
        # 记录日志
        _log_activity('删除附件', f'删除附件: {attachment.filename}')
        
        return jsonify({'success': True, 'message': '附件已删除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

