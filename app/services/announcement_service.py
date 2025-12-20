"""Announcement service: encapsulate create/edit/upload logic for announcements."""
from datetime import datetime
from app import db
from app.file_upload_utils import save_uploaded_file, generate_thumbnail_async


def create_announcement_from_form(data, files, user):
    """Create an announcement from submitted form data and file list.

    Returns the created Announcement instance.
    """
    # sanitize is handled by routes; this service expects cleaned content
    from app.models import Announcement, AnnouncementAttachment

    announcement = Announcement(
        title=data.get('title'),
        content=data.get('content'),
        type=data.get('type', 'notice'),
        priority=data.get('priority', 'normal'),
        is_pinned=data.get('is_pinned') == '1',
        is_published=data.get('is_active') == '1',
        creator_id=user.id
    )

    # parse times if provided (assume already converted by caller if necessary)
    publish_time = data.get('publish_time')
    if publish_time:
        try:
            # 前端使用 <input type="datetime-local"> 提交的是本地时区值，
            # 将其按 Asia/Shanghai 解释并转换为 UTC 存库（去掉 tzinfo，保持与其他字段一致）
            import pytz
            from datetime import datetime as _dt
            local = pytz.timezone('Asia/Shanghai')
            naive = _dt.strptime(publish_time, '%Y-%m-%dT%H:%M')
            localized = local.localize(naive)
            announcement.publish_time = localized.astimezone(pytz.UTC).replace(tzinfo=None)
        except Exception:
            try:
                announcement.publish_time = datetime.strptime(publish_time, '%Y-%m-%dT%H:%M')
            except Exception:
                pass

    expire_time = data.get('expire_time')
    if expire_time:
        try:
            import pytz
            from datetime import datetime as _dt
            local = pytz.timezone('Asia/Shanghai')
            naive = _dt.strptime(expire_time, '%Y-%m-%dT%H:%M')
            localized = local.localize(naive)
            announcement.expire_time = localized.astimezone(pytz.UTC).replace(tzinfo=None)
        except Exception:
            try:
                announcement.expire_time = datetime.strptime(expire_time, '%Y-%m-%dT%H:%M')
            except Exception:
                pass

    db.session.add(announcement)
    db.session.flush()

    # handle files
    if files:
        for file in files:
            if file and file.filename:
                uploaded = save_uploaded_file(file, folder_type='announcement')
                file_path = uploaded['file_path']
                filename = uploaded['filename']
                stored_filename = uploaded['stored_filename']
                file_size = uploaded['file_size']
                file_type = uploaded['file_type']

                attachment = AnnouncementAttachment(
                    announcement_id=announcement.id,
                    filename=filename,
                    stored_filename=stored_filename,
                    file_path=file_path,
                    file_size=file_size,
                    file_type=file_type,
                    upload_user_id=user.id
                )
                db.session.add(attachment)
                db.session.flush()

                # spawn async thumbnail generation (will update attachment record when done)
                if file_type and file_type.startswith('image/'):
                    generate_thumbnail_async(file_path, attachment_id=attachment.id)

    db.session.commit()
    return announcement


def upload_announcement_image(announcement_id, file, user):
    """Upload single image for rich text editor and return attachment dict."""
    if not file or not file.filename:
        raise ValueError('invalid file')

    from app.models import AnnouncementAttachment

    uploaded = save_uploaded_file(file, folder_type='announcement')
    file_path = uploaded['file_path']
    filename = uploaded['filename']
    stored_filename = uploaded['stored_filename']
    file_size = uploaded['file_size']
    file_type = uploaded['file_type']

    attachment = AnnouncementAttachment(
        announcement_id=announcement_id,
        filename=filename,
        stored_filename=stored_filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
        upload_user_id=user.id
    )
    db.session.add(attachment)
    db.session.flush()

    if file_type and file_type.startswith('image/'):
        generate_thumbnail_async(file_path, attachment_id=attachment.id)

    db.session.commit()
    return attachment
