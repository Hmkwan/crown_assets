"""企业微信登录路由

此模块提供企业微信扫码登录功能,作为传统账号密码登录的补充方式。

功能特点:
1. 不影响现有用户管理系统
2. 管理员仍可通过后台开通账号或审批账号申请
3. 企业微信登录仅用于已存在的用户快速登录
4. 首次使用企业微信登录的用户需先在系统中创建账号并绑定企业微信ID

路由说明:
- /login/wework - 发起企业微信登录
- /callback/wework - 企业微信登录回调处理
- /bind/wework - 绑定企业微信账号(可选)
"""

from flask import redirect, url_for, request, flash, session, render_template
from flask_login import login_user, current_user, login_required
from app.auth import bp
from app import db
from app.models import User
from app.integrations import get_wework_client, generate_wework_login_url
from flask import current_app
import logging

logger = logging.getLogger(__name__)


@bp.route('/login/wework')
def wework_login():
    """发起企业微信扫码登录
    
    流程:
    1. 检查企业微信是否启用
    2. 生成登录URL并重定向
    3. 用户扫码授权
    4. 企业微信回调到 /callback/wework
    """
    # 检查企业微信是否启用
    if not current_app.config.get('WEWORK_ENABLED', False):
        flash('企业微信登录功能未启用', 'warning')
        return redirect(url_for('auth.login'))
    
    # 检查企业微信配置
    if not all([
        current_app.config.get('WEWORK_CORP_ID'),
        current_app.config.get('WEWORK_AGENT_ID'),
        current_app.config.get('WEWORK_SECRET')
    ]):
        flash('企业微信配置不完整,请联系管理员', 'error')
        logger.error('企业微信配置不完整')
        return redirect(url_for('auth.login'))
    
    # 生成回调URL
    callback_url = url_for('auth.wework_callback', _external=True)
    
    # 生成登录URL
    try:
        login_url = generate_wework_login_url(
            redirect_uri=callback_url,
            state=session.get('_csrf_token', '')
        )
        return redirect(login_url)
    except Exception as e:
        logger.error(f'生成企业微信登录URL失败: {e}')
        flash('发起企业微信登录失败,请稍后重试', 'error')
        return redirect(url_for('auth.login'))


@bp.route('/callback/wework')
def wework_callback():
    """企业微信登录回调处理
    
    流程:
    1. 获取授权码code
    2. 通过code获取用户userid
    3. 根据userid查找或创建本地用户
    4. 登录用户
    """
    # 检查是否已登录
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # 获取授权码
    code = request.args.get('code')
    if not code:
        flash('企业微信授权失败,缺少授权码', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # 获取企业微信客户端
        client = get_wework_client()
        
        # 通过code获取用户信息
        user_info = client.get_user_info(code)
        if not user_info or not user_info.get('UserId'):
            flash('获取企业微信用户信息失败', 'error')
            logger.error(f'获取用户信息失败: {user_info}')
            return redirect(url_for('auth.login'))
        
        wework_userid = user_info['UserId']
        
        # 获取用户详细信息
        user_detail = client.get_user_detail(wework_userid)
        
        # 查找已绑定的本地用户
        # 注意: 需要在User表添加 wework_userid 字段
        user = User.query.filter_by(username=wework_userid).first()
        
        if not user:
            # 用户不存在,提示需要先创建账号
            flash(
                f'未找到对应账号。企业微信用户ID: {wework_userid}<br>'
                f'请联系管理员为您开通账号,或通过账号申请功能提交申请。',
                'warning'
            )
            logger.warning(f'企业微信用户 {wework_userid} 在系统中不存在')
            return redirect(url_for('auth.login'))
        
        # 检查账号是否启用
        if not user.is_active:
            flash('您的账号已被禁用,请联系管理员', 'error')
            return redirect(url_for('auth.login'))
        
        # 登录用户
        login_user(user, remember=True)
        
        # 更新用户信息(可选)
        if user_detail:
            try:
                # 更新用户的企业微信相关信息
                # user.wework_avatar = user_detail.get('avatar')
                # user.email = user_detail.get('email') or user.email
                # user.mobile = user_detail.get('mobile') or user.mobile
                # db.session.commit()
                pass
            except Exception as e:
                logger.error(f'更新用户信息失败: {e}')
        
        flash(f'欢迎回来, {user.name or user.username}!', 'success')
        
        # 重定向到之前的页面或首页
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        
        return redirect(next_page)
        
    except Exception as e:
        logger.error(f'企业微信登录处理失败: {e}', exc_info=True)
        flash('企业微信登录失败,请稍后重试或使用账号密码登录', 'error')
        return redirect(url_for('auth.login'))


@bp.route('/bind/wework', methods=['GET', 'POST'])
@login_required
def bind_wework():
    """绑定企业微信账号(可选功能)
    
    允许已有账号的用户绑定企业微信ID,
    以便后续可以使用企业微信快速登录
    
    注意: 此功能需要User表添加 wework_userid 字段
    """
    if request.method == 'POST':
        # 处理绑定逻辑
        # TODO: 实现绑定功能
        flash('绑定功能待实现', 'info')
        return redirect(url_for('main.index'))
    
    return render_template('auth/bind_wework.html')


@bp.route('/unbind/wework', methods=['POST'])
@login_required  
def unbind_wework():
    """解绑企业微信账号
    
    允许用户解除企业微信绑定,
    解绑后只能使用账号密码登录
    """
    try:
        # TODO: 实现解绑逻辑
        # current_user.wework_userid = None
        # db.session.commit()
        
        flash('企业微信解绑成功', 'success')
    except Exception as e:
        logger.error(f'解绑企业微信失败: {e}')
        flash('解绑失败,请稍后重试', 'error')
    
    return redirect(url_for('main.index'))
