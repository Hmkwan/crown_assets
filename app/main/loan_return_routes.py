"""
设备借用归还验收相关路由
"""
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import EquipmentLoan, Equipment, User, Notification, RepairOrder
from app.main import bp
from datetime import datetime


def get_beijing_now():
    """获取北京时间"""
    from datetime import timezone, timedelta
    beijing_tz = timezone(timedelta(hours=8))
    return datetime.now(beijing_tz).replace(tzinfo=None)


@bp.route('/loans/<int:id>/request_return', methods=['GET', 'POST'])
@login_required
def request_loan_return(id):
    """发起归还申请"""
    loan = EquipmentLoan.query.get_or_404(id)
    
    if loan.requester_id != current_user.id and current_user.role not in ['admin', 'super_admin']:
        flash('您没有权限操作此借用记录', 'danger')
        return redirect(url_for('main.my_loans'))
    
    if loan.status not in ['approved', 'borrowed']:
        flash('只能归还已批准或已借出的设备', 'warning')
        return redirect(url_for('main.my_loans'))
    
    if request.method == 'POST':
        try:
            equipment = loan.equipment
            return_notes = request.form.get('return_notes', '')
            return_condition = request.form.get('return_condition', 'good')
            
            # 判断是否需要验收
            require_inspection = equipment and (equipment.require_return_inspection or (equipment.price and equipment.price > 5000))
            
            if require_inspection:
                loan.status = 'return_pending'
                loan.return_request_date = get_beijing_now()
                loan.return_notes = return_notes
                loan.return_condition = return_condition
                
                admins = User.query.filter(User.role.in_(['admin', 'super_admin'])).all()
                for admin in admins:
                    notification = Notification(
                        user_id=admin.id,
                        title='设备待验收',
                        message=f'用户 {current_user.username} 申请归还设备: {equipment.name} (借用ID:{loan.id})',
                        order_type='equipment_loan',
                        order_id=loan.id
                    )
                    db.session.add(notification)
                
                flash_msg = '归还申请已提交,请等待管理员验收'
                current_app.logger.info(f'用户 {current_user.username} 申请归还设备 (借用ID:{loan.id}), 等待验收')
            else:
                loan.status = 'returned'
                loan.return_request_date = get_beijing_now()
                loan.returned_date = get_beijing_now()
                loan.return_notes = return_notes
                loan.return_condition = return_condition
                if equipment:
                    equipment.status = 'available'
                flash_msg = '设备归还成功'
                current_app.logger.info(f'用户 {current_user.username} 快速归还设备 (借用ID:{loan.id})')
            
            db.session.commit()
            flash(flash_msg, 'success')
            return redirect(url_for('main.my_loans'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'归还申请失败: {e}', exc_info=True)
            flash('操作失败,请联系管理员', 'danger')
    
    return render_template('main/request_loan_return.html', loan=loan, title='申请归还', now=datetime.now)


@bp.route('/loans/<int:id>/inspect', methods=['GET', 'POST'])
@login_required
def inspect_loan_return(id):
    """验收归还设备"""
    if current_user.role not in ['admin', 'super_admin']:
        flash('只有管理员可以验收设备', 'danger')
        return redirect(url_for('main.index'))
    
    loan = EquipmentLoan.query.get_or_404(id)
    if loan.status != 'return_pending':
        flash('该借用记录不在待验收状态', 'warning')
        return redirect(url_for('main.loans_return_pending'))
    
    if request.method == 'POST':
        try:
            inspection_result = request.form.get('inspection_result')
            inspection_notes = request.form.get('inspection_notes', '')
            equipment = loan.equipment
            
            loan.inspected_by = current_user.id
            loan.inspection_date = get_beijing_now()
            loan.inspection_notes = inspection_notes
            loan.inspection_result = inspection_result
            
            if inspection_result == 'passed':
                loan.status = 'returned'
                loan.returned_date = get_beijing_now()
                if equipment:
                    equipment.status = 'available'
                flash_msg = '验收通过,设备已归还'
                current_app.logger.info(f'设备 {equipment.name if equipment else "未知"} 归还验收通过 (借用ID:{loan.id})')
                
            elif inspection_result == 'requires_repair':
                loan.status = 'returned'
                loan.returned_date = get_beijing_now()
                if equipment:
                    equipment.status = 'repair'
                    repair_order = RepairOrder(
                        equipment_id=equipment.id,
                        requester_id=current_user.id,
                        description=f'设备借用归还验收发现问题: {inspection_notes}\n借用人: {loan.requester.username if loan.requester else "未知"}',
                        status='submitted'
                    )
                    db.session.add(repair_order)
                flash_msg = '设备需要维修,已自动创建维修工单'
                current_app.logger.info(f'设备 {equipment.name if equipment else "未知"} 归还需维修 (借用ID:{loan.id}), 已创建维修工单')
                
            else:  # failed
                loan.status = 'returned'
                loan.returned_date = get_beijing_now()
                loan.damage_compensation = float(request.form.get('damage_compensation', 0))
                loan.damage_description = request.form.get('damage_description', '')
                if equipment:
                    equipment.status = 'repair'
                    
                if loan.requester:
                    notification = Notification(
                        user_id=loan.requester_id,
                        title='设备验收未通过',
                        message=f'您归还的设备 {equipment.name if equipment else "未知设备"} 验收未通过, 需赔偿 ¥{loan.damage_compensation}',
                        order_type='equipment_loan',
                        order_id=loan.id
                    )
                    db.session.add(notification)
                    
                flash_msg = f'验收未通过,已记录赔偿金额 ¥{loan.damage_compensation}'
                current_app.logger.warning(f'设备 {equipment.name if equipment else "未知"} 归还验收未通过 (借用ID:{loan.id}), 赔偿:{loan.damage_compensation}')
            
            # 通知借用人验收结果
            if loan.requester:
                result_map = {'passed': '通过', 'requires_repair': '需维修', 'failed': '未通过'}
                notification = Notification(
                    user_id=loan.requester_id,
                    title='设备归还验收完成',
                    message=f'您归还的设备 {equipment.name if equipment else "未知设备"} 已验收完成, 结果: {result_map.get(inspection_result, inspection_result)}',
                    order_type='equipment_loan',
                    order_id=loan.id
                )
                db.session.add(notification)
            
            db.session.commit()
            flash(flash_msg, 'success')
            return redirect(url_for('main.loans_return_pending'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'验收失败: {e}', exc_info=True)
            flash('验收失败,请联系管理员', 'danger')
    
    return render_template('main/inspect_loan_return.html', loan=loan, title='验收归还')


@bp.route('/loans/return-pending')
@login_required
def loans_return_pending():
    """待验收的归还申请列表"""
    if current_user.role not in ['admin', 'super_admin']:
        flash('只有管理员可以查看此页面', 'danger')
        return redirect(url_for('main.index'))
    
    pending_loans = EquipmentLoan.query.filter_by(status='return_pending').order_by(
        EquipmentLoan.return_request_date.desc()
    ).all()
    
    return render_template('main/loans_return_pending.html', 
                         pending_loans=pending_loans,
                         title='待验收归还')
