import os
from flask import Blueprint, jsonify
from flask_login import current_user
from app.utils.redis_utils import create_redis_client

online_users_bp = Blueprint('online_users', __name__)

# Redis连接（延迟初始化并包含重试）
redis_client = create_redis_client()  # 可能为 None，如果 Redis 不可用，接口会返回错误信息

@online_users_bp.route('/online_users', methods=['GET'])
def get_online_users():
    """获取在线用户列表

    如果 Redis 未启用或不可用，返回空列表以便前端能优雅降级（无需抛出 500）。
    返回结构: { 'online_users': [ { 'id': <int>, 'username': <str>, 'real_name': <str|None> }, ... ] }
    """
    try:
        if not redis_client:
            return jsonify({'online_users': []}), 200
        online_user_ids = redis_client.smembers('online_users') or set()
        # smembers 返回 bytes，解码为字符串并尝试转换为 int
        decoded_ids = []
        for uid in online_user_ids:
            try:
                if isinstance(uid, bytes):
                    uid = uid.decode('utf-8')
                decoded_ids.append(int(uid))
            except Exception:
                # 回退为原始字符串
                try:
                    decoded_ids.append(int(str(uid)))
                except Exception:
                    continue

        # 查询用户信息以返回可读字段
        from app.models import User
        users = User.query.filter(User.id.in_(decoded_ids)).all() if decoded_ids else []
        result = []
        for u in users:
            result.append({'id': u.id, 'username': u.username, 'real_name': getattr(u, 'real_name', None)})
        return jsonify({'online_users': result}), 200
    except Exception as e:
        # 遇到意外错误时记录并返回空列表
        import logging
        logger = logging.getLogger(__name__)
        logger.warning('获取在线用户失败: %s', e, exc_info=True)
        return jsonify({'online_users': []}), 200

@online_users_bp.route('/update_online_status', methods=['POST'])
def update_online_status():
    """更新用户在线状态"""
    try:
        user_id = current_user.id
        redis_client.sadd('online_users', user_id)
        return jsonify({'message': '在线状态已更新'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@online_users_bp.route('/remove_online_status', methods=['POST'])
def remove_online_status():
    """移除用户在线状态"""
    try:
        user_id = current_user.id
        redis_client.srem('online_users', user_id)
        return jsonify({'message': '在线状态已移除'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500