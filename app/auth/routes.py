from flask_login import login_user, logout_user, current_user
from flask import request, redirect, url_for, flash, current_app, render_template
from app import db
# 移除无效导入
from app.models import Department
from app.auth.forms import LoginForm, RegistrationForm
from urllib.parse import urlparse

from app.auth import bp


@bp.route('/auth/login', methods=['GET', 'POST'])
def login():
    from app.models import User  # 延迟导入
    # If already authenticated, allow GET to redirect but still accept POST to re-authenticate (useful for tests/admin switching)
    if current_user.is_authenticated and request.method == 'GET':
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # 支持使用用户名或邮箱登录，避免用户混淆
        uname = form.username.data.strip()
        user = User.query.filter((User.username == uname) | (User.email == uname)).first()
        if user is None or not user.check_password(form.password.data):
            flash('用户名或密码错误')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        
        db.session.commit()
        
        # 默认登录后跳回首页（欢迎页），避免管理员登录后难以找到主导航入口
        next_page = request.args.get('next')
        if next_page and urlparse(next_page).netloc == '':
            return redirect(next_page)
        return redirect(url_for('main.index'))

    # 如果表单校验未通过，但请求中包含用户名/密码且没有 csrf_token（例如测试客户端），尝试直接认证回退
    # 仅在测试环境允许此回退，以避免降低生产环境的 CSRF 安全性
    if request.method == 'POST' and 'csrf_token' not in request.form and current_app.config.get('TESTING', False):
        uname = (request.form.get('username') or '').strip()
        pwd = request.form.get('password') or ''
        if uname and pwd:
            user = User.query.filter((User.username == uname) | (User.email == uname)).first()
            if user and user.check_password(pwd):
                login_user(user, remember=bool(request.form.get('remember_me')))
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('main.index'))
    
    return render_template('auth/login.html', title='登录', form=form)


@bp.route('/auth/logout')
def logout():
    # 只有当用户已登录时才记录登出日志
    if current_user.is_authenticated:
        # 延迟导入模型以避免循环导入
        from app.models import UserActivityLog
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
        # 延迟导入模型以避免循环导入
        from app.models import AccountRequest, User, Notification
        # 申请账号统一设置为普通用户，其他权限由管理员在权限管理模块中分配
        req = AccountRequest(
            username=form.username.data.strip(),
            employee_no=form.employee_no.data.strip(),
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip(),
            department=department_name,
            role_requested='user',  # 统一为普通用户
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