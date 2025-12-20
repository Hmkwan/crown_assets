"""
设备保养计划管理路由
"""
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import MaintenancePlan, MaintenanceRecord, Equipment, User, Notification, AssetLifecycle
from app.utils import get_beijing_now
from app.main import bp
from datetime import datetime, timedelta


@bp.route('/maintenance/plans')
@login_required
def maintenance_plans():
    """保养计划列表"""
    status_filter = request.args.get('status', 'active')
    
    query = MaintenancePlan.query
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    elif status_filter == 'due_soon':
        # 7天内到期
        seven_days_later = (get_beijing_now().date() + timedelta(days=7))
        query = query.filter(
            MaintenancePlan.is_active == True,
            MaintenancePlan.next_maintenance_date <= seven_days_later
        )
    
    # 非管理员只能看自己负责的
    if current_user.role != 'admin':
        query = query.filter_by(responsible_person=current_user.id)
    
    plans = query.order_by(MaintenancePlan.next_maintenance_date.asc()).all()
    
    # 统计
    stats = {
        'total': MaintenancePlan.query.count(),
        'active': MaintenancePlan.query.filter_by(is_active=True).count(),
        'due_soon': MaintenancePlan.query.filter(
            MaintenancePlan.is_active == True,
            MaintenancePlan.next_maintenance_date <= (get_beijing_now().date() + timedelta(days=7))
        ).count()
    }
    
    return render_template('main/maintenance_plans.html',
                         title='保养计划管理',
                         plans=plans,
                         stats=stats,
                         status_filter=status_filter)


@bp.route('/maintenance/plans/create', methods=['GET', 'POST'])
@login_required
def create_maintenance_plan():
    """创建保养计划"""
    if current_user.role != 'admin':
        flash('权限不足', 'danger')
        return redirect(url_for('main.maintenance_plans'))
    
    if request.method == 'POST':
        try:
            equipment_id = request.form.get('equipment_id', type=int)
            plan_name = request.form.get('plan_name')
            maintenance_type = request.form.get('maintenance_type')
            interval_days = request.form.get('interval_days', type=int)
            next_date = request.form.get('next_maintenance_date')
            responsible_person = request.form.get('responsible_person', type=int)
            description = request.form.get('description', '')
            
            if not all([equipment_id, plan_name, maintenance_type, next_date, responsible_person]):
                flash('请填写所有必填项', 'warning')
                return redirect(request.url)
            
            # 类型映射的默认间隔天数
            type_intervals = {
                'daily': 1,
                'weekly': 7,
                'monthly': 30,
                'quarterly': 90,
                'yearly': 365
            }
            
            if maintenance_type in type_intervals and not interval_days:
                interval_days = type_intervals[maintenance_type]
            
            plan = MaintenancePlan(
                equipment_id=equipment_id,
                plan_name=plan_name,
                maintenance_type=maintenance_type,
                interval_days=interval_days,
                next_maintenance_date=datetime.strptime(next_date, '%Y-%m-%d').date(),
                responsible_person=responsible_person,
                description=description,
                created_by=current_user.id
            )
            
            db.session.add(plan)
            db.session.commit()
            
            # 发送通知给负责人
            if responsible_person != current_user.id:
                notification = Notification(
                    user_id=responsible_person,
                    message=f'您被指定为设备保养计划"{plan_name}"的负责人',
                    link=f'/maintenance/plans',
                    created_at=get_beijing_now()
                )
                db.session.add(notification)
                db.session.commit()
            
            flash('保养计划创建成功', 'success')
            return redirect(url_for('main.maintenance_plans'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败: {str(e)}', 'danger')
    
    # 获取设备列表
    equipments = Equipment.query.filter(
        Equipment.status.in_(['available', 'in_use'])
    ).order_by(Equipment.name).all()
    
    # 获取用户列表
    users = User.query.filter_by(is_active=True).order_by(User.username).all()
    
    return render_template('main/create_maintenance_plan.html',
                         title='创建保养计划',
                         equipments=equipments,
                         users=users)


@bp.route('/maintenance/plans/<int:plan_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_maintenance_plan(plan_id):
    """编辑保养计划"""
    plan = MaintenancePlan.query.get_or_404(plan_id)
    
    if current_user.role != 'admin':
        flash('权限不足', 'danger')
        return redirect(url_for('main.maintenance_plans'))
    
    if request.method == 'POST':
        try:
            plan.plan_name = request.form.get('plan_name')
            plan.maintenance_type = request.form.get('maintenance_type')
            plan.interval_days = request.form.get('interval_days', type=int)
            plan.next_maintenance_date = datetime.strptime(
                request.form.get('next_maintenance_date'), '%Y-%m-%d'
            ).date()
            plan.responsible_person = request.form.get('responsible_person', type=int)
            plan.description = request.form.get('description', '')
            plan.is_active = request.form.get('is_active') == 'on'
            
            db.session.commit()
            flash('保养计划更新成功', 'success')
            return redirect(url_for('main.maintenance_plans'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')
    
    users = User.query.filter_by(is_active=True).order_by(User.username).all()
    
    return render_template('main/edit_maintenance_plan.html',
                         title='编辑保养计划',
                         plan=plan,
                         users=users)


@bp.route('/maintenance/plans/<int:plan_id>/complete', methods=['GET', 'POST'])
@login_required
def complete_maintenance(plan_id):
    """完成保养记录"""
    plan = MaintenancePlan.query.get_or_404(plan_id)
    
    # 检查权限
    if current_user.role != 'admin' and plan.responsible_person != current_user.id:
        flash('权限不足', 'danger')
        return redirect(url_for('main.maintenance_plans'))
    
    if request.method == 'POST':
        try:
            description = request.form.get('description')
            notes = request.form.get('notes', '')
            cost = request.form.get('cost', 0.0, type=float)
            
            if not description:
                flash('请填写保养内容', 'warning')
                return redirect(request.url)
            
            # 创建保养记录
            record = MaintenanceRecord(
                plan_id=plan.id,
                equipment_id=plan.equipment_id,
                maintenance_date=get_beijing_now(),
                maintenance_type=plan.maintenance_type,
                performed_by=current_user.id,
                description=description,
                notes=notes,
                cost=cost,
                status='completed'
            )
            
            # 更新计划的下次保养日期
            plan.last_maintenance_date = get_beijing_now().date()
            if plan.interval_days:
                plan.next_maintenance_date = plan.last_maintenance_date + timedelta(days=plan.interval_days)
                record.next_maintenance_date = plan.next_maintenance_date
            
            # 记录生命周期事件
            if cost > 0:
                lifecycle_event = AssetLifecycle(
                    equipment_id=plan.equipment_id,
                    event_type='maintenance',
                    description=f'设备保养: {description}',
                    cost=cost,
                    event_date=get_beijing_now()
                )
                db.session.add(lifecycle_event)
            
            db.session.add(record)
            db.session.commit()
            
            flash('保养记录已提交', 'success')
            return redirect(url_for('main.maintenance_plans'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'提交失败: {str(e)}', 'danger')
    
    return render_template('main/complete_maintenance.html',
                         title='完成保养',
                         plan=plan)


@bp.route('/maintenance/records')
@login_required
def maintenance_records():
    """保养记录列表"""
    equipment_id = request.args.get('equipment_id', type=int)
    
    query = MaintenanceRecord.query
    
    if equipment_id:
        query = query.filter_by(equipment_id=equipment_id)
    
    # 非管理员只能看自己执行的
    if current_user.role != 'admin':
        query = query.filter_by(performed_by=current_user.id)
    
    records = query.order_by(MaintenanceRecord.maintenance_date.desc()).all()
    
    # 统计
    stats = {
        'total': MaintenanceRecord.query.count(),
        'this_month': MaintenanceRecord.query.filter(
            MaintenanceRecord.maintenance_date >= get_beijing_now().replace(day=1)
        ).count(),
        'total_cost': db.session.query(db.func.sum(MaintenanceRecord.cost)).scalar() or 0
    }
    
    equipments = Equipment.query.order_by(Equipment.name).all()
    
    return render_template('main/maintenance_records.html',
                         title='保养记录',
                         records=records,
                         stats=stats,
                         equipments=equipments,
                         equipment_id=equipment_id)
