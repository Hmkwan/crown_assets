from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import bp
from app.models import User, UserActivityLog
from app.auth.forms import LoginForm, RegistrationForm
from urllib.parse import urlparse


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
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


@bp.route('/logout')
def logout():
    # 记录用户登出活动
    if current_user.is_authenticated:
        activity_log = UserActivityLog(
            user_id=current_user.id,
            action='用户登出',
            description=f'用户 {current_user.username} 登出系统'
        )
        db.session.add(activity_log)
        db.session.commit()
    
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # 只有管理员可以注册新用户
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            department=form.department.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('用户创建成功')
        
        # 记录用户注册活动
        activity_log = UserActivityLog(
            user_id=user.id,
            action='用户注册',
            description=f'新用户 {user.username} 注册系统'
        )
        db.session.add(activity_log)
        db.session.commit()
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='注册', form=form)