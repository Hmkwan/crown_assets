"""
数据库管理工具模块
提供数据库备份、恢复、重置等功能
"""
import os
import shutil
from datetime import datetime


def get_backup_dir():
    """获取备份目录路径"""
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def backup_database():
    """备份数据库"""
    try:
        from flask import has_app_context, current_app
        if not has_app_context():
            return {'success': False, 'message': '需要在应用上下文中执行'}
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        
        # SQLite 数据库路径
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            
            if not os.path.exists(db_path):
                return {'success': False, 'message': '数据库文件不存在'}
            
            # 创建备份目录
            backup_dir = get_backup_dir()
            
            # 生成备份文件名（带时间戳）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'app_backup_{timestamp}.db'
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # 复制数据库文件
            shutil.copy2(db_path, backup_path)
            
            # 获取文件大小
            file_size = os.path.getsize(backup_path)
            
            return {
                'success': True,
                'message': '备份成功',
                'backup_path': backup_path,
                'backup_filename': backup_filename,
                'file_size': file_size,
                'timestamp': timestamp
            }
        else:
            return {'success': False, 'message': '当前仅支持 SQLite 数据库备份'}
    except Exception as e:
        return {'success': False, 'message': f'备份失败: {str(e)}'}


def restore_database(backup_filename):
    """恢复数据库"""
    try:
        from flask import has_app_context, current_app
        if not has_app_context():
            return {'success': False, 'message': '需要在应用上下文中执行'}
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            backup_dir = get_backup_dir()
            backup_path = os.path.join(backup_dir, backup_filename)
            
            if not os.path.exists(backup_path):
                return {'success': False, 'message': '备份文件不存在'}
            
            # 备份当前数据库（如果存在）
            if os.path.exists(db_path):
                current_backup = f"{db_path}.before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(db_path, current_backup)
            
            # 恢复数据库
            shutil.copy2(backup_path, db_path)
            
            return {
                'success': True,
                'message': '恢复成功',
                'backup_used': backup_filename
            }
        else:
            return {'success': False, 'message': '当前仅支持 SQLite 数据库恢复'}
    except Exception as e:
        return {'success': False, 'message': f'恢复失败: {str(e)}'}


def reset_database():
    """重置数据库（删除所有表并重新创建）"""
    try:
        from flask import has_app_context
        if not has_app_context():
            return {'success': False, 'message': '需要在应用上下文中执行'}
        from app import db
        # 删除所有表
        db.drop_all()
        
        # 重新创建所有表
        db.create_all()
        
        # 初始化数据
        from init_db import init_db, init_equipment_types
        init_db()
        init_equipment_types()
        
        return {
            'success': True,
            'message': '数据库重置成功，已重新初始化',
            'admin_username': 'admin',
            'admin_password': 'admin123'
        }
    except Exception as e:
        return {'success': False, 'message': f'重置失败: {str(e)}'}


def list_backups(filter_date=None):
    """列出所有备份文件
    
    Args:
        filter_date: 筛选日期，可选值：'today', 'yesterday', 'week', 'month', 'all' 或 None（默认全部）
    """
    try:
        backup_dir = get_backup_dir()
        
        if not os.path.exists(backup_dir):
            return {'success': True, 'backups': [], 'total': 0}
        
        backups = []
        now = datetime.now()
        
        for filename in os.listdir(backup_dir):
            if filename.startswith('app_backup_') and filename.endswith('.db'):
                filepath = os.path.join(backup_dir, filename)
                file_stat = os.stat(filepath)
                created_dt = datetime.fromtimestamp(file_stat.st_mtime)
                
                # 日期筛选
                if filter_date:
                    if filter_date == 'today':
                        if created_dt.date() != now.date():
                            continue
                    elif filter_date == 'yesterday':
                        from datetime import timedelta
                        yesterday = now.date() - timedelta(days=1)
                        if created_dt.date() != yesterday:
                            continue
                    elif filter_date == 'week':
                        from datetime import timedelta
                        week_ago = now - timedelta(days=7)
                        if created_dt < week_ago:
                            continue
                    elif filter_date == 'month':
                        from datetime import timedelta
                        month_ago = now - timedelta(days=30)
                        if created_dt < month_ago:
                            continue
                
                # 提取时间戳（从文件名中）
                timestamp_str = filename.replace('app_backup_', '').replace('.db', '')
                
                # 格式化友好时间显示
                time_diff = now - created_dt
                if time_diff.days == 0:
                    if time_diff.seconds < 3600:  # 1小时内
                        if time_diff.seconds < 60:
                            friendly_time = f'刚刚 ({created_dt.strftime("%H:%M:%S")})'
                        else:
                            friendly_time = f'{time_diff.seconds // 60}分钟前 ({created_dt.strftime("%H:%M:%S")})'
                    else:
                        friendly_time = f'今天 {created_dt.strftime("%H:%M:%S")}'
                elif time_diff.days == 1:
                    friendly_time = f'昨天 {created_dt.strftime("%H:%M:%S")}'
                elif time_diff.days < 7:
                    friendly_time = f'{time_diff.days}天前 ({created_dt.strftime("%m-%d %H:%M")})'
                else:
                    friendly_time = created_dt.strftime('%Y-%m-%d %H:%M:%S')
                
                backups.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'created': created_dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'friendly_time': friendly_time,
                    'timestamp': file_stat.st_mtime,
                    'timestamp_str': timestamp_str,
                    'date': created_dt.date().isoformat()
                })
        
        # 按创建时间倒序排列
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {'success': True, 'backups': backups, 'total': len(backups)}
    except Exception as e:
        return {'success': False, 'message': f'获取备份列表失败: {str(e)}', 'backups': [], 'total': 0}


def delete_backup(backup_filename):
    """删除备份文件"""
    try:
        backup_dir = get_backup_dir()
        backup_path = os.path.join(backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            return {'success': False, 'message': '备份文件不存在'}
        
        if not backup_filename.startswith('app_backup_') or not backup_filename.endswith('.db'):
            return {'success': False, 'message': '无效的备份文件名'}
        
        os.remove(backup_path)
        
        return {'success': True, 'message': '备份文件删除成功'}
    except Exception as e:
        return {'success': False, 'message': f'删除失败: {str(e)}'}


def get_database_info():
    """获取数据库信息"""
    try:
        from flask import has_app_context, current_app
        if not has_app_context():
            return {'success': False, 'message': '需要在应用上下文中执行'}
        from app import db
        from sqlalchemy import inspect
        
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        
        info = {
            'type': 'SQLite' if db_uri.startswith('sqlite:///') else 'Unknown',
            'uri': db_uri.split('@')[-1] if '@' in db_uri else db_uri.replace('sqlite:///', '')
        }
        
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            if os.path.exists(db_path):
                info['exists'] = True
                info['size'] = os.path.getsize(db_path)
                info['modified'] = datetime.fromtimestamp(os.path.getmtime(db_path)).strftime('%Y-%m-%d %H:%M:%S')
            else:
                info['exists'] = False
        
        # 获取表信息
        try:
            engine = db.get_engine(current_app)
            insp = inspect(engine)
            info['tables'] = insp.get_table_names()
            info['table_count'] = len(info['tables'])
        except Exception:
            info['tables'] = []
            info['table_count'] = 0
        
        return {'success': True, 'info': info}
    except Exception as e:
        return {'success': False, 'message': f'获取数据库信息失败: {str(e)}'}

