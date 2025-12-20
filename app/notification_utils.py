"""
通知工具函数
整合数据库通知和实时WebSocket推送
"""
from app import db
from app.models import Notification, User
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


def create_notification(user_id, title, message, order_type=None, order_id=None, notification_type='info', link=None):
    """
    创建通知并实时推送
    
    Args:
        user_id: 用户ID
        title: 通知标题
        message: 通知内容
        order_type: 工单类型(可选)
        order_id: 工单ID(可选)
        notification_type: 通知类型 info/success/warning/error
        link: 跳转链接(可选)
    
    Returns:
        Notification对象
    """
    # 创建数据库通知
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        order_type=order_type,
        order_id=order_id
    )
    db.session.add(notification)
    
    try:
        # 尝试实时推送
        from app.socketio_handler import send_notification_to_user
        
        notification_data = {
            'title': title,
            'message': message,
            'type': notification_type,
            'link': link,
            'data': {
                'order_type': order_type,
                'order_id': order_id
            } if order_type and order_id else None
        }
        
        send_notification_to_user(user_id, notification_data)
        logger.info(f"✓ 实时通知已发送: {title} -> 用户{user_id}")
        
    except Exception as e:
        logger.warning(f"⚠ 实时通知推送失败,仅保存数据库记录: {e}")
    
    return notification


def create_notification_batch(user_ids, title, message, order_type=None, order_id=None, notification_type='info'):
    """
    批量创建通知
    
    Args:
        user_ids: 用户ID列表
        title: 通知标题
        message: 通知内容
        order_type: 工单类型(可选)
        order_id: 工单ID(可选)
        notification_type: 通知类型
    
    Returns:
        创建的通知数量
    """
    count = 0
    for user_id in user_ids:
        create_notification(
            user_id=user_id,
            title=title,
            message=message,
            order_type=order_type,
            order_id=order_id,
            notification_type=notification_type
        )
        count += 1
    
    return count


def notify_approval_needed(approver_id, order_type, order_id, order_description, node_name):
    """
    通知审批人有新的待审批工单
    
    Args:
        approver_id: 审批人ID
        order_type: 工单类型
        order_id: 工单ID
        order_description: 工单描述
        node_name: 审批节点名称
    """
    title = f'待审批: {order_description}'
    message = f'工单 #{order_id} 需要您审批 ({node_name})'
    link = f'/approvals'
    
    create_notification(
        user_id=approver_id,
        title=title,
        message=message,
        order_type=order_type,
        order_id=order_id,
        notification_type='warning',
        link=link
    )


def notify_approval_progress(requester_id, order_type, order_id, approver_name, next_node_name):
    """
    通知申请人审批进度
    
    Args:
        requester_id: 申请人ID
        order_type: 工单类型
        order_id: 工单ID
        approver_name: 审批人姓名
        next_node_name: 下一节点名称
    """
    title = '审批状态更新'
    message = f'您的工单 #{order_id} 已被 {approver_name} 批准，进入下一审批节点: {next_node_name}'
    link = f'/{order_type}/{order_id}'
    
    create_notification(
        user_id=requester_id,
        title=title,
        message=message,
        order_type=order_type,
        order_id=order_id,
        notification_type='info',
        link=link
    )


def notify_approval_completed(requester_id, order_type, order_id, order_description):
    """
    通知申请人审批完成
    
    Args:
        requester_id: 申请人ID
        order_type: 工单类型
        order_id: 工单ID
        order_description: 工单描述
    """
    title = '审批完成'
    message = f'您的{order_description} #{order_id} 已通过所有审批'
    link = f'/{order_type}/{order_id}'
    
    create_notification(
        user_id=requester_id,
        title=title,
        message=message,
        order_type=order_type,
        order_id=order_id,
        notification_type='success',
        link=link
    )


def notify_approval_rejected(requester_id, order_type, order_id, approver_name, reason=''):
    """
    通知申请人审批被拒绝
    
    Args:
        requester_id: 申请人ID
        order_type: 工单类型
        order_id: 工单ID
        approver_name: 审批人姓名
        reason: 拒绝原因(可选)
    """
    title = '审批被拒绝'
    message = f'您的工单 #{order_id} 已被 {approver_name} 拒绝'
    if reason:
        message += f'。原因: {reason}'
    link = f'/{order_type}/{order_id}'
    
    create_notification(
        user_id=requester_id,
        title=title,
        message=message,
        order_type=order_type,
        order_id=order_id,
        notification_type='error',
        link=link
    )
