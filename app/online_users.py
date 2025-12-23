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
    """
    try:
        if not redis_client:
            return jsonify({'online_users': []}), 200
        online_user_ids = redis_client.smembers('online_users')
        # 返回 Python 原生的 list，确保 JSON 序列化
        return jsonify({'online_users': list(online_user_ids)}), 200
    except Exception as e:
        # 日志已由调用方处理，这里返回空列表以便前端继续工作
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