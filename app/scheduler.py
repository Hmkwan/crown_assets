"""
定时任务调度器
用于执行定期检查和自动提醒任务
"""
from datetime import datetime, timedelta
# Lazy import APScheduler classes inside init_scheduler to avoid import errors during test collection
from flask import current_app
from app.models import EquipmentLoan, User, Equipment, Notification, MaintenancePlan
from app import db
from app.utils import get_beijing_now

# 全局变量保存app实例
_app = None


def check_overdue_loans():
    """
    检查逾期借用并发送通知
    每天早上9点执行
    """
    with _app.app_context():
        try:
            now = get_beijing_now()
            
            # 查找所有借用中且已逾期的记录
            overdue_loans = EquipmentLoan.query.filter(
                EquipmentLoan.status.in_(['borrowed', 'approved']),
                EquipmentLoan.end_date < now
            ).all()
            
            if not overdue_loans:
                _app.logger.info(f"[定时任务] 逾期检查完成,无逾期借用 ({now.strftime('%Y-%m-%d %H:%M')})")
                return
            
            # 获取所有管理员
            admins = User.query.filter_by(role='admin').all()
            
            notification_count = 0
            
            for loan in overdue_loans:
                # 计算逾期天数
                days_overdue = (now.date() - loan.end_date.date()).days
                
                equipment_name = loan.equipment.name if loan.equipment else "未知设备"
                equipment_sn = loan.equipment.serial_number if loan.equipment and loan.equipment.serial_number else "无"
                
                # 发送通知给借用人
                if loan.requester:
                    message = f"您借用的设备【{equipment_name}】(编号:{equipment_sn})已逾期{days_overdue}天,计划归还日期为{loan.end_date.strftime('%Y-%m-%d')},请尽快归还!"
                    
                    notification = Notification(
                        user_id=loan.requester_id,
                        message=message,
                        link=f'/loans/my',
                        created_at=now
                    )
                    db.session.add(notification)
                    notification_count += 1
                    
                    _app.logger.info(f"[定时任务] 发送逾期通知给用户 {loan.requester.username}: 借用ID={loan.id}, 逾期{days_overdue}天")
                
                # 每3天发送一次通知给管理员(避免通知过多)
                if days_overdue % 3 == 1:
                    for admin in admins:
                        admin_message = f"设备借用逾期提醒:【{equipment_name}】(编号:{equipment_sn})由 {loan.requester.username if loan.requester else '未知用户'} 借用,已逾期{days_overdue}天"
                        
                        admin_notification = Notification(
                            user_id=admin.id,
                            message=admin_message,
                            link=f'/loan_requests',
                            created_at=now
                        )
                        db.session.add(admin_notification)
                        notification_count += 1
            
            db.session.commit()
            _app.logger.info(f"[定时任务] 逾期检查完成,发现{len(overdue_loans)}条逾期记录,发送{notification_count}条通知")
            
        except Exception as e:
            _app.logger.error(f"[定时任务] 逾期检查失败: {str(e)}")
            db.session.rollback()


def check_upcoming_return_dates():
    """
    检查即将到期的借用(3天内到期)
    每天早上9点执行
    """
    with _app.app_context():
        try:
            now = get_beijing_now()
            three_days_later = now + timedelta(days=3)
            
            # 查找3天内到期的借用
            upcoming_loans = EquipmentLoan.query.filter(
                EquipmentLoan.status.in_(['borrowed', 'approved']),
                EquipmentLoan.end_date > now,
                EquipmentLoan.end_date <= three_days_later
            ).all()
            
            if not upcoming_loans:
                _app.logger.info(f"[定时任务] 即将到期检查完成,无即将到期借用 ({now.strftime('%Y-%m-%d %H:%M')})")
                return
            
            notification_count = 0
            
            for loan in upcoming_loans:
                days_left = (loan.end_date.date() - now.date()).days
                
                equipment_name = loan.equipment.name if loan.equipment else "未知设备"
                equipment_sn = loan.equipment.serial_number if loan.equipment and loan.equipment.serial_number else "无"
                
                # 发送提醒给借用人
                if loan.requester:
                    if days_left == 0:
                        message = f"您借用的设备【{equipment_name}】(编号:{equipment_sn})今天到期,请及时归还!"
                    else:
                        message = f"您借用的设备【{equipment_name}】(编号:{equipment_sn})将在{days_left}天后到期({loan.end_date.strftime('%Y-%m-%d')}),请做好归还准备!"
                    
                    notification = Notification(
                        user_id=loan.requester_id,
                        message=message,
                        link=f'/loans/my',
                        created_at=now
                    )
                    db.session.add(notification)
                    notification_count += 1
                    
                    _app.logger.info(f"[定时任务] 发送到期提醒给用户 {loan.requester.username}: 借用ID={loan.id}, 剩余{days_left}天")
            
            db.session.commit()
            _app.logger.info(f"[定时任务] 即将到期检查完成,发现{len(upcoming_loans)}条记录,发送{notification_count}条提醒")
            
        except Exception as e:
            _app.logger.error(f"[定时任务] 即将到期检查失败: {str(e)}")
            db.session.rollback()


def check_pending_return_inspections():
    """
    检查待验收的归还申请(超过2天未处理)
    每天早上10点执行
    """
    with _app.app_context():
        try:
            now = get_beijing_now()
            two_days_ago = now - timedelta(days=2)
            
            # 查找超过2天未验收的归还申请
            pending_inspections = EquipmentLoan.query.filter(
                EquipmentLoan.status == 'return_pending',
                EquipmentLoan.return_request_date < two_days_ago
            ).all()
            
            if not pending_inspections:
                _app.logger.info(f"[定时任务] 待验收检查完成,无超时待验收 ({now.strftime('%Y-%m-%d %H:%M')})")
                return
            
            # 获取所有管理员
            admins = User.query.filter_by(role='admin').all()
            notification_count = 0
            
            for loan in pending_inspections:
                days_pending = (now.date() - loan.return_request_date.date()).days
                
                equipment_name = loan.equipment.name if loan.equipment else "未知设备"
                requester_name = loan.requester.username if loan.requester else "未知用户"
                
                # 发送通知给管理员
                for admin in admins:
                    message = f"归还验收提醒:【{equipment_name}】的归还申请已等待{days_pending}天,请尽快处理!申请人:{requester_name}"
                    
                    notification = Notification(
                        user_id=admin.id,
                        message=message,
                        link=f'/loans/return-pending',
                        created_at=now
                    )
                    db.session.add(notification)
                    notification_count += 1
            
            db.session.commit()
            _app.logger.info(f"[定时任务] 待验收检查完成,发现{len(pending_inspections)}条超时记录,发送{notification_count}条通知")
            
        except Exception as e:
            _app.logger.error(f"[定时任务] 待验收检查失败: {str(e)}")
            db.session.rollback()


def check_maintenance_due():
    """
    检查即将到期的保养计划(3天内)
    每天早上8点执行
    """
    with _app.app_context():
        try:
            now = get_beijing_now()
            seven_days_later = now.date() + timedelta(days=7)
            
            # 查找7天内到期的保养计划
            due_plans = MaintenancePlan.query.filter(
                MaintenancePlan.is_active == True,
                MaintenancePlan.next_maintenance_date <= seven_days_later,
                MaintenancePlan.next_maintenance_date >= now.date()
            ).all()
            
            if not due_plans:
                _app.logger.info(f"[定时任务] 保养提醒检查完成,无即将到期保养 ({now.strftime('%Y-%m-%d %H:%M')})")
                return
            
            notification_count = 0
            
            for plan in due_plans:
                days_until_due = (plan.next_maintenance_date - now.date()).days
                
                equipment_name = plan.equipment.name if plan.equipment else "未知设备"
                equipment_sn = plan.equipment.serial_number if plan.equipment and plan.equipment.serial_number else "无"
                
                # 发送提醒给负责人
                if plan.responsible:
                    if days_until_due == 0:
                        message = f"设备保养提醒:【{equipment_name}】(编号:{equipment_sn})今天需要保养!保养项目:{plan.plan_name}"
                    else:
                        message = f"设备保养提醒:【{equipment_name}】(编号:{equipment_sn})将在{days_until_due}天后需要保养({plan.next_maintenance_date.strftime('%Y-%m-%d')}),保养项目:{plan.plan_name}"
                    
                    notification = Notification(
                        user_id=plan.responsible_person,
                        message=message,
                        link=f'/maintenance/plans',
                        created_at=now
                    )
                    db.session.add(notification)
                    notification_count += 1
                    
                    _app.logger.info(f"[定时任务] 发送保养提醒给用户 {plan.responsible.username}: 计划ID={plan.id}, {days_until_due}天后到期")
            
            db.session.commit()
            _app.logger.info(f"[定时任务] 保养提醒检查完成,发现{len(due_plans)}个计划,发送{notification_count}条提醒")
            
        except Exception as e:
            _app.logger.error(f"[定时任务] 保养提醒检查失败: {str(e)}")
            db.session.rollback()


def check_pending_approvals():
    """
    检查待审批的工单并发送提醒
    每天上午10:30和下午15:00执行
    提醒审批人有待处理的审批任务
    """
    with _app.app_context():
        try:
            from app.models import ApprovalWorkflow
            
            now = get_beijing_now()
            
            # 查找所有待审批的工作流节点
            pending_approvals = ApprovalWorkflow.query.filter(
                ApprovalWorkflow.status == 'pending'
            ).all()
            
            if not pending_approvals:
                _app.logger.info(f"[定时任务] 审批提醒检查完成,无待审批事项 ({now.strftime('%Y-%m-%d %H:%M')})")
                return
            
            # 按审批人分组统计
            approver_stats = {}
            
            # 工单类型映射
            order_type_map = {
                'repair_order': '维修工单',
                'part_request_order': '配件申请',
                'equipment_application': '设备申请',
                'equipment_loan': '设备借用',
                'equipment_transfer': '设备调拨',
                'equipment_scrap': '设备报废',
            }
            
            for approval in pending_approvals:
                if not approval.approver_id:
                    continue
                    
                if approval.approver_id not in approver_stats:
                    approver_stats[approval.approver_id] = {
                        'approver': approval.approver,
                        'items': []
                    }
                
                # 获取工单类型名称
                type_name = order_type_map.get(approval.order_type, '其他申请')
                approver_stats[approval.approver_id]['items'].append({
                    'type_name': type_name,
                    'order_id': approval.order_id,
                    'approval_id': approval.id
                })
            
            notification_count = 0
            
            # 为每个审批人发送汇总通知
            for approver_id, stats in approver_stats.items():
                items = stats['items']
                if not items:
                    continue
                
                # 统计各类型工单数量
                type_counts = {}
                for item in items:
                    type_name = item['type_name']
                    type_counts[type_name] = type_counts.get(type_name, 0) + 1
                
                # 构建消息
                type_summary = ', '.join([f"{name}{count}条" for name, count in type_counts.items()])
                message = f"您有{len(items)}条待审批事项({type_summary}),请及时处理。"
                
                notification = Notification(
                    user_id=approver_id,
                    title="审批待办提醒",
                    message=message,
                    order_type='approval',
                    order_id=None
                )
                db.session.add(notification)
                notification_count += 1
                
                _app.logger.info(f"[定时任务] 发送审批提醒给用户 {stats['approver'].username}: {len(items)}条待审批")
            
            db.session.commit()
            _app.logger.info(f"[定时任务] 审批提醒检查完成,发现{len(pending_approvals)}条待审批,通知{notification_count}个审批人")
            
        except Exception as e:
            _app.logger.error(f"[定时任务] 审批提醒检查失败: {str(e)}")
            db.session.rollback()


def init_scheduler(app):
    """
    初始化定时任务调度器
    可以通过配置禁用特定任务
    """
    # 保存app实例到全局变量
    global _app
    _app = app
    
    # 检查是否启用调度器
    if not app.config.get('SCHEDULER_ENABLED', True):
        app.logger.info('[调度器] 定时任务调度器已禁用')
        return
    
    # 延迟导入 apscheduler，以避免在没有该依赖的测试/环境中抛出 ImportError
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except Exception as e:
        app.logger.warning('[调度器] apscheduler 未安装或不可用，跳过调度器初始化: %s', e)
        return None

    scheduler = BackgroundScheduler(
        timezone='Asia/Shanghai',
        job_defaults={
            'coalesce': True,  # 合并错过的任务
            'max_instances': 1  # 同一任务最多只有1个实例运行
        }
    )
    
    jobs_config = app.config.get('SCHEDULER_JOBS', {})
    
    # 每天早上8点检查保养计划
    if jobs_config.get('maintenance_due', True):
        scheduler.add_job(
            func=check_maintenance_due,
            trigger=CronTrigger(hour=8, minute=0),
            id='check_maintenance_due',
            name='检查保养计划',
            replace_existing=True
        )
    
    # 每天早上9点检查逾期借用
    if jobs_config.get('overdue_loans', True):
        scheduler.add_job(
            func=check_overdue_loans,
            trigger=CronTrigger(hour=9, minute=0),
            id='check_overdue_loans',
            name='检查逾期借用',
            replace_existing=True
        )
    
    # 每天早上9点检查即将到期的借用
    if jobs_config.get('upcoming_returns', True):
        scheduler.add_job(
            func=check_upcoming_return_dates,
            trigger=CronTrigger(hour=9, minute=0),
            id='check_upcoming_returns',
            name='检查即将到期借用',
            replace_existing=True
        )
    
    # 每天早上10点检查待验收归还
    if jobs_config.get('pending_inspections', True):
        scheduler.add_job(
            func=check_pending_return_inspections,
            trigger=CronTrigger(hour=10, minute=0),
            id='check_pending_inspections',
            name='检查待验收归还',
            replace_existing=True
        )
    
    # 每天上午10:30和下午15:00检查待审批事项
    if jobs_config.get('pending_approvals', True):
        scheduler.add_job(
            func=check_pending_approvals,
            trigger=CronTrigger(hour='10,15', minute=30),
            id='check_pending_approvals',
            name='检查待审批事项',
            replace_existing=True
        )
    
    scheduler.start()
    app.logger.info("[调度器] 定时任务调度器已启动")
    
    return scheduler

