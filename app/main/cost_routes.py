"""
成本分析模块路由
"""
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Equipment, AssetCost, Department
"""
延迟按需导入 CostService，避免在模块导入时抛出异常导致蓝图未注册。
"""
from app.main import bp
from sqlalchemy import func
from app import get_beijing_now


@bp.route('/cost-analysis')
@login_required
def cost_analysis():
    """兼容旧端点：将旧的 `cost_analysis` 重定向到新的 `cost_analysis_report` 页面。"""
    # 将查询参数保留并重定向到新的报告视图
    return redirect(url_for('main.cost_analysis_report', **request.args))


@bp.route('/reports/cost-analysis')
@login_required
def cost_analysis_report():
    """资产成本分析仪表板（来自服务）"""
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    # 延迟导入服务
    from app.services import CostService

    # 年份筛选（可选）
    selected_year = request.args.get('year', type=int)

    # 获取成本数据
    depreciation_data = CostService.get_depreciation_analysis(year=selected_year)
    cost_by_type = CostService.get_cost_by_asset_type()
    maintenance_costs = CostService.get_maintenance_cost_analysis()
    
    # 计算统计数据
    total_purchase = sum(item.get('total_purchase', 0) for item in depreciation_data)
    total_current_value = sum(item.get('current_value', 0) for item in depreciation_data)
    total_depreciation = total_purchase - total_current_value

    # 将配件库存价值计入总体库存/采购统计（配件按库存数量乘以单价）
    from app.models import SparePart
    spare_parts_value = db.session.query(func.sum(SparePart.price * SparePart.stock_quantity)).scalar() or 0

    # 把配件总价值计入总采购与当前价值（配件通常不折旧）
    total_purchase += float(spare_parts_value)
    total_current_value += float(spare_parts_value)
    total_depreciation = total_purchase - total_current_value
    
    departments = Department.query.all()
    selected_department = request.args.get('department', type=int)
    # 生成最近若干年份供下拉选择（默认 0-10 年）
    current_year = get_beijing_now().year
    years = list(range(current_year, current_year - 11, -1))
    
    if selected_department:
        dept_costs = CostService.get_department_cost_analysis(selected_department)
    else:
        dept_costs = CostService.get_department_cost_analysis()
    # 年度汇总统计（用于表格或图表展示）
    annual_summary = CostService.get_annual_summary(years)
    
    return render_template(
        'main/cost_analysis.html',
        title='资产成本分析',
        depreciation_data=depreciation_data,
        selected_year=selected_year,
        years=years,
        cost_by_type=cost_by_type,
        maintenance_costs=maintenance_costs,
        total_purchase=total_purchase,
        total_current_value=total_current_value,
        total_depreciation=total_depreciation,
        departments=departments,
        selected_department=selected_department,
        dept_costs=dept_costs,
        annual_summary=annual_summary
    )


@bp.route('/asset/<int:equipment_id>/cost')
@login_required
def asset_cost_detail(equipment_id):
    """查看单个资产的成本详情"""
    equipment = Equipment.query.get_or_404(equipment_id)
    cost = AssetCost.query.filter_by(equipment_id=equipment_id).first()
    
    if not cost:
        flash('此资产暂无成本记录', 'warning')
        cost = AssetCost(equipment_id=equipment_id)
    
    from app.services import CostService
    from datetime import datetime

    roi = CostService.calculate_roi(equipment_id)
    
    # 计算生命周期成本
    lifecycle_costs = {
        'purchase_price': cost.purchase_price or 0,
        'maintenance_cost': cost.maintenance_cost or 0,
        'upgrade_cost': 0,  # AssetCost 模型暂无此字段
        'other_cost': 0,  # AssetCost 模型暂无此字段
        'total_cost': (cost.purchase_price or 0) + (cost.maintenance_cost or 0)
    }
    
    # 计算当前净值
    current_value = cost.calculate_current_value() if cost.id else (cost.purchase_price or 0)
    
    return render_template(
        'main/asset_cost_detail.html',
        title=f'{equipment.name} - 成本详情',
        equipment=equipment,
        cost=cost,
        roi=roi,
        lifecycle_costs=lifecycle_costs,
        current_value=current_value
    )


@bp.route('/asset/<int:equipment_id>/cost/edit', methods=['GET', 'POST'])
@login_required
def edit_asset_cost(equipment_id):
    """编辑资产成本"""
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限执行此操作', 'danger')
        return redirect(url_for('main.index'))
    
    equipment = Equipment.query.get_or_404(equipment_id)
    
    if request.method == 'POST':
        purchase_price = request.form.get('purchase_price', type=float, default=0)
        maintenance_cost = request.form.get('maintenance_cost', type=float, default=0)
        # 表单传入百分比值(0-100)，需转换为小数(0-1)
        depreciation_rate_percent = request.form.get('depreciation_rate', type=float, default=15)
        depreciation_rate = depreciation_rate_percent / 100.0
        expected_lifespan = request.form.get('expected_lifespan', type=int, default=5)
        supplier = request.form.get('supplier', '')
        warranty_period = request.form.get('warranty_period', type=int, default=0)
        purchase_date_raw = (request.form.get('purchase_date') or '').strip()
        purchase_date = None
        if purchase_date_raw:
            from datetime import datetime
            try:
                purchase_date = datetime.strptime(purchase_date_raw, '%Y-%m-%d').date()
            except Exception:
                purchase_date = None
        
        try:
            from app.services import CostService

            CostService.add_cost_record(
                equipment_id=equipment_id,
                purchase_price=purchase_price,
                maintenance_cost=maintenance_cost,
                depreciation_rate=depreciation_rate,
                expected_lifespan=expected_lifespan,
                supplier=supplier,
                warranty_period=warranty_period if warranty_period > 0 else None,
                purchase_date=purchase_date
            )
            flash('资产成本信息已更新', 'success')
            return redirect(url_for('main.asset_cost_detail', equipment_id=equipment_id))
        except Exception as e:
            flash(f'更新失败: {str(e)}', 'danger')
    
    cost = AssetCost.query.filter_by(equipment_id=equipment_id).first()
    
    return render_template(
        'main/edit_asset_cost.html',
        title=f'编辑 {equipment.name} 成本',
        equipment=equipment,
        cost=cost
    )


@bp.route('/api/cost/department/<int:department_id>')
@login_required
def api_department_cost(department_id):
    """API：获取部门成本数据"""
    if current_user.role not in ['admin', 'technician']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    from app.services import CostService

    costs = CostService.get_department_cost_analysis(department_id)
    
    data = {
        'department': costs[0][0] if costs else 'Unknown',
        'asset_count': costs[0][1] if costs else 0,
        'total_purchase': float(costs[0][2] or 0) if costs else 0,
        'total_maintenance': float(costs[0][3] or 0) if costs else 0
    }
    
    return jsonify(data)


@bp.route('/api/cost/roi/<int:equipment_id>')
@login_required
def api_equipment_roi(equipment_id):
    """API：获取单个设备ROI数据"""
    from app.services import CostService

    roi = CostService.calculate_roi(equipment_id)
    
    if roi:
        roi['current_value'] = float(roi['current_value'])
        roi['total_investment'] = float(roi['total_investment'])
        roi['depreciation'] = float(roi['depreciation'])
        roi['yearly_cost'] = float(roi['yearly_cost'])
        return jsonify(roi)
    
    return jsonify({'error': 'Not found'}), 404
