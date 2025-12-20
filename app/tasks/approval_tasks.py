"""
审批系统定时任务
处理超时、提醒、自动审批等后台任务
"""

from app import create_app, db, get_beijing_now
from app.approval_models import (
    ApprovalInstance, ApprovalStep, ApprovalLog, 
    ApprovalReminder, WorkflowNode
)
from app.approval_engine import ApprovalEngine
from app.services.approval_notification_service import ApprovalNotificationService
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()


def check_and_process_timeouts():
    """检查并处理超时的审批"""
    with app.app_context():
        logger.info("开始检查超时审批...")
        
        now = get_beijing_now()
        
        # 查找所有超时的待审批步骤
        overdue_steps = ApprovalStep.query.filter(
            ApprovalStep.status == 'pending',
            ApprovalStep.deadline.isnot(None),
            ApprovalStep.deadline < now
        ).all()
        
        logger.info(f"发现 {len(overdue_steps)} 个超时审批")
        
        for step in overdue_steps:
            try:
                process_timeout_step(step)
            except Exception as e:
                logger.error(f"处理超时审批 {step.id} 失败: {e}")
                continue
        
        db.session.commit()
        logger.info("超时审批处理完成")


def process_timeout_step(step):
    """处理单个超时步骤"""
    node = step.node
    
    if not node.timeout_action:
        # 没有配置超时动作,仅发送通知
        ApprovalNotificationService.notify_approval_overdue(step)
        return
    
    logger.info(f"处理超时步骤 {step.id}, 动作: {node.timeout_action}")
    
    if node.timeout_action == 'auto_approve':
        # 自动通过
        ApprovalEngine.approve_step(
            step_id=step.id,
            approver_id=None,  # 系统自动
            comments='系统超时自动通过',
            ip_address='system',
            user_agent='auto-approval-task'
        )
        logger.info(f"步骤 {step.id} 超时自动通过")
    
    elif node.timeout_action == 'auto_reject':
        # 自动拒绝
        ApprovalEngine.reject_step(
            step_id=step.id,
            approver_id=None,
            comments='系统超时自动拒绝',
            ip_address='system',
            user_agent='auto-approval-task'
        )
        logger.info(f"步骤 {step.id} 超时自动拒绝")
    
    elif node.timeout_action == 'escalate':
        # 升级到上级
        if node.escalate_to_user_id:
            old_approver_id = step.approver_id
            step.approver_id = node.escalate_to_user_id
            step.updated_at = get_beijing_now()
            
            # 记录日志
            log = ApprovalLog(
                instance_id=step.instance_id,
                step_id=step.id,
                action='escalate',
                actor_id=None,
                from_user_id=old_approver_id,
                to_user_id=node.escalate_to_user_id,
                comments='超时自动升级',
                ip_address='system',
                user_agent='auto-approval-task'
            )
            db.session.add(log)
            
            # 通知新审批人
            ApprovalNotificationService.notify_new_approval(step)
            logger.info(f"步骤 {step.id} 升级到用户 {node.escalate_to_user_id}")
    
    elif node.timeout_action == 'notify':
        # 仅通知
        ApprovalNotificationService.notify_approval_overdue(step)
        logger.info(f"步骤 {step.id} 发送超时通知")


def send_deadline_reminders():
    """发送截止日期提醒"""
    with app.app_context():
        logger.info("开始发送截止日期提醒...")
        
        now = get_beijing_now()
        remind_time = now + timedelta(hours=24)
        
        # 查找即将到期的审批(24小时内)
        approaching_steps = ApprovalStep.query.filter(
            ApprovalStep.status == 'pending',
            ApprovalStep.deadline.isnot(None),
            ApprovalStep.deadline > now,
            ApprovalStep.deadline <= remind_time
        ).all()
        
        logger.info(f"发现 {len(approaching_steps)} 个即将到期的审批")
        
        for step in approaching_steps:
            try:
                # 检查是否已发送提醒
                existing_reminder = ApprovalReminder.query.filter_by(
                    step_id=step.id,
                    reminder_type='deadline',
                    status='sent'
                ).first()
                
                if not existing_reminder:
                    ApprovalNotificationService.notify_deadline_approaching(step)
                    logger.info(f"发送截止提醒给步骤 {step.id}")
            except Exception as e:
                logger.error(f"发送提醒失败 {step.id}: {e}")
                continue
        
        db.session.commit()
        logger.info("截止日期提醒发送完成")


def process_auto_approval_rules():
    """处理自动审批规则"""
    with app.app_context():
        logger.info("开始处理自动审批规则...")
        
        # 查找配置了自动审批规则的待审批步骤
        pending_steps = ApprovalStep.query.filter_by(status='pending').all()
        
        auto_approved = 0
        
        for step in pending_steps:
            try:
                if check_auto_approval(step):
                    ApprovalEngine.approve_step(
                        step_id=step.id,
                        approver_id=None,
                        comments='满足自动审批条件,系统自动通过',
                        ip_address='system',
                        user_agent='auto-approval-task'
                    )
                    auto_approved += 1
                    logger.info(f"步骤 {step.id} 满足自动审批条件")
            except Exception as e:
                logger.error(f"处理自动审批失败 {step.id}: {e}")
                continue
        
        db.session.commit()
        logger.info(f"自动审批处理完成,共自动通过 {auto_approved} 个")


def check_auto_approval(step):
    """检查是否满足自动审批条件"""
    node = step.node
    
    if not node.auto_approve_rules:
        return False
    
    try:
        import json
        rules = json.loads(node.auto_approve_rules) if isinstance(node.auto_approve_rules, str) else node.auto_approve_rules
        
        # 获取工单上下文数据
        instance = step.instance
        context = {}
        
        if instance.context_data:
            context = json.loads(instance.context_data) if isinstance(instance.context_data, str) else instance.context_data
        
        # 检查规则
        for key, value in rules.items():
            if key == 'amount_below':
                if context.get('total_cost', 0) >= value:
                    return False
            elif key == 'amount_above':
                if context.get('total_cost', 0) < value:
                    return False
            elif key == 'type':
                if context.get('type') != value:
                    return False
            elif key == 'priority':
                if context.get('priority') != value:
                    return False
            elif key == 'department':
                if context.get('department') != value:
                    return False
        
        return True
    except Exception as e:
        logger.error(f"检查自动审批规则失败: {e}")
        return False


def cleanup_old_notifications():
    """清理旧通知"""
    with app.app_context():
        logger.info("开始清理旧通知...")
        
        from app.models import Notification
        
        # 删除30天前已读的通知
        cutoff_date = get_beijing_now() - timedelta(days=30)
        
        deleted = Notification.query.filter(
            Notification.is_read == True,
            Notification.created_date < cutoff_date
        ).delete()
        
        db.session.commit()
        logger.info(f"清理完成,删除了 {deleted} 条旧通知")


def generate_approval_statistics():
    """生成审批统计报告"""
    with app.app_context():
        logger.info("开始生成审批统计...")
        
        now = get_beijing_now()
        
        # 统计各种状态的审批
        total_pending = ApprovalStep.query.filter_by(status='pending').count()
        total_approved = ApprovalStep.query.filter_by(status='approved').count()
        total_rejected = ApprovalStep.query.filter_by(status='rejected').count()
        
        # 统计超时的审批
        overdue = ApprovalStep.query.filter(
            ApprovalStep.status == 'pending',
            ApprovalStep.deadline.isnot(None),
            ApprovalStep.deadline < now
        ).count()
        
        # 统计平均审批时长
        completed_steps = ApprovalStep.query.filter(
            ApprovalStep.status.in_(['approved', 'rejected']),
            ApprovalStep.processed_at.isnot(None)
        ).all()
        
        if completed_steps:
            total_duration = sum([
                (step.processed_at - step.assigned_at).total_seconds() 
                for step in completed_steps
            ])
            avg_duration_hours = total_duration / len(completed_steps) / 3600
        else:
            avg_duration_hours = 0
        
        stats = {
            'timestamp': now.isoformat(),
            'total_pending': total_pending,
            'total_approved': total_approved,
            'total_rejected': total_rejected,
            'overdue': overdue,
            'avg_duration_hours': round(avg_duration_hours, 2)
        }
        
        logger.info(f"审批统计: {stats}")
        
        # 可以将统计结果保存到数据库或文件
        return stats


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python approval_tasks.py [task_name]")
        print("可用任务:")
        print("  timeout        - 处理超时审批")
        print("  reminder       - 发送截止提醒")
        print("  auto_approve   - 处理自动审批")
        print("  cleanup        - 清理旧通知")
        print("  stats          - 生成统计报告")
        print("  all            - 运行所有任务")
        sys.exit(1)
    
    task = sys.argv[1]
    
    try:
        if task == 'timeout':
            check_and_process_timeouts()
        elif task == 'reminder':
            send_deadline_reminders()
        elif task == 'auto_approve':
            process_auto_approval_rules()
        elif task == 'cleanup':
            cleanup_old_notifications()
        elif task == 'stats':
            stats = generate_approval_statistics()
            print(f"统计结果: {stats}")
        elif task == 'all':
            check_and_process_timeouts()
            send_deadline_reminders()
            process_auto_approval_rules()
            cleanup_old_notifications()
            generate_approval_statistics()
        else:
            print(f"未知任务: {task}")
            sys.exit(1)
        
        print(f"✅ 任务 '{task}' 执行成功")
    except Exception as e:
        logger.error(f"任务执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
