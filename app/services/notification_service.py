"""
通知服务
处理系统内的所有通知发送
"""
from app import db, get_beijing_now
from app.models import Notification, User
from datetime import datetime


class NotificationService:
    """统一的通知服务"""
    
    @staticmethod
    def send_notification(user_id, title, message, order_type=None, order_id=None):
        """
        发送通知给指定用户
        
        Args:
            user_id: 用户ID
            title: 通知标题
            message: 通知内容
            order_type: 工单类型（可选）
            order_id: 工单ID（可选）
        
        Returns:
            Notification对象
        """
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            order_type=order_type,
            order_id=order_id,
            created_date=get_beijing_now()
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # TODO: 后续可添加
        # - 邮件通知
        # - 微信推送
        # - WebSocket实时推送
        
        return notification
    
    @staticmethod
    def send_bulk_notification(user_ids, title, message, order_type=None, order_id=None):
        """
        批量发送通知
        
        Args:
            user_ids: 用户ID列表
            title: 通知标题
            message: 通知内容
            order_type: 工单类型（可选）
            order_id: 工单ID（可选）
        
        Returns:
            创建的通知数量
        """
        notifications = []
        for user_id in user_ids:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                order_type=order_type,
                order_id=order_id,
                created_date=get_beijing_now()
            )
            notifications.append(notification)
        
        db.session.bulk_save_objects(notifications)
        db.session.commit()
        
        return len(notifications)
    
    @staticmethod
    def notify_approval_pending(order_type, order_id, approver_ids, order_description=''):
        """
        通知审批人有新的待审批工单
        
        Args:
            order_type: 工单类型
            order_id: 工单ID
            approver_ids: 审批人ID列表
            order_description: 工单描述
        """
        order_type_display = {
            'repair_order': '维修工单',
            'part_request_order': '配件申请',
            'equipment_application': '设备申购',
            'equipment_scrap': '设备报废',
            'equipment_transfer': '设备调拨',
            'equipment_handover': '设备交接'
        }.get(order_type, '工单')
        
        title = f'新的{order_type_display}待审批'
        message = f'您有一个新的{order_type_display}需要审批'
        if order_description:
            message += f': {order_description}'
        
        return NotificationService.send_bulk_notification(
            user_ids=approver_ids,
            title=title,
            message=message,
            order_type=order_type,
            order_id=order_id
        )
    
    @staticmethod
    def notify_approval_result(order_type, order_id, requester_id, approved, approver_name, comments=''):
        """
        通知申请人审批结果
        
        Args:
            order_type: 工单类型
            order_id: 工单ID
            requester_id: 申请人ID
            approved: 是否批准
            approver_name: 审批人姓名
            comments: 审批意见
        """
        order_type_display = {
            'repair_order': '维修工单',
            'part_request_order': '配件申请',
            'equipment_application': '设备申购',
            'equipment_scrap': '设备报废',
            'equipment_transfer': '设备调拨',
            'equipment_handover': '设备交接'
        }.get(order_type, '工单')
        
        result = '已批准' if approved else '已拒绝'
        title = f'{order_type_display}{result}'
        message = f'您的{order_type_display}已被{approver_name}{result}'
        if comments:
            message += f'\n审批意见: {comments}'
        
        return NotificationService.send_notification(
            user_id=requester_id,
            title=title,
            message=message,
            order_type=order_type,
            order_id=order_id
        )
    
    @staticmethod
    def notify_order_status_change(order_type, order_id, user_id, old_status, new_status):
        """
        通知工单状态变更
        
        Args:
            order_type: 工单类型
            order_id: 工单ID
            user_id: 通知的用户ID
            old_status: 原状态
            new_status: 新状态
        """
        order_type_display = {
            'repair_order': '维修工单',
            'part_request_order': '配件申请',
            'equipment_application': '设备申购'
        }.get(order_type, '工单')
        
        status_display = {
            'pending': '待处理',
            'in_progress': '处理中',
            'completed': '已完成',
            'cancelled': '已取消',
            'rejected': '已拒绝',
            'approved': '已批准'
        }
        
        title = f'{order_type_display}状态更新'
        message = f'您的{order_type_display}状态已从"{status_display.get(old_status, old_status)}"变更为"{status_display.get(new_status, new_status)}"'
        
        return NotificationService.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            order_type=order_type,
            order_id=order_id
        )
    
    @staticmethod
    def notify_assignment(user_id, item_type, item_name):
        """
        通知用户被分配了资源（如设备）
        
        Args:
            user_id: 用户ID
            item_type: 资源类型（如'设备'）
            item_name: 资源名称
        """
        title = f'{item_type}分配通知'
        message = f'{item_type} "{item_name}" 已分配给您'
        
        return NotificationService.send_notification(
            user_id=user_id,
            title=title,
            message=message
        )
    
    @staticmethod
    def notify_role_by_workflow_role(workflow_role, title, message, order_type=None, order_id=None):
        """
        向具有特定审批流角色的所有用户发送通知
        
        Args:
            workflow_role: 审批流角色（如'finance', 'admin'）
            title: 通知标题
            message: 通知内容
            order_type: 工单类型（可选）
            order_id: 工单ID（可选）
        """
        # 查找所有拥有该角色的用户
        users = User.query.all()
        target_user_ids = [
            user.id for user in users 
            if user.has_workflow_role(workflow_role)
        ]
        
        if not target_user_ids:
            return 0
        
        return NotificationService.send_bulk_notification(
            user_ids=target_user_ids,
            title=title,
            message=message,
            order_type=order_type,
            order_id=order_id
        )
    
    @staticmethod
    def mark_as_read(notification_id, user_id):
        """
        标记通知为已读
        
        Args:
            notification_id: 通知ID
            user_id: 用户ID（用于验证权限）
        
        Returns:
            是否成功
        """
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        
        return False
    
    @staticmethod
    def mark_all_as_read(user_id):
        """
        标记用户所有通知为已读
        
        Args:
            user_id: 用户ID
        
        Returns:
            更新的通知数量
        """
        count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({'is_read': True})
        
        db.session.commit()
        return count
    
    @staticmethod
    def get_unread_count(user_id):
        """
        获取用户未读通知数量
        
        Args:
            user_id: 用户ID
        
        Returns:
            未读数量
        """
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
    
    @staticmethod
    def delete_old_notifications(days=30):
        """
        删除旧通知（定时任务）
        
        Args:
            days: 保留天数
        
        Returns:
            删除的通知数量
        """
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        count = Notification.query.filter(
            Notification.created_date < cutoff_date,
            Notification.is_read == True
        ).delete()
        
        db.session.commit()
        return count
