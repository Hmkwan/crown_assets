"""企业微信管理路由(管理员)

此模块提供管理员管理企业微信集成的功能,包括:
1. 同步组织架构
2. 同步用户信息
3. 查看同步状态
4. 配置企业微信参数

仅管理员可访问
"""

from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.main import bp
from app.decorators import admin_required
from app.integrations import get_wework_client
from app import db
from app.models import User, Department, UserActivityLog
import logging

logger = logging.getLogger(__name__)


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


@bp.route('/admin/wework')
@login_required
@admin_required
def admin_wework():
    """企业微信管理首页
    
    显示:
    - 企业微信配置状态
    - 同步统计信息
    - 快捷操作按钮
    """
    from flask import current_app
    
    # 检查配置状态
    wework_config = {
        'enabled': current_app.config.get('WEWORK_ENABLED', False),
        'corp_id': current_app.config.get('WEWORK_CORP_ID', ''),
        'agent_id': current_app.config.get('WEWORK_AGENT_ID', ''),
        'secret_configured': bool(current_app.config.get('WEWORK_SECRET', ''))
    }
    
    # 统计信息
    stats = {
        'total_users': User.query.count(),
        'wework_bound_users': 0,  # TODO: 统计已绑定企业微信的用户
        'total_departments': Department.query.count(),
        'wework_synced_departments': 0  # TODO: 统计已同步的部门
    }
    
    # 记录访问
    _log_activity('访问企业微信管理', '查看企业微信配置页面')
    
    return render_template(
        'admin/wework/index.html',
        wework_config=wework_config,
        stats=stats
    )


@bp.route('/admin/wework/sync-departments', methods=['POST'])
@login_required
@admin_required
def sync_wework_departments():
    """同步企业微信组织架构
    
    将企业微信的部门结构同步到本地Department表
    """
    try:
        client = get_wework_client()
        result = client.sync_departments_to_local()
        
        if result['success']:
            # 记录日志
            _log_activity('同步企业微信部门',
                         f"新建{result['created']}个, 更新{result['updated']}个, 总计{result['total']}个部门")
            
            flash(
                f"组织架构同步成功! 新建{result['created']}个, "
                f"更新{result['updated']}个, 总计{result['total']}个部门",
                'success'
            )
        else:
            flash(f"同步失败: {result.get('message', '未知错误')}", 'error')
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f'同步组织架构失败: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/admin/wework/sync-users', methods=['POST'])
@login_required
@admin_required
def sync_wework_users():
    """同步企业微信用户
    
    将企业微信的用户信息同步到本地User表
    
    注意: 此操作不会创建新用户,只会更新已存在用户的信息
    """
    try:
        # 兼容性：请求 body 可能为空或不是 JSON，使用 silent=True 避免抛出 BadRequest
        data = request.get_json(silent=True)
        if data is None:
            raw = request.get_data(as_text=True)
            logger.debug(f'sync_wework_users raw body: {raw!r}')
            department_id = None
        else:
            department_id = data.get('department_id')
        
        client = get_wework_client()
        result = client.sync_users_to_local(department_id)
        
        if result['success']:
            # 记录日志
            _log_activity('同步企业微信用户',
                         f"新建{result['created']}个, 更新{result['updated']}个, 总计{result['total']}个用户")
            
            flash(
                f"用户信息同步成功! 新建{result['created']}个, "
                f"更新{result['updated']}个, 总计{result['total']}个用户",
                'success'
            )
        else:
            flash(f"同步失败: {result.get('message', '未知错误')}", 'error')
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f'同步用户失败: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/admin/wework/preview-departments')
@login_required
@admin_required
def preview_wework_departments():
    """预览企业微信部门结构
    
    获取企业微信的部门列表,但不写入数据库
    用于管理员预览和确认数据
    """
    try:
        client = get_wework_client()
        departments = client.get_department_list()
        
        # 记录日志
        _log_activity('预览企业微信部门', f'查看企业微信部门列表(共{len(departments)}个)')
        
        return jsonify({
            'success': True,
            'data': departments,
            'total': len(departments)
        })
        
    except Exception as e:
        logger.error(f'获取部门列表失败: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/admin/wework/preview-users')
@login_required
@admin_required
def preview_wework_users():
    """预览企业微信用户列表(通讯录)
    
    获取企业微信的所有用户,但不写入数据库
    """
    try:
        client = get_wework_client()
        users = client.get_all_users()
        
        # 记录日志
        _log_activity('预览企业微信用户', f'查看企业微信用户列表(共{len(users)}个)')
        
        return jsonify({
            'success': True,
            'data': users,
            'total': len(users)
        })
        
    except Exception as e:
        logger.error(f'获取用户列表失败: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/admin/wework/test-connection', methods=['POST'])
@login_required
@admin_required
def test_wework_connection():
    """测试企业微信连接
    
    验证企业微信配置是否正确
    """
    try:
        client = get_wework_client()
        
        # 尝试获取access_token
        token = client.get_access_token()
        
        if token and token != 'PLACEHOLDER_ACCESS_TOKEN':
            # 尝试获取部门列表验证
            departments = client.get_department_list()
            
            # 记录日志
            _log_activity('测试企业微信连接', '企业微信连接成功')
            
            return jsonify({
                'success': True,
                'message': '企业微信连接成功!',
                'department_count': len(departments)
            })
        else:
            return jsonify({
                'success': False,
                'message': '企业微信未正确配置,当前使用示例数据。请检查环境变量配置。'
            })
        
    except Exception as e:
        logger.error(f'测试连接失败: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'message': f'连接失败: {str(e)}'
        }), 500
