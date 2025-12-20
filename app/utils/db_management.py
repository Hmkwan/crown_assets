"""
数据库管理工具模块
提供数据库备份、恢复、重置等功能
"""
import os
import shutil
from datetime import datetime, timedelta, timezone
import subprocess
import shlex
import sys
import gzip
import re
from urllib.parse import urlparse
try:
    import pytz
except Exception:
    pytz = None
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None


def get_backup_dir():
    """获取备份目录路径"""
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    backup_dir = os.path.join(PROJECT_ROOT, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def backup_database(compress=True):
    """备份数据库
    
    Args:
        compress: 是否压缩备份文件（仅PostgreSQL）
    """
    try:
        from flask import has_app_context, current_app
        if not has_app_context():
            return {'success': False, 'message': '需要在应用上下文中执行'}
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        
        # 创建备份目录
        backup_dir = get_backup_dir()
        
        # 生成时间戳
        try:
            if pytz:
                tz = pytz.timezone('Asia/Shanghai')
                now = datetime.now(tz)
            else:
                now = datetime.utcnow() + timedelta(hours=8)
        except Exception:
            now = datetime.utcnow()
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        
        # SQLite 数据库路径
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            
            if not os.path.exists(db_path):
                return {'success': False, 'message': '数据库文件不存在'}
            
            backup_filename = f'app_backup_{timestamp}.db'
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # 复制数据库文件
            shutil.copy2(db_path, backup_path)
            
            # 获取文件大小
            file_size = os.path.getsize(backup_path)
            
            return {
                'success': True,
                'message': 'SQLite备份成功',
                'backup_path': backup_path,
                'backup_filename': backup_filename,
                'file_size': file_size,
                'timestamp': timestamp,
                'db_type': 'sqlite'
            }
        
        # PostgreSQL 数据库
        elif db_uri.startswith('postgresql://') or db_uri.startswith('postgres://'):
            # 解析数据库连接信息
            parsed = urlparse(db_uri)
            host = parsed.hostname or 'localhost'
            port = parsed.port or 5432
            username = parsed.username or 'postgres'
            password = parsed.password
            database = parsed.path.lstrip('/')
            
            # 生成备份文件名
            if compress:
                backup_filename = f'postgresql_backup_{timestamp}.sql.gz'
            else:
                backup_filename = f'postgresql_backup_{timestamp}.sql'
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # 设置环境变量（用于pg_dump密码）
            env = os.environ.copy()
            if password:
                env['PGPASSWORD'] = password
            
            try:
                # 执行pg_dump
                if compress:
                    # 直接输出到压缩文件
                    cmd = [
                        'pg_dump',
                        '-h', host,
                        '-p', str(port),
                        '-U', username,
                        '-d', database,
                        '--no-owner',  # 不包含所有者信息
                        '--no-privileges',  # 不包含权限信息
                        '-F', 'c',  # 自定义压缩格式
                        '-f', backup_path
                    ]
                else:
                    # 纯SQL格式
                    cmd = [
                        'pg_dump',
                        '-h', host,
                        '-p', str(port),
                        '-U', username,
                        '-d', database,
                        '--no-owner',
                        '--no-privileges',
                        '-f', backup_path
                    ]
                
                result = subprocess.run(
                    cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分钟超时
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr or result.stdout
                    # 检查是否是pg_dump不存在的错误
                    if 'not found' in error_msg.lower() or 'is not recognized' in error_msg.lower():
                        return {
                            'success': False,
                            'message': 'pg_dump命令不存在，请安装PostgreSQL客户端工具。Windows: 安装PostgreSQL并添加到PATH; Linux: sudo apt install postgresql-client'
                        }
                    return {'success': False, 'message': f'pg_dump执行失败: {error_msg}'}
                
                # 检查备份文件是否创建成功
                if not os.path.exists(backup_path):
                    return {'success': False, 'message': '备份文件创建失败'}
                
                # 获取文件大小
                file_size = os.path.getsize(backup_path)
                
                # 如果是压缩格式，计算压缩比
                compression_ratio = None
                if compress:
                    # 估算压缩比（基于文件大小）
                    compression_ratio = 'N/A'  # 自定义格式无法直接计算
                
                return {
                    'success': True,
                    'message': 'PostgreSQL备份成功',
                    'backup_path': backup_path,
                    'backup_filename': backup_filename,
                    'file_size': file_size,
                    'timestamp': timestamp,
                    'db_type': 'postgresql',
                    'compressed': compress,
                    'compression_ratio': compression_ratio
                }
                
            except subprocess.TimeoutExpired:
                return {'success': False, 'message': '备份超时（超过5分钟），请检查数据库连接'}
            except FileNotFoundError:
                # pg_dump 不存在，使用 Python 备份方案
                try:
                    result = _python_postgresql_backup(db_uri, backup_dir, timestamp, compress)
                    if result['success']:
                        result['message'] += ' (使用Python备份)'
                    return result
                except Exception as fallback_error:
                    return {
                        'success': False,
                        'message': f'pg_dump不可用且Python备份失败: {str(fallback_error)}'
                    }
        
        else:
            return {'success': False, 'message': f'不支持的数据库类型: {db_uri.split(":")[0]}'}
            
    except Exception as e:
        import traceback
        return {'success': False, 'message': f'备份失败: {str(e)}', 'trace': traceback.format_exc()}


def restore_database(backup_filename, auto_backup=True):
    """恢复数据库
    
    Args:
        backup_filename: 备份文件名
        auto_backup: 恢复前是否自动备份当前数据库
    """
    try:
        from flask import has_app_context, current_app
        if not has_app_context():
            return {'success': False, 'message': '需要在应用上下文中执行'}
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        backup_dir = get_backup_dir()
        backup_path = os.path.join(backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            return {'success': False, 'message': '备份文件不存在'}
        
        # SQLite数据库恢复
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            
            # 验证备份文件
            if not backup_filename.endswith('.db'):
                return {'success': False, 'message': 'SQLite备份文件必须是.db格式'}
            
            # 自动备份当前数据库
            if auto_backup and os.path.exists(db_path):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                current_backup = f"{db_path}.before_restore_{timestamp}"
                shutil.copy2(db_path, current_backup)
            
            # 恢复数据库
            shutil.copy2(backup_path, db_path)
            
            return {
                'success': True,
                'message': 'SQLite数据库恢复成功',
                'backup_used': backup_filename,
                'db_type': 'sqlite'
            }
        
        # PostgreSQL数据库恢复
        elif db_uri.startswith('postgresql://') or db_uri.startswith('postgres://'):
            # 验证备份文件
            if not (backup_filename.endswith('.sql') or backup_filename.endswith('.sql.gz')):
                return {'success': False, 'message': 'PostgreSQL备份文件必须是.sql或.sql.gz格式'}
            
            # 解析数据库连接信息
            parsed = urlparse(db_uri)
            host = parsed.hostname or 'localhost'
            port = parsed.port or 5432
            username = parsed.username or 'postgres'
            password = parsed.password
            database = parsed.path.lstrip('/')
            
            # 自动备份当前数据库
            if auto_backup:
                backup_result = backup_database(compress=True)
                if not backup_result.get('success'):
                    return {
                        'success': False,
                        'message': f'恢复前自动备份失败: {backup_result.get("message")}'
                    }
            
            # 设置环境变量
            env = os.environ.copy()
            if password:
                env['PGPASSWORD'] = password
            
            try:
                # 判断是否是压缩格式
                is_compressed = backup_filename.endswith('.gz')
                
                if is_compressed or backup_filename.endswith('.sql.gz'):
                    # 使用pg_restore恢复压缩备份
                    # 先清空数据库
                    drop_cmd = [
                        'psql',
                        '-h', host,
                        '-p', str(port),
                        '-U', username,
                        '-d', 'postgres',  # 连接到postgres数据库
                        '-c', f'DROP DATABASE IF EXISTS {database}; CREATE DATABASE {database};'
                    ]
                    
                    drop_result = subprocess.run(
                        drop_cmd,
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if drop_result.returncode != 0:
                        # 尝试只清空表（如果无法删除数据库）
                        pass
                    
                    # 使用pg_restore恢复
                    cmd = [
                        'pg_restore',
                        '-h', host,
                        '-p', str(port),
                        '-U', username,
                        '-d', database,
                        '--clean',  # 恢复前清理
                        '--if-exists',  # 如果对象存在才删除
                        '--no-owner',
                        '--no-privileges',
                        backup_path
                    ]
                else:
                    # 使用psql恢复SQL文件
                    cmd = [
                        'psql',
                        '-h', host,
                        '-p', str(port),
                        '-U', username,
                        '-d', database,
                        '-f', backup_path
                    ]
                
                result = subprocess.run(
                    cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=600  # 10分钟超时
                )
                
                # PostgreSQL恢复可能会有警告但成功，所以不严格检查returncode
                if result.returncode != 0 and 'ERROR' in result.stderr:
                    error_msg = result.stderr or result.stdout
                    if 'not found' in error_msg.lower() or 'is not recognized' in error_msg.lower():
                        tool = 'pg_restore' if is_compressed else 'psql'
                        return {
                            'success': False,
                            'message': f'{tool}命令不存在，请安装PostgreSQL客户端工具'
                        }
                    return {'success': False, 'message': f'数据库恢复失败: {error_msg}'}
                
                return {
                    'success': True,
                    'message': 'PostgreSQL数据库恢复成功',
                    'backup_used': backup_filename,
                    'db_type': 'postgresql',
                    'auto_backup_created': auto_backup
                }
                
            except subprocess.TimeoutExpired:
                return {'success': False, 'message': '恢复超时（超过10分钟），请检查备份文件和数据库连接'}
            except FileNotFoundError as e:
                return {'success': False, 'message': f'PostgreSQL工具未找到: {str(e)}'}
        
        else:
            return {'success': False, 'message': f'不支持的数据库类型'}
            
    except Exception as e:
        import traceback
        return {'success': False, 'message': f'恢复失败: {str(e)}', 'trace': traceback.format_exc()}


def reset_database():
    """重置数据库（删除所有表并重新创建）
    
    保留的系统基础数据：
    1. 管理员账户 (admin/admin123，超级管理员不属于任何部门)
    2. 默认部门 (信息部、财务部、人力行政部、国内销售中心、生产办、企管部)
    3. 设备类型 (15种常用设备类型)
    4. 配件类型 (20种常用配件类型)
    5. 审批流程模板 (6种标准审批流程)
    """
    try:
        from flask import has_app_context
        if not has_app_context():
            return {'success': False, 'message': '需要在应用上下文中执行'}
        from app import db
        
        # 删除所有表
        db.drop_all()
        
        # 重新创建所有表
        db.create_all()
        
        # 使用新的系统数据初始化脚本
        from init_system_data import (
            init_departments, init_admin_user, init_equipment_types,
            init_spare_part_types, init_workflow_templates
        )
        
        # 依次初始化基础数据
        init_departments()
        db.session.commit()
        
        admin = init_admin_user()
        db.session.commit()
        
        init_equipment_types()
        db.session.commit()
        
        init_spare_part_types()
        db.session.commit()
        
        init_workflow_templates(admin.id)
        db.session.commit()
        
        return {
            'success': True,
            'message': '数据库重置成功，已重新初始化系统基础数据',
            'details': {
                'admin_username': 'admin',
                'admin_password': 'admin123',
                'admin_note': '超级管理员，不属于任何部门',
                'departments': '6个默认部门',
                'equipment_types': '15种设备类型',
                'spare_part_types': '20种配件类型',
                'workflow_templates': '6个审批流程模板'
            }
        }
    except Exception as e:
        import traceback
        return {'success': False, 'message': f'重置失败: {str(e)}', 'trace': traceback.format_exc()}


def list_backups(filter_date=None, db_type=None):
    """列出所有备份文件
    
    Args:
        filter_date: 筛选日期，可选值：'today', 'yesterday', 'week', 'month', 'all' 或 None（默认全部）
        db_type: 数据库类型筛选，'sqlite', 'postgresql' 或 None（默认全部）
    """
    try:
        backup_dir = get_backup_dir()
        
        if not os.path.exists(backup_dir):
            return {'success': True, 'backups': [], 'total': 0}
        
        backups = []
        # use Asia/Shanghai aware now when possible
        try:
            if ZoneInfo:
                now = datetime.now(ZoneInfo('Asia/Shanghai'))
            elif pytz:
                now = datetime.now(pytz.timezone('Asia/Shanghai'))
            else:
                now = datetime.utcnow() + timedelta(hours=8)
        except Exception:
            now = datetime.utcnow()
        
        for filename in os.listdir(backup_dir):
            # 支持SQLite (.db) 和 PostgreSQL (.sql, .sql.gz) 备份
            file_db_type = None
            is_compressed = False
            
            if filename.startswith('app_backup_') and filename.endswith('.db'):
                file_db_type = 'sqlite'
                timestamp_str = filename.replace('app_backup_', '').replace('.db', '')
            elif (filename.startswith('postgresql_backup_') or filename.startswith('python_postgresql_backup_')) and (filename.endswith('.sql') or filename.endswith('.sql.gz')):
                file_db_type = 'postgresql'
                is_compressed = filename.endswith('.gz')
                if filename.startswith('python_postgresql_backup_'):
                    if is_compressed:
                        timestamp_str = filename.replace('python_postgresql_backup_', '').replace('.sql.gz', '')
                    else:
                        timestamp_str = filename.replace('python_postgresql_backup_', '').replace('.sql', '')
                else:
                    if is_compressed:
                        timestamp_str = filename.replace('postgresql_backup_', '').replace('.sql.gz', '')
                    else:
                        timestamp_str = filename.replace('postgresql_backup_', '').replace('.sql', '')
            else:
                continue  # 跳过不识别的文件
            
            # 数据库类型筛选
            if db_type and file_db_type != db_type:
                continue
            
            if True:  # Maintain structure for replacement
                filepath = os.path.join(backup_dir, filename)
                file_stat = os.stat(filepath)
                # 将文件时间转换为北京时间显示，兼容无 pytz 情况
                try:
                    mtime = file_stat.st_mtime
                    # interpret mtime as UTC then convert to Asia/Shanghai when possible
                    if ZoneInfo:
                        created_dt = datetime.fromtimestamp(mtime, timezone.utc).astimezone(ZoneInfo('Asia/Shanghai'))
                    elif pytz:
                        created_dt = datetime.fromtimestamp(mtime, pytz.utc).astimezone(pytz.timezone('Asia/Shanghai'))
                    else:
                        created_dt = datetime.utcfromtimestamp(mtime) + timedelta(hours=8)
                except Exception:
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
                
                # 格式化友好时间显示 (注意 created_dt 可能是 timezone-aware or naive)
                # Make created_dt timezone-aware in the same tz as now when possible
                try:
                    if created_dt.tzinfo is None:
                        if ZoneInfo:
                            created_dt = created_dt.replace(tzinfo=ZoneInfo('Asia/Shanghai'))
                        elif pytz:
                            created_dt = pytz.timezone('Asia/Shanghai').localize(created_dt)
                except Exception:
                    pass

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
                
                # 计算压缩比（仅对压缩文件）
                compression_ratio = None
                if is_compressed:
                    # 估算压缩比：对于PostgreSQL，通常压缩比为5-10倍
                    compression_ratio = 'N/A'  # 实际需要解压才能计算
                
                backups.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'created': created_dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'friendly_time': friendly_time,
                    'timestamp': file_stat.st_mtime,
                    'timestamp_str': timestamp_str,
                    'date': created_dt.date().isoformat(),
                    'db_type': file_db_type,
                    'compressed': is_compressed,
                    'compression_ratio': compression_ratio,
                    'file_extension': '.sql.gz' if is_compressed else ('.sql' if file_db_type == 'postgresql' else '.db')
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
        
        # 验证文件名（支持SQLite和PostgreSQL）
        is_valid = (
            (backup_filename.startswith('app_backup_') and backup_filename.endswith('.db')) or
            (backup_filename.startswith('postgresql_backup_') and 
             (backup_filename.endswith('.sql') or backup_filename.endswith('.sql.gz')))
        )
        
        if not is_valid:
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
        
        # 判断数据库类型
        if db_uri.startswith('sqlite:///'):
            db_type = 'SQLite'
        elif db_uri.startswith('postgresql://'):
            db_type = 'PostgreSQL'
        elif db_uri.startswith('mysql://'):
            db_type = 'MySQL'
        else:
            db_type = 'Unknown'
        
        info = {
            'type': db_type,
            'uri': db_uri.split('@')[-1] if '@' in db_uri else db_uri.replace('sqlite:///', '')
        }
        
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            if os.path.exists(db_path):
                info['exists'] = True
                info['size'] = os.path.getsize(db_path)
                # format mtime in Asia/Shanghai
                try:
                    mtime = os.path.getmtime(db_path)
                    if ZoneInfo:
                        modified_dt = datetime.fromtimestamp(mtime, timezone.utc).astimezone(ZoneInfo('Asia/Shanghai'))
                    elif pytz:
                        modified_dt = datetime.fromtimestamp(mtime, pytz.utc).astimezone(pytz.timezone('Asia/Shanghai'))
                    else:
                        modified_dt = datetime.utcfromtimestamp(mtime) + timedelta(hours=8)
                    info['modified'] = modified_dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    info['modified'] = datetime.fromtimestamp(os.path.getmtime(db_path)).strftime('%Y-%m-%d %H:%M:%S')
            else:
                info['exists'] = False
        elif db_uri.startswith('postgresql://') or db_uri.startswith('mysql://'):
            # PostgreSQL/MySQL 数据库不是文件，从数据库获取信息
            info['exists'] = True
            try:
                from sqlalchemy import text
                engine = db.engine
                with engine.connect() as conn:
                    if db_uri.startswith('postgresql://'):
                        # 获取PostgreSQL数据库大小
                        result = conn.execute(text("SELECT pg_database_size(current_database())"))
                        info['size'] = result.scalar()
                    else:
                        # MySQL 暂不支持获取大小
                        info['size'] = None
            except Exception:
                info['size'] = None
            info['modified'] = 'N/A'
        else:
            info['exists'] = False
        
        # 获取表信息
        try:
            engine = db.engine
            insp = inspect(engine)
            info['tables'] = insp.get_table_names()
            info['table_count'] = len(info['tables'])
        except Exception:
            info['tables'] = []
            info['table_count'] = 0
        
        return {'success': True, 'info': info}
    except Exception as e:
        return {'success': False, 'message': f'获取数据库信息失败: {str(e)}'}

def export_database_to_mysql(sqlite_path, out_dir=None, src_tz='UTC', dst_tz='Asia/Shanghai'):
    """调用脚本将 SQLite 导出为 MySQL 兼容 SQL 文件，返回生成的文件名。"""
    try:
        if out_dir is None:
            out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'migrations')
        os.makedirs(out_dir, exist_ok=True)
        # 生成输出文件名
        try:
            if pytz:
                now = datetime.now(pytz.timezone('Asia/Shanghai'))
            else:
                from datetime import timedelta
                now = datetime.utcnow() + timedelta(hours=8)
        except Exception:
            now = datetime.utcnow()
        out_name = f'app_db_mysql_dump_{now.strftime("%Y%m%d_%H%M%S")}.sql'
        out_path = os.path.join(out_dir, out_name)

        PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        script = os.path.join(PROJECT_ROOT, 'scripts', 'sqlite_to_mysql.py')
        cmd = [sys.executable, script, '--sqlite', sqlite_path, '--out', out_path, '--src-tz', src_tz, '--dst-tz', dst_tz]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            return {'success': False, 'message': proc.stderr}
        return {'success': True, 'dump_path': out_path, 'dump_filename': out_name}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def export_database_to_mssql(sqlite_path, out_dir=None, src_tz='UTC', dst_tz='Asia/Shanghai'):
    """调用脚本将 SQLite 导出为 SQL Server 兼容 SQL 文件，返回生成的文件名。"""
    try:
        if out_dir is None:
            out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'migrations')
        os.makedirs(out_dir, exist_ok=True)
        try:
            if pytz:
                now = datetime.now(pytz.timezone('Asia/Shanghai'))
            else:
                from datetime import timedelta
                now = datetime.utcnow() + timedelta(hours=8)
        except Exception:
            now = datetime.utcnow()
        out_name = f'app_db_mssql_dump_{now.strftime("%Y%m%d_%H%M%S")}.sql'
        out_path = os.path.join(out_dir, out_name)

        PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        script = os.path.join(PROJECT_ROOT, 'scripts', 'sqlite_to_mssql.py')
        cmd = [sys.executable, script, '--sqlite', sqlite_path, '--out', out_path, '--src-tz', src_tz, '--dst-tz', dst_tz]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            return {'success': False, 'message': proc.stderr}
        return {'success': True, 'dump_path': out_path, 'dump_filename': out_name}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def export_database_to_postgresql(sqlite_path, out_dir=None, src_tz='UTC', dst_tz='Asia/Shanghai'):
    """调用脚本将 SQLite 导出为 PostgreSQL 兼容 SQL 文件，返回生成的文件名。"""
    try:
        if out_dir is None:
            out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'migrations')
        os.makedirs(out_dir, exist_ok=True)
        try:
            if pytz:
                now = datetime.now(pytz.timezone('Asia/Shanghai'))
            else:
                from datetime import timedelta
                now = datetime.utcnow() + timedelta(hours=8)
        except Exception:
            now = datetime.utcnow()
        out_name = f'app_db_postgresql_dump_{now.strftime("%Y%m%d_%H%M%S")}.sql'
        out_path = os.path.join(out_dir, out_name)

        PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        script = os.path.join(PROJECT_ROOT, 'scripts', 'sqlite_to_postgresql.py')
        cmd = [sys.executable, script, '--sqlite', sqlite_path, '--out', out_path, '--src-tz', src_tz, '--dst-tz', dst_tz]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            return {'success': False, 'message': proc.stderr}
        return {'success': True, 'dump_path': out_path, 'dump_filename': out_name}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def validate_database_file(file_path):
    """验证数据库文件是否有效"""
    try:
        if not os.path.exists(file_path):
            return {'success': False, 'message': '文件不存在'}
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return {'success': False, 'message': '文件为空'}
        
        file_ext = os.path.splitext(file_path.lower())[1]
        
        # SQLite 数据库验证
        if file_ext == '.db':
            import sqlite3
            try:
                conn = sqlite3.connect(file_path)
                cursor = conn.cursor()
                
                # 检查是否是有效的SQLite数据库
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                table_count = len(tables)
                
                conn.close()
                
                return {
                    'success': True,
                    'message': 'SQLite数据库文件有效',
                    'file_size': file_size,
                    'table_count': table_count,
                    'tables': [t[0] for t in tables],
                    'db_type': 'sqlite'
                }
            except Exception as e:
                return {'success': False, 'message': f'不是有效的SQLite数据库: {str(e)}'}
        
        # PostgreSQL SQL 文件验证
        elif file_ext == '.sql' or file_path.lower().endswith('.sql.gz'):
            is_compressed = file_path.lower().endswith('.gz')
            
            # 读取文件头部内容
            try:
                if is_compressed:
                    with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
                        header = f.read(1000)  # 读取前1000字符
                else:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        header = f.read(1000)
                
                # 检查是否包含SQL关键字
                sql_keywords = ['CREATE', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'TABLE', 'DATABASE', 'SELECT']
                has_sql = any(keyword in header.upper() for keyword in sql_keywords)
                
                if not has_sql:
                    return {'success': False, 'message': '文件不包含有效的SQL语句'}
                
                # 尝试提取数据库名称（如果有）
                db_name = None
                db_match = re.search(r'CREATE DATABASE\s+([\w_]+)', header, re.IGNORECASE)
                if db_match:
                    db_name = db_match.group(1)
                
                # 尝试统计表数量
                table_count = len(re.findall(r'CREATE TABLE', header, re.IGNORECASE))
                
                return {
                    'success': True,
                    'message': 'PostgreSQL SQL文件有效',
                    'file_size': file_size,
                    'compressed': is_compressed,
                    'db_name': db_name,
                    'table_count_estimate': table_count,
                    'db_type': 'postgresql'
                }
            except Exception as e:
                return {'success': False, 'message': f'SQL文件读取失败: {str(e)}'}
        
        else:
            return {'success': False, 'message': f'不支持的文件类型: {file_ext}'}
            
    except Exception as e:
        return {'success': False, 'message': f'验证失败: {str(e)}'}


def get_table_chinese_name(table_name):
    """获取数据表的中文名称"""
    table_names = {
        'app_user': '用户表',
        'user': '用户表(旧)',  # 兼容旧表名
        'department': '部门表',
        'equipment': '设备表',
        'spare_part': '备件表',
        'spare_part_type': '备件类型表',
        'equipment_type': '设备类型表',
        'repair_order': '维修工单表',
        'part_request_order': '配件申请表',
        'part_replacement': '配件更换表',
        'equipment_transfer': '设备调拨表',
        'equipment_scrap': '设备报废表',
        'equipment_loan': '设备借用表',
        'equipment_application': '设备申领表',
        'notification': '通知表',
        'user_activity_log': '用户操作日志表',
        'approval_workflow': '审批流程表',
        'approval_decision': '审批决策表',
        'workflow_node': '工作流节点表',
        'workflow_template': '工作流模板表',
        'workflow_step': '工作流步骤表',
        'workflow_instance': '工作流实例表',
        'approval_instance': '审批实例表',
        'approval_step': '审批步骤表',
        'approval_log': '审批日志表',
        'approval_reminder': '审批提醒表',
        'approval_delegate': '审批委托表',
        'account_request': '账号申请表',
        'asset_cost': '资产成本表',
        'asset_lifecycle': '资产生命周期表',
        'asset_handover': '资产交接表',
        'inventory_warning': '库存预警表',
        'permission': '权限表',
        'role_definition': '角色定义表',
        'user_custom_role': '用户自定义角色表',
        'user_approval_role': '用户审批角色表',
        'approval_role': '审批角色表',
        'action_log': '操作日志表',
        'audit_log': '审计日志表',
        'announcement': '系统公告表',
        'announcements': '系统公告表',
        'alembic_version': '数据库版本表',
    }
    return table_names.get(table_name, table_name)


def get_database_tables_info():
    """获取数据库中所有表的详细信息(表名和记录数)"""
    try:
        from flask import has_app_context, current_app
        if not has_app_context():
            return {'success': False, 'message': '需要在应用上下文中执行'}
        from app import db
        from sqlalchemy import inspect, text
        
        engine = db.engine
        insp = inspect(engine)
        tables = insp.get_table_names()
        
        tables_info = []
        total_records = 0
        
        with engine.connect() as conn:
            for table_name in tables:
                try:
                    # 获取记录数
                    result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
                    count = result.scalar()
                    total_records += count
                    
                    # 获取列信息
                    columns = insp.get_columns(table_name)
                    column_count = len(columns)
                    
                    tables_info.append({
                        'name': table_name,
                        'chinese_name': get_table_chinese_name(table_name),
                        'record_count': count,
                        'column_count': column_count,
                        'columns': [col['name'] for col in columns]
                    })
                except Exception as e:
                    tables_info.append({
                        'name': table_name,
                        'chinese_name': get_table_chinese_name(table_name),
                        'record_count': 0,
                        'column_count': 0,
                        'columns': [],
                        'error': str(e)
                    })
        
        # 按记录数排序
        tables_info.sort(key=lambda x: x['record_count'], reverse=True)
        
        return {
            'success': True,
            'tables': tables_info,
            'table_count': len(tables_info),
            'total_records': total_records
        }
    except Exception as e:
        return {'success': False, 'message': f'获取表信息失败: {str(e)}'}


def get_table_data(table_name, page=1, per_page=50):
    """获取指定表的数据(分页)"""
    try:
        from flask import has_app_context, current_app
        if not has_app_context():
            return {'success': False, 'message': '需要在应用上下文中执行'}
        from app import db
        from sqlalchemy import inspect, text
        
        engine = db.engine
        insp = inspect(engine)
        
        # 检查表是否存在
        tables = insp.get_table_names()
        if table_name not in tables:
            return {'success': False, 'message': f'表 {table_name} 不存在'}
        
        # 获取列信息
        columns = insp.get_columns(table_name)
        column_names = [col['name'] for col in columns]
        
        with engine.connect() as conn:
            # 获取总记录数
            result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
            total_count = result.scalar()
            
            # 分页查询数据
            offset = (page - 1) * per_page
            result = conn.execute(text(f'SELECT * FROM "{table_name}" LIMIT {per_page} OFFSET {offset}'))
            rows = result.fetchall()
            
            # 转换为字典列表
            data = []
            for row in rows:
                row_dict = {}
                for i, col_name in enumerate(column_names):
                    value = row[i]
                    # 处理None值和长文本
                    if value is None:
                        row_dict[col_name] = None
                    elif isinstance(value, str) and len(value) > 100:
                        row_dict[col_name] = value[:100] + '...'
                    else:
                        row_dict[col_name] = value
                data.append(row_dict)
            
            total_pages = (total_count + per_page - 1) // per_page
            
            return {
                'success': True,
                'table_name': table_name,
                'columns': column_names,
                'column_info': columns,
                'data': data,
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
    except Exception as e:
        return {'success': False, 'message': f'获取表数据失败: {str(e)}'}


def _python_postgresql_backup(db_uri, backup_dir, timestamp, compress=True):
    """
    纯 Python 实现的 PostgreSQL 备份（不依赖 pg_dump）
    当 pg_dump 不可用时作为后备方案
    
    注意: 此方案仅备份数据和表结构，不包含索引、约束、序列等
    """
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # 解析数据库连接
        parsed = urlparse(db_uri)
        conn_params = {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 5432,
            'user': parsed.username or 'postgres',
            'password': parsed.password,
            'database': parsed.path.lstrip('/')
        }
        
        # 连接数据库
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # 生成备份文件名
        if compress:
            backup_filename = f'python_postgresql_backup_{timestamp}.sql.gz'
            backup_path = os.path.join(backup_dir, backup_filename)
            output_file = gzip.open(backup_path, 'wt', encoding='utf-8')
        else:
            backup_filename = f'python_postgresql_backup_{timestamp}.sql'
            backup_path = os.path.join(backup_dir, backup_filename)
            output_file = open(backup_path, 'w', encoding='utf-8')
        
        try:
            # 写入备份头部
            output_file.write(f"-- PostgreSQL 数据库备份 (Python方式)\n")
            output_file.write(f"-- 时间: {timestamp}\n")
            output_file.write(f"-- 数据库: {conn_params['database']}\n")
            output_file.write(f"-- 警告: 此备份不包含索引、约束、序列等对象\n\n")
            
            # 获取所有用户表
            cursor.execute("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' 
                ORDER BY tablename
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            table_count = 0
            # 备份每个表
            for table in tables:
                table_count += 1
                
                # 获取表结构
                cursor.execute(f"""
                    SELECT column_name, data_type, character_maximum_length, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = %s
                    ORDER BY ordinal_position
                """, (table,))
                columns = cursor.fetchall()
                
                # 生成 CREATE TABLE 语句
                output_file.write(f"-- 表: {table}\n")
                output_file.write(f"DROP TABLE IF EXISTS {table} CASCADE;\n")
                output_file.write(f"CREATE TABLE {table} (\n")
                
                column_defs = []
                for col in columns:
                    col_name, data_type, max_length, is_nullable = col
                    col_def = f"    {col_name} {data_type}"
                    if max_length:
                        col_def += f"({max_length})"
                    if is_nullable == 'NO':
                        col_def += " NOT NULL"
                    column_defs.append(col_def)
                
                output_file.write(",\n".join(column_defs))
                output_file.write("\n);\n\n")
                
                # 导出数据
                cursor.execute(f'SELECT * FROM "{table}"')
                rows = cursor.fetchall()
                
                if rows:
                    col_names = [desc[0] for desc in cursor.description]
                    output_file.write(f"-- 数据: {table} ({len(rows)} 行)\n")
                    
                    for row in rows:
                        values = []
                        for val in row:
                            if val is None:
                                values.append('NULL')
                            elif isinstance(val, str):
                                # 转义单引号
                                escaped = val.replace("'", "''")
                                values.append(f"'{escaped}'")
                            elif isinstance(val, (int, float, bool)):
                                values.append(str(val))
                            else:
                                # 其他类型转字符串
                                escaped = str(val).replace("'", "''")
                                values.append(f"'{escaped}'")
                        
                        insert_sql = f"INSERT INTO {table} ({','.join(col_names)}) VALUES ({','.join(values)});\n"
                        output_file.write(insert_sql)
                    
                    output_file.write("\n")
            
            output_file.write(f"\n-- 备份完成！共备份 {table_count} 个表\n")
            
        finally:
            output_file.close()
            cursor.close()
            conn.close()
        
        # 获取文件大小
        file_size = os.path.getsize(backup_path)
        
        return {
            'success': True,
            'message': f'PostgreSQL备份成功（Python方式，{table_count}个表）',
            'backup_path': backup_path,
            'backup_filename': backup_filename,
            'file_size': file_size,
            'timestamp': timestamp,
            'db_type': 'postgresql',
            'compressed': compress,
            'table_count': table_count,
            'method': 'python'
        }
        
    except ImportError:
        return {
            'success': False,
            'message': 'psycopg2 模块未安装，无法使用Python备份'
        }
    except Exception as e:
        import traceback
        return {
            'success': False,
            'message': f'Python备份失败: {str(e)}',
            'trace': traceback.format_exc()
        }


def initialize_system():
    """
    系统初始化 - 清除所有用户数据，保留系统基础配置
    
    保留的内容:
    - 角色定义
    - 权限定义
    - 设备类型 (计算机、打印机等)
    - 配件类型 (内存、硬盘等)
    - 基础部门
    - 审批流程配置
    
    删除的内容:
    - 所有员工账号 (除admin外)
    - 所有设备记录
    - 所有转移/维修/报废记录
    - 所有借用和申请记录
    - 所有操作日志
    """
    try:
        from flask import has_app_context, current_app
        if not has_app_context():
            return {'success': False, 'message': '需要在应用上下文中执行'}
        
        from app import db
        from app.models import (
            User, RoleDefinition, EquipmentType, SparePartType,
            Department, ApprovalWorkflow,
            Equipment, EquipmentTransfer, EquipmentScrap, EquipmentLoan,
            EquipmentApplication, PartRequestOrder, AccountRequest,
            AuditLog, UserActivityLog, Notification
        )
        
        # 第一步：备份数据库
        backup_result = backup_database(compress=True)
        if not backup_result.get('success'):
            return {
                'success': False,
                'message': f'初始化前备份失败，已取消: {backup_result.get("message")}'
            }
        
        # 第二步：清除用户数据
        clear_stats = {
            'part_replacements': 0,
            'repair_orders': 0,
            'maintenance_records': 0,
            'maintenance_plans': 0,
            'asset_costs': 0,
            'asset_lifecycles': 0,
            'inventory_warnings': 0,
            'spare_parts': 0,
            'spare_part_types': 0,
            'asset_handovers': 0,
            'equipment': 0,
            'transfers': 0,
            'scraps': 0,
            'loans': 0,
            'applications': 0,
            'part_requests': 0,
            'account_requests': 0,
            'audit_logs': 0,
            'notifications': 0,
            'user_activity_logs': 0,
            'users': 0
        }
        
        try:
            from sqlalchemy import text
            # 先清除依赖于设备的子表，避免外键冲突
            from app.models import (
                RepairOrder, PartReplacement, SparePart, SparePartType,
                InventoryWarning, AssetCost, AssetLifecycle,
                MaintenancePlan, MaintenanceRecord, AssetHandover,
                ApprovalWorkflow
            )

            if db.engine.name == 'postgresql':
                # 在 PostgreSQL 中使用 TRUNCATE ... CASCADE 一次性清空，避免外键问题
                candidate_tables = [
                    'part_replacement', 'repair_order', 'maintenance_record', 'maintenance_plan',
                    'asset_cost', 'asset_lifecycle', 'inventory_warning', 'spare_part', 'spare_part_type',
                    'asset_handover', 'approval_workflow',
                    'equipment_transfer', 'equipment_scrap', 'equipment_loan', 'equipment_application',
                    'part_request_order', 'account_request', 'audit_log', 'notification', 'user_activity_log',
                    'equipment'
                ]

                inspector = db.inspect(db.engine)
                existing_tables = set(inspector.get_table_names())
                table_order = [t for t in candidate_tables if t in existing_tables]

                # 记录清理前数量
                for tbl in table_order:
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
                    key = {
                        'part_replacement': 'part_replacements',
                        'repair_order': 'repair_orders',
                        'maintenance_record': 'maintenance_records',
                        'maintenance_plan': 'maintenance_plans',
                        'asset_cost': 'asset_costs',
                        'asset_lifecycle': 'asset_lifecycles',
                        'inventory_warning': 'inventory_warnings',
                        'spare_part': 'spare_parts',
                        'spare_part_type': 'spare_part_types',
                        'asset_handover': 'asset_handovers',
                        'approval_workflow': 'approval_workflows',
                        'equipment_transfer': 'transfers',
                        'equipment_scrap': 'scraps',
                        'equipment_loan': 'loans',
                        'equipment_application': 'applications',
                        'part_request_order': 'part_requests',
                        'account_request': 'account_requests',
                        'audit_log': 'audit_logs',
                        'notification': 'notifications',
                        'user_activity_log': 'user_activity_logs',
                        'equipment': 'equipment'
                    }.get(tbl, tbl)
                    clear_stats[key] = result or 0

                if table_order:
                    db.session.execute(text('TRUNCATE TABLE ' + ', '.join(table_order) + ' CASCADE'))
            else:
                # ORM 删除（用于非 PostgreSQL）
                clear_stats['part_replacements'] = db.session.query(PartReplacement).delete()
                clear_stats['repair_orders'] = db.session.query(RepairOrder).delete()
                clear_stats['approval_workflows'] = db.session.query(ApprovalWorkflow).delete()
                clear_stats['maintenance_records'] = db.session.query(MaintenanceRecord).delete()
                clear_stats['maintenance_plans'] = db.session.query(MaintenancePlan).delete()
                clear_stats['asset_costs'] = db.session.query(AssetCost).delete()
                clear_stats['asset_lifecycles'] = db.session.query(AssetLifecycle).delete()
                clear_stats['inventory_warnings'] = db.session.query(InventoryWarning).delete()
                clear_stats['spare_parts'] = db.session.query(SparePart).delete()
                clear_stats['spare_part_types'] = db.session.query(SparePartType).delete()
                clear_stats['asset_handovers'] = db.session.query(AssetHandover).delete()

                clear_stats['transfers'] = db.session.query(EquipmentTransfer).delete()
                clear_stats['scraps'] = db.session.query(EquipmentScrap).delete()
                clear_stats['loans'] = db.session.query(EquipmentLoan).delete()
                clear_stats['applications'] = db.session.query(EquipmentApplication).delete()
                clear_stats['part_requests'] = db.session.query(PartRequestOrder).delete()
                clear_stats['account_requests'] = db.session.query(AccountRequest).delete()
                clear_stats['audit_logs'] = db.session.query(AuditLog).delete()
                clear_stats['notifications'] = db.session.query(Notification).delete()
                clear_stats['user_activity_logs'] = db.session.query(UserActivityLog).delete()

                # 最后清除设备（顶层表）
                clear_stats['equipment'] = db.session.query(Equipment).delete()
            
            # 清除除admin外的所有用户
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                clear_stats['users'] = User.query.filter(
                    User.id != admin_user.id
                ).delete()
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'清除数据失败: {str(e)}'
            }
        
        # 第三步：确保管理员账号存在并重置密码
        try:
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@company.com',
                    full_name='系统管理员',
                    is_active=True
                )
                admin_user.set_password('admin@123')
                db.session.add(admin_user)
            else:
                # 重置admin密码
                admin_user.set_password('admin@123')
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '系统初始化成功！',
                'admin_username': 'admin',
                'admin_password': 'admin@123',
                'backup_file': backup_result.get('backup_filename'),
                'users_cleared': clear_stats['users'],
                'equipment_cleared': clear_stats['equipment'],
                'transfers_cleared': clear_stats['transfers'],
                'loans_cleared': clear_stats['loans'],
                'applications_cleared': clear_stats['applications'],
                'part_requests_cleared': clear_stats['part_requests'],
                'account_requests_cleared': clear_stats['account_requests']
            }
        
        except Exception as e:
            db.session.rollback()
            import traceback
            return {
                'success': False,
                'message': f'初始化失败: {str(e)}',
                'trace': traceback.format_exc()
            }
        
    except Exception as e:
        import traceback
        return {
            'success': False,
            'message': f'系统初始化异常: {str(e)}',
            'trace': traceback.format_exc()
        }
