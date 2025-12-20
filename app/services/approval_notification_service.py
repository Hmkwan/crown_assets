"""
审批系统通知服务
处理审批流程相关的所有通知
"""

from app import db, get_beijing_now
from app.models import Notification, User
from app.approval_models import ApprovalInstance, ApprovalStep, ApprovalReminder
from datetime import datetime, timedelta
import json


class ApprovalNotificationService:
    """审批系统专用通知服务"""
    
    @staticmethod
    def notify_new_approval(step):
        """通知审批人有新的待审批"""
        if not step.approver:
            return None
        
        instance = step.instance
        order_type_map = {
            'repair_order': '维修工单',
            'part_request_order': '备件申请',
            'equipment_application': '设备申请',
            'equipment_transfer': '设备调拨',
            'equipment_scrap': '设备报废',
            'equipment_loan': '设备借用'
        }
        
        order_type_name = order_type_map.get(instance.order_type, instance.order_type)
        
        notification = Notification(
            user_id=step.approver_id,
            title=f'新的{order_type_name}待审批',
            message=f'您有一个新的{order_type_name} #{instance.order_id} 需要审批,节点: {step.node.name}',
            order_type=instance.order_type,
            order_id=instance.order_id,
            is_read=False,
            created_date=get_beijing_now()
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # 创建提醒记录
        if step.deadline:
            ApprovalNotificationService._create_deadline_reminder(step)
        
        return notification
    
    @staticmethod
    def notify_approval_result(instance, result, comments=''):
        """通知发起人审批结果"""
        status_map = {
            'approved': '已通过',
            'rejected': '已拒绝',
            'cancelled': '已取消'
        }
        
        order_type_map = {
            'repair_order': '维修工单',
            'part_request_order': '备件申请',
            'equipment_application': '设备申请',
            'equipment_transfer': '设备调拨',
            'equipment_scrap': '设备报废',
            'equipment_loan': '设备借用'
        }
        
        status_text = status_map.get(result, result)
        order_type_name = order_type_map.get(instance.order_type, instance.order_type)
        
        message = f'您提交的{order_type_name} #{instance.order_id} {status_text}'
        if comments:
            message += f'\n审批意见: {comments}'
        
        notification = Notification(
            user_id=instance.initiator_id,
            title=f'{order_type_name}审批{status_text}',
            message=message,
            order_type=instance.order_type,
            order_id=instance.order_id,
            is_read=False,
            created_date=get_beijing_now()
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return notification
    
    @staticmethod
    def notify_approval_transfer(from_user, to_user, step, reason=''):
        """通知审批转交"""
        instance = step.instance
        order_type_map = {
            'repair_order': '维修工单',
            'part_request_order': '备件申请',
            'equipment_application': '设备申请',
            'equipment_transfer': '设备调拨',
            'equipment_scrap': '设备报废',
            'equipment_loan': '设备借用'
        }
        
        order_type_name = order_type_map.get(instance.order_type, instance.order_type)
        
        # 通知新审批人
        message = f'{from_user.username} 将{order_type_name} #{instance.order_id} 的审批转交给您'
        if reason:
            message += f'\n原因: {reason}'
        
        notification_new = Notification(
            user_id=to_user.id,
            title=f'审批转交通知',
            message=message,
            order_type=instance.order_type,
            order_id=instance.order_id,
            is_read=False,
            created_date=get_beijing_now()
        )
        
        db.session.add(notification_new)
        
        # 通知原审批人
        notification_old = Notification(
            user_id=from_user.id,
            title=f'审批已转交',
            message=f'您已将{order_type_name} #{instance.order_id} 的审批转交给 {to_user.username}',
            order_type=instance.order_type,
            order_id=instance.order_id,
            is_read=False,
            created_date=get_beijing_now()
        )
        
        db.session.add(notification_old)
        db.session.commit()
        
        return notification_new, notification_old
    
    @staticmethod
    def notify_deadline_approaching(step):
        """通知审批即将到期"""
        if not step.approver or not step.deadline:
            return None
        
        instance = step.instance
        order_type_map = {
            'repair_order': '维修工单',
            'part_request_order': '备件申请',
            'equipment_application': '设备申请',
            'equipment_transfer': '设备调拨',
            'equipment_scrap': '设备报废',
            'equipment_loan': '设备借用'
        }
        
        order_type_name = order_type_map.get(instance.order_type, instance.order_type)
        hours_left = int((step.deadline - get_beijing_now()).total_seconds() / 3600)
        
        notification = Notification(
            user_id=step.approver_id,
            title=f'审批即将到期',
            message=f'{order_type_name} #{instance.order_id} 将在 {hours_left} 小时后到期,请及时处理',
            order_type=instance.order_type,
            order_id=instance.order_id,
            is_read=False,
            created_date=get_beijing_now()
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # 记录提醒
        reminder = ApprovalReminder(
            step_id=step.id,
            approver_id=step.approver_id,
            reminder_type='deadline',
            notify_method='system',
            sent_at=get_beijing_now(),
            status='sent'
        )
        db.session.add(reminder)
        db.session.commit()
        
        return notification
    
    @staticmethod
    def notify_approval_overdue(step):
        """通知审批已逾期"""
        if not step.approver:
            return None
        
        instance = step.instance
        order_type_map = {
            'repair_order': '维修工单',
            'part_request_order': '备件申请',
            'equipment_application': '设备申请',
            'equipment_transfer': '设备调拨',
            'equipment_scrap': '设备报废',
            'equipment_loan': '设备借用'
        }
        
        order_type_name = order_type_map.get(instance.order_type, instance.order_type)
        
        notification = Notification(
            user_id=step.approver_id,
            title=f'审批已逾期',
            message=f'{order_type_name} #{instance.order_id} 已逾期,请尽快处理',
            order_type=instance.order_type,
            order_id=instance.order_id,
            is_read=False,
            created_date=get_beijing_now()
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # 记录提醒
        reminder = ApprovalReminder(
            step_id=step.id,
            approver_id=step.approver_id,
            reminder_type='overdue',
            notify_method='system',
            sent_at=get_beijing_now(),
            status='sent'
        )
        db.session.add(reminder)
        db.session.commit()
        
        return notification
    
    @staticmethod
    def _create_deadline_reminder(step):
        """创建截止日期提醒"""
        if not step.deadline:
            return
        
        # 计算提醒时间(截止前24小时)
        reminder_time = step.deadline - timedelta(hours=24)
        
        if reminder_time > get_beijing_now():
            reminder = ApprovalReminder(
                step_id=step.id,
                approver_id=step.approver_id,
                reminder_type='deadline',
                notify_method='system',
                status='pending'
            )
            db.session.add(reminder)
    
    @staticmethod
    def send_batch_notification(user_ids, title, message, order_type=None, order_id=None):
        """批量发送通知"""
        notifications = []
        for user_id in user_ids:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                order_type=order_type,
                order_id=order_id,
                is_read=False,
                created_date=get_beijing_now()
            )
            notifications.append(notification)
        
        db.session.bulk_save_objects(notifications)
        db.session.commit()
        
        return len(notifications)
    
    @staticmethod
    def notify_parallel_approval_result(step, approved_count, required_count):
        """通知并行审批进度"""
        instance = step.instance
        
        # 获取所有参与并行审批的审批人
        parallel_steps = ApprovalStep.query.filter_by(
            instance_id=instance.id,
            parallel_group_id=step.parallel_group_id,
            status='pending'
        ).all()
        
        order_type_map = {
            'repair_order': '维修工单',
            'part_request_order': '备件申请',
            'equipment_application': '设备申请',
            'equipment_transfer': '设备调拨',
            'equipment_scrap': '设备报废',
            'equipment_loan': '设备借用'
        }
        
        order_type_name = order_type_map.get(instance.order_type, instance.order_type)
        
        message = f'{order_type_name} #{instance.order_id} 的并行审批进度: {approved_count}/{required_count}'
        
        for ps in parallel_steps:
            if ps.approver_id:
                notification = Notification(
                    user_id=ps.approver_id,
                    title='并行审批进度更新',
                    message=message,
                    order_type=instance.order_type,
                    order_id=instance.order_id,
                    is_read=False,
                    created_date=get_beijing_now()
                )
                db.session.add(notification)
        
        db.session.commit()
