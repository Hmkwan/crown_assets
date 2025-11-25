from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User, UserActivityLog, AccountRequest, Notification, Department
from app.auth.forms import LoginForm, RegistrationForm
from urllib.parse import urlparse

from app.auth import bp


@bp.route('/auth/login', methods=['GET', 'POST'])
def login():
    # If already authenticated, allow GET to redirect but still accept POST to re-authenticate (useful for tests/admin switching)
    if current_user.is_authenticated and request.method == 'GET':
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('用户名或密码错误')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        
        # 记录用户登录活动
        activity_log = UserActivityLog(
            user_id=user.id,
            action='用户登录',
            description=f'用户 {user.username} 登录系统'
        )
        db.session.add(activity_log)
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            if user.role == 'admin':
                next_page = url_for('main.admin_dashboard')
            elif user.role == 'technician':
                next_page = url_for('main.technician_dashboard')
            else:
                next_page = url_for('main.index')
            
        return redirect(next_page)
    
    return render_template('auth/login.html', title='登录', form=form)


@bp.route('/auth/logout')
def logout():
    # 只有当用户已登录时才记录登出日志
    if current_user.is_authenticated:
        activity_log = UserActivityLog(
            user_id=current_user.id,
            action='用户登出',
            description=f'用户 {current_user.username} 登出系统'
        )
        db.session.add(activity_log)
        db.session.commit()

    # 执行登出操作
    logout_user()
    # 登出后跳转至登录页
    return redirect(url_for('auth.login'))


@bp.route('/auth/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    departments = Department.query.order_by(Department.name).all()
    if not departments:
        flash('尚未配置部门信息，请联系管理员。')
        return redirect(url_for('auth.login'))
    form.department.choices = [(dept.id, dept.name) for dept in departments]
    
    if form.validate_on_submit():
        department_obj = Department.query.get(form.department.data)
        department_name = department_obj.name if department_obj else ''
        req = AccountRequest(
            username=form.username.data.strip(),
            employee_no=form.employee_no.data.strip(),
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip(),
            department=department_name,
            role_requested=form.role_requested.data,
            reason=form.reason.data.strip() if form.reason.data else ''
        )
        req.set_password(form.password.data)
        db.session.add(req)
        db.session.flush()
        
        admins = User.query.filter_by(role='admin').all()
        if not admins:
            flash('系统中暂未配置管理员，无法提交申请。')
            db.session.rollback()
            return redirect(url_for('auth.login'))
        
        for admin in admins:
            notification = Notification(
                user_id=admin.id,
                title='新的账号申请',
                message=f'员工 {req.full_name or req.username} 提交账号申请，请尽快审批。',
                order_type='account_request',
                order_id=req.id
            )
            db.session.add(notification)
        
        db.session.commit()
        flash('账号申请已提交，请等待管理员审批。')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_request.html', title='账号申请', form=form)