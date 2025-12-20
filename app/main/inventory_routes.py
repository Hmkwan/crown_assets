"""
库存预警模块路由
"""
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import InventoryWarning, SparePart
"""
Note: Import services lazily inside view functions to avoid import-time
errors that can prevent blueprint registration during app startup.
"""
from app.main import bp


@bp.route('/inventory-warnings')
@login_required
def inventory_warning():
    """兼容旧端点：将旧的 `inventory_warning` 重定向到新的 `inventory_warnings` 页面。"""
    return redirect(url_for('main.inventory_warnings', **request.args))


@bp.route('/inventory/warnings')
@login_required
def inventory_warnings():
    """库存预警仪表板"""
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    # 延迟导入服务，避免在模块导入期触发错误
    from app.services import InventoryService

    # 获取库存状态
    warning_status = InventoryService.get_warning_status()
    procurement_suggestions = InventoryService.get_procurement_suggestion()
    inventory_summary = InventoryService.get_inventory_summary()
    
    return render_template(
        'main/inventory_warnings.html',
        title='库存预警管理',
        warning_status=warning_status,
        procurement_suggestions=procurement_suggestions,
        inventory_summary=inventory_summary
    )


@bp.route('/inventory/procurement-plan')
@login_required
def procurement_plan():
    """采购计划建议"""
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    from app.services import InventoryService

    suggestions = InventoryService.get_procurement_suggestion()

    # 将 suggestions 分组为 critical / warning / normal，便于模板渲染
    procurement_plan = {
        'critical': [s for s in suggestions if s.get('urgency') == 'CRITICAL'],
        'warning': [s for s in suggestions if s.get('urgency') == 'HIGH'],
        'normal': [s for s in suggestions if s.get('urgency') not in ('CRITICAL', 'HIGH')]
    }

    total_procurement_cost = sum(item.get('total_estimated_cost', 0) for item in suggestions)

    procurement_summary = {
        'total_cost': total_procurement_cost,
        'item_count': len(suggestions)
    }

    return render_template(
        'main/procurement_plan.html',
        title='采购建议',
        procurement_plan=procurement_plan,
        procurement_summary=procurement_summary
    )


@bp.route('/spare-part/<int:spare_part_id>/warning', methods=['GET', 'POST'])
@login_required
def manage_inventory_warning(spare_part_id):
    """管理配件库存预警规则"""
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限执行此操作', 'danger')
        return redirect(url_for('main.index'))
    
    spare_part = SparePart.query.get_or_404(spare_part_id)
    warning = InventoryWarning.query.filter_by(spare_part_id=spare_part_id).first()
    
    if request.method == 'POST':
        min_threshold = request.form.get('min_threshold', type=int, default=10)
        critical_threshold = request.form.get('critical_threshold', type=int, default=5)
        reorder_quantity = request.form.get('reorder_quantity', type=int, default=20)
        lead_time_days = request.form.get('lead_time_days', type=int, default=7)
        enabled = request.form.get('enabled') == 'on'
        try:
            from app.services import InventoryService

            InventoryService.update_warning_rule(
                spare_part_id=spare_part_id,
                min_threshold=min_threshold,
                critical_threshold=critical_threshold,
                reorder_quantity=reorder_quantity,
                lead_time_days=lead_time_days
            )

            if warning:
                warning.enabled = enabled
                db.session.commit()

            flash('库存预警规则已更新', 'success')
            return redirect(url_for('main.inventory_warnings'))
        except Exception as e:
            flash(f'更新失败: {str(e)}', 'danger')
    
    from app.services import InventoryService

    # 获取配件的使用统计
    turnover_rate = InventoryService.get_stock_turnover_rate(spare_part_id)
    
    return render_template(
        'main/edit_inventory_warning.html',
        title=f'配置 {spare_part.name} 预警规则',
        spare_part=spare_part,
        warning=warning,
        turnover_rate=turnover_rate
    )


@bp.route('/api/inventory/status')
@login_required
def api_inventory_status():
    """API：获取库存状态"""
    if current_user.role not in ['admin', 'technician']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    from app.services import InventoryService

    status = InventoryService.get_warning_status()
    
    return jsonify({
        'critical_count': len(status['critical']),
        'warning_count': len(status['warning']),
        'normal_count': len(status['normal']),
        'overstock_count': len(status['overstock']),
        'items': {
            'critical': status['critical'][:10],
            'warning': status['warning'][:10]
        }
    })


@bp.route('/api/inventory/check-alerts')
@login_required
def api_check_alerts():
    """API：检查并创建库存预警"""
    if current_user.role not in ['admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    from app.services import InventoryService

    alerts_created = InventoryService.check_and_alert()
    
    return jsonify({
        'alerts_created': alerts_created,
        'message': f'已检查库存，创建 {alerts_created} 条预警'
    })


@bp.route('/spare-part/<int:spare_part_id>/turnover')
@login_required
def spare_part_turnover(spare_part_id):
    """查看配件周转率"""
    spare_part = SparePart.query.get_or_404(spare_part_id)
    
    days = request.args.get('days', 30, type=int)
    from app.services import InventoryService

    turnover_rate = InventoryService.get_stock_turnover_rate(spare_part_id, days)
    
    return render_template(
        'main/spare_part_turnover.html',
        title=f'{spare_part.name} - 周转分析',
        spare_part=spare_part,
        turnover_rate=turnover_rate,
        days=days
    )
