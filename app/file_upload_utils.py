"""文件上传处理工具"""
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image

# python-magic是可选依赖,如果没有安装则使用简单的扩展名检测
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {
    'document': {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'},
    'image': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'},
    'video': {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'},
    'audio': {'mp3', 'wav', 'ogg', 'aac', 'm4a'}
}

ALL_ALLOWED_EXTENSIONS = set()
for exts in ALLOWED_EXTENSIONS.values():
    ALL_ALLOWED_EXTENSIONS.update(exts)

# MIME类型映射
MIME_TYPES = {
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xls': 'application/vnd.ms-excel',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'ppt': 'application/vnd.ms-powerpoint',
    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'txt': 'text/plain',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'bmp': 'image/bmp',
    'webp': 'image/webp',
    'mp4': 'video/mp4',
    'avi': 'video/x-msvideo',
    'mov': 'video/quicktime',
    'webm': 'video/webm',
    'mp3': 'audio/mpeg',
    'wav': 'audio/wav',
    'ogg': 'audio/ogg'
}

# 文件大小限制(字节)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 上传目录配置
UPLOAD_FOLDERS = {
    'announcement': 'app/uploads/announcements',
    'chat': 'app/uploads/chat',
    'thumbnail': 'app/uploads/thumbnails'
}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALL_ALLOWED_EXTENSIONS


def get_file_extension(filename):
    """获取文件扩展名"""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def generate_unique_filename(filename):
    """生成唯一文件名"""
    ext = get_file_extension(filename)
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    return unique_name


def get_mime_type(filename):
    """获取文件MIME类型"""
    ext = get_file_extension(filename)
    return MIME_TYPES.get(ext, 'application/octet-stream')


def get_upload_path(folder_type='announcement'):
    """获取上传目录路径"""
    folder = UPLOAD_FOLDERS.get(folder_type, 'app/uploads')
    
    # 确保目录存在
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    
    return folder


def save_uploaded_file(file, folder_type='announcement'):
    """
    保存上传的文件
    
    Args:
        file: FileStorage对象
        folder_type: 文件夹类型
        
    Returns:
        dict: {
            'filename': 原始文件名,
            'stored_filename': 存储文件名,
            'file_path': 文件路径,
            'file_size': 文件大小,
            'file_type': MIME类型
        }
    """
    if not file or not allowed_file(file.filename):
        raise ValueError('不支持的文件类型')
    
    # 安全的文件名
    original_filename = secure_filename(file.filename)
    
    # 生成唯一存储文件名
    stored_filename = generate_unique_filename(original_filename)
    
    # 获取上传目录
    upload_folder = get_upload_path(folder_type)
    
    # 完整文件路径
    file_path = os.path.join(upload_folder, stored_filename)
    
    # 保存文件
    file.save(file_path)
    
    # 获取文件大小
    file_size = os.path.getsize(file_path)
    
    # 检查文件大小
    if file_size > MAX_FILE_SIZE:
        os.remove(file_path)
        raise ValueError(f'文件大小超过限制({MAX_FILE_SIZE / 1024 / 1024}MB)')
    
    # 获取MIME类型
    file_type = get_mime_type(original_filename)
    
    return {
        'filename': original_filename,
        'stored_filename': stored_filename,
        'file_path': file_path,
        'file_size': file_size,
        'file_type': file_type
    }


def create_thumbnail(image_path, max_size=(300, 300)):
    """
    创建缩略图
    
    Args:
        image_path: 原图路径
        max_size: 最大尺寸(宽, 高)
        
    Returns:
        str: 缩略图路径
    """
    try:
        # 打开图片
        img = Image.open(image_path)
        
        # 生成缩略图
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # 生成缩略图文件名
        filename = os.path.basename(image_path)
        stored_filename = f"thumb_{filename}"
        
        # 缩略图保存路径
        thumbnail_folder = get_upload_path('thumbnail')
        thumbnail_path = os.path.join(thumbnail_folder, stored_filename)
        
        # 保存缩略图
        img.save(thumbnail_path, quality=85, optimize=True)
        
        return thumbnail_path
        
    except Exception as e:
        print(f"创建缩略图失败: {e}")
        return None


def delete_file(file_path):
    """删除文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"删除文件失败: {e}")
    return False


def generate_thumbnail_async(file_path, attachment_id=None):
    """
    异步生成缩略图；如果提供 attachment_id，会在生成后更新数据库记录的 thumbnail_path。

    在 TESTING 环境下会同步运行以便测试稳定。
    """
    try:
        # 尽量复用当前 Flask app，上下文在路由中存在
        from flask import current_app
        app = current_app._get_current_object()
    except Exception:
        app = None

    def _worker(path, att_id):
        try:
            thumb = create_thumbnail(path)
            if not thumb:
                return

            if att_id is not None:
                # 更新 DB 中的附件记录
                # 在独立线程中推送 app context
                if app:
                    with app.app_context():
                        from app import db
                        from app.models import AnnouncementAttachment
                        att = AnnouncementAttachment.query.get(att_id)
                        if att:
                            att.thumbnail_path = thumb
                            try:
                                db.session.add(att)
                                db.session.commit()
                            except Exception:
                                db.session.rollback()
                else:
                    # 作为回退，尝试创建临时 app 执行更新
                    try:
                        from app import create_app, db
                        tmp_app = create_app()
                        with tmp_app.app_context():
                            from app.models import AnnouncementAttachment
                            att = AnnouncementAttachment.query.get(att_id)
                            if att:
                                att.thumbnail_path = thumb
                                db.session.add(att)
                                db.session.commit()
                    except Exception:
                        pass
        except Exception:
            pass

    # 在测试环境中直接同步执行，避免异步带来的不确定性
    try:
        if app and app.config.get('TESTING', False):
            _worker(file_path, attachment_id)
            return
    except Exception:
        pass

    try:
        import threading
        t = threading.Thread(target=_worker, args=(file_path, attachment_id), daemon=True)
        t.start()
    except Exception:
        # 最后回退为同步执行
        _worker(file_path, attachment_id)


def format_file_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
