"""
报废处置管理路由
"""
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import EquipmentScrap, Equipment, User, Notification, AssetLifecycle
from app.utils import get_beijing_now
from app.main import bp


@bp.route('/scraps/<int:scrap_id>/dispose', methods=['GET', 'POST'])
@login_required
def dispose_scrap(scrap_id):
    """处置报废设备"""
    if current_user.role != 'admin':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    scrap = EquipmentScrap.query.get_or_404(scrap_id)
    
    if scrap.status != 'approved':
        flash('只能处置已批准的报废申请', 'warning')
        return redirect(url_for('main.admin_scraps'))
    
    if request.method == 'POST':
        try:
            disposal_method = request.form.get('disposal_method')
            disposal_date = request.form.get('disposal_date')
            disposal_notes = request.form.get('disposal_notes')
            disposal_value = request.form.get('disposal_value', 0.0, type=float)
            disposal_company = request.form.get('disposal_company', '')
            
            if not disposal_method:
                flash('请选择处置方式', 'warning')
                return redirect(request.url)
            
            # 更新报废记录
            scrap.disposal_method = disposal_method
            scrap.disposal_date = get_beijing_now() if not disposal_date else disposal_date
            scrap.disposal_handler = current_user.id
            scrap.disposal_notes = disposal_notes
            scrap.disposal_value = disposal_value
            scrap.disposal_company = disposal_company
            scrap.status = 'disposed'  # 更新状态为已处置
            
            # 更新设备状态
            if scrap.equipment:
                scrap.equipment.status = 'disposed'
            
            # 记录生命周期事件
            disposal_method_map = {
                'recycling': '回收',
                'donation': '捐赠',
                'destruction': '销毁',
                'sale': '出售'
            }
            method_text = disposal_method_map.get(disposal_method, disposal_method)
            
            lifecycle_event = AssetLifecycle(
                equipment_id=scrap.equipment_id,
                event_type='disposal',
                description=f'设备处置({method_text}): {disposal_notes}',
                cost=-disposal_value if disposal_value > 0 else 0,  # 负数表示收入
                event_date=scrap.disposal_date
            )
            db.session.add(lifecycle_event)
            
            # 发送通知给申请人
            if scrap.requester:
                notification = Notification(
                    user_id=scrap.requester_id,
                    message=f'您申请的设备报废已完成处置,处置方式:{method_text}',
                    link=f'/scraps/{scrap_id}',
                    created_at=get_beijing_now()
                )
                db.session.add(notification)
            
            db.session.commit()
            flash(f'报废设备已处置({method_text})', 'success')
            # scrap_requests endpoint 不存在，重定向到管理员报废管理页
            return redirect(url_for('main.admin_scraps'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'处置失败: {str(e)}', 'danger')
    
    # 处置方式选项
    disposal_methods = [
        ('recycling', '回收利用'),
        ('donation', '捐赠'),
        ('destruction', '销毁'),
        ('sale', '出售')
    ]
    
    return render_template('main/dispose_scrap.html',
                         title='处置报废设备',
                         scrap=scrap,
                         disposal_methods=disposal_methods)


@bp.route('/scraps/<int:scrap_id>/financial_clear', methods=['POST'])
@login_required
def financial_clear_scrap(scrap_id):
    """财务核销报废设备"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    scrap = EquipmentScrap.query.get_or_404(scrap_id)
    
    if scrap.status != 'disposed':
        return jsonify({'success': False, 'message': '只能核销已处置的报废设备'}), 400
    
    if scrap.financial_cleared:
        return jsonify({'success': False, 'message': '该报废设备已核销'}), 400
    
    try:
        financial_notes = request.form.get('financial_notes', '')
        
        scrap.financial_cleared = True
        scrap.financial_cleared_date = get_beijing_now()
        scrap.financial_cleared_by = current_user.id
        scrap.financial_notes = financial_notes
        
        # 记录生命周期事件
        lifecycle_event = AssetLifecycle(
            equipment_id=scrap.equipment_id,
            event_type='financial_clear',
            description=f'财务核销完成: {financial_notes}',
            cost=0,
            event_date=get_beijing_now()
        )
        db.session.add(lifecycle_event)
        
        # 发送通知给申请人
        if scrap.requester:
            notification = Notification(
                user_id=scrap.requester_id,
                message=f'报废设备财务核销完成',
                link=f'/scraps/{scrap_id}',
                created_at=get_beijing_now()
            )
            db.session.add(notification)
        
        db.session.commit()
        return jsonify({'success': True, 'message': '财务核销完成'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/scraps/disposal_list')
@login_required
def scrap_disposal_list():
    """报废处置列表(管理员)"""
    if current_user.role != 'admin':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    status_filter = request.args.get('status', 'approved')
    
    # 构建查询
    query = EquipmentScrap.query
    
    if status_filter == 'approved':
        # 已批准待处置
        query = query.filter_by(status='approved')
    elif status_filter == 'disposed':
        # 已处置待核销
        query = query.filter_by(status='disposed', financial_cleared=False)
    elif status_filter == 'cleared':
        # 已核销
        query = query.filter_by(financial_cleared=True)
    elif status_filter == 'all':
        # 所有已批准及之后的状态
        query = query.filter(EquipmentScrap.status.in_(['approved', 'disposed']))
    
    scraps = query.order_by(EquipmentScrap.created_date.desc()).all()
    
    # 统计
    stats = {
        'pending_disposal': EquipmentScrap.query.filter_by(status='approved').count(),
        'pending_clear': EquipmentScrap.query.filter_by(status='disposed', financial_cleared=False).count(),
        'cleared': EquipmentScrap.query.filter_by(financial_cleared=True).count()
    }
    
    return render_template('main/scrap_disposal_list.html',
                         title='报废处置管理',
                         scraps=scraps,
                         stats=stats,
                         status_filter=status_filter)
