"""
资产生命周期模块路由
"""
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Equipment, AssetLifecycle
"""
延迟按需导入 LifecycleService，避免在模块导入时发生异常阻塞蓝图注册。
"""
from app.main import bp
from types import SimpleNamespace
from datetime import datetime


@bp.route('/asset/<int:asset_id>/lifecycle')
@login_required
def asset_lifecycle(asset_id):
    """兼容旧端点：将 asset_id 参数重定向到 equipment_id"""
    return redirect(url_for('main.asset_lifecycle_detail', equipment_id=asset_id))


@bp.route('/asset/<int:equipment_id>/lifecycle-detail')
@login_required
def asset_lifecycle_detail(equipment_id):
    """查看资产生命周期"""
    equipment = Equipment.query.get_or_404(equipment_id)
    
    from app.services import LifecycleService
    from app.models import AssetLifecycle

    timeline = LifecycleService.get_asset_timeline(equipment_id)
    age_info = LifecycleService.get_asset_age(equipment_id)
    lifecycle_cost = LifecycleService.get_lifecycle_cost_summary(equipment_id)
    retirement_recommendation = LifecycleService.recommend_retirement(equipment_id)
    
    # 获取所有生命周期事件
    events = AssetLifecycle.query.filter_by(equipment_id=equipment_id).order_by(AssetLifecycle.event_date.desc()).all()
    
    # 按事件类型统计
    event_type_stats = {}
    for event in events:
        event_type = event.event_type or 'other'
        if event_type not in event_type_stats:
            event_type_stats[event_type] = {'count': 0, 'total_cost': 0}
        event_type_stats[event_type]['count'] += 1
        event_type_stats[event_type]['total_cost'] += (event.cost_involved or 0)
    
    # 提取总成本
    total_lifecycle_cost = lifecycle_cost.get('total_lifecycle_cost', 0)
    
    return render_template(
        'main/asset_lifecycle.html',
        title=f'{equipment.name} - 生命周期',
        equipment=equipment,
        timeline=timeline,
        age_info=age_info,
        lifecycle_cost=lifecycle_cost,
        total_lifecycle_cost=total_lifecycle_cost,
        events=events,
        event_type_stats=event_type_stats,
        retirement_recommendation=retirement_recommendation
    )


@bp.route('/asset/<int:equipment_id>/lifecycle/event/new', methods=['GET', 'POST'])
@login_required
def record_lifecycle_event(equipment_id):
    """记录资产生命周期事件"""
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限执行此操作', 'danger')
        return redirect(url_for('main.index'))
    
    equipment = Equipment.query.get_or_404(equipment_id)
    
    if request.method == 'POST':
        event_type = request.form.get('event_type')
        new_status = request.form.get('new_status')
        old_status = equipment.status
        description = request.form.get('description', '')
        cost = request.form.get('cost', type=float, default=0)
        documents = request.form.get('documents', '')
        
        try:
            from app.services import LifecycleService

            event = LifecycleService.record_event(
                equipment_id=equipment_id,
                event_type=event_type,
                new_status=new_status,
                old_status=old_status,
                user_id=current_user.id,
                description=description,
                cost=cost,
                documents=documents
            )
            
            # 更新设备状态
            equipment.status = new_status
            db.session.commit()
            
            flash('生命周期事件已记录', 'success')
            return redirect(url_for('main.asset_lifecycle', equipment_id=equipment_id))
        except Exception as e:
            flash(f'记录失败: {str(e)}', 'danger')
    
    from app.services import LifecycleService

    return render_template(
        'main/record_lifecycle_event.html',
        title=f'记录 {equipment.name} 事件',
        equipment=equipment,
        event_types=LifecycleService.EVENT_TYPES
    )


@bp.route('/asset/lifecycle/dashboard')
@login_required
def lifecycle_dashboard():
    """资产生命周期仪表板"""
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    from app.services import LifecycleService

    dashboard_stats = LifecycleService.get_lifecycle_dashboard()

    # 准备模板需要的聚合字段（兼容老模板字段名）
    all_equipment = Equipment.query.all()

    # 计算年限分布统计
    age_distribution = {'0-2': 0, '2-5': 0, '5-7': 0, '7+': 0}
    aging_assets_list = []
    recent_events = []

    total_purchase_acc = 0.0
    total_maintenance_acc = 0.0
    total_upgrade_acc = 0.0
    counted_assets = 0

    candidates = []
    retired_count = 0

    for equipment in all_equipment:
        # 统计已报废数量
        if getattr(equipment, 'status', '') == 'retired':
            retired_count += 1

        age_info = LifecycleService.get_asset_age(equipment.id)
        if not age_info:
            continue

        age_years = age_info.get('age_years', 0)
        if age_years < 2:
            age_distribution['0-2'] += 1
        elif age_years < 5:
            age_distribution['2-5'] += 1
        elif age_years < 7:
            age_distribution['5-7'] += 1
        else:
            age_distribution['7+'] += 1

        # 维护老化资产列表（供模板展示）
        if age_years >= 5:
            # 尝试从 AssetCost 获取采购价格（容错），回退到 Equipment.price
            from app.models import AssetCost
            cost = AssetCost.query.filter_by(equipment_id=equipment.id).first()
            purchase_price = float(cost.purchase_price) if cost and cost.purchase_price else float(getattr(equipment, 'price', 0) or 0)
            aging_assets_list.append({
                'asset_no': equipment.id,
                'equipment_name': equipment.name,
                'usage_years': int(age_years),
                'purchase_price': purchase_price
            })

        # 计算生命周期成本汇总（用于平均值）
        lifecycle_cost = LifecycleService.get_lifecycle_cost_summary(equipment.id)
        cb = lifecycle_cost.get('cost_breakdown', {})
        purchase_part = 0.0
        maintenance_part = cb.get('maintenance', 0) if cb else 0
        upgrade_part = cb.get('upgrade', 0) if cb else 0
        # 这里无法可靠区分 purchase 成本（可能来自 AssetCost），尝试读取 AssetCost
        try:
            from app.models import AssetCost
            ac = AssetCost.query.filter_by(equipment_id=equipment.id).first()
            if ac and ac.purchase_price:
                purchase_part = float(ac.purchase_price or 0)
            else:
                purchase_part = float(getattr(equipment, 'price', 0) or 0)
        except Exception:
            purchase_part = float(getattr(equipment, 'price', 0) or 0)

        total_purchase_acc += purchase_part
        total_maintenance_acc += float(maintenance_part or 0)
        total_upgrade_acc += float(upgrade_part or 0)
        counted_assets += 1

        # 最近事件：取每台设备最后一条事件
        last_event = AssetLifecycle.query.filter_by(equipment_id=equipment.id).order_by(AssetLifecycle.event_date.desc()).first()
        if last_event:
            recent_events.append({
                'equipment_name': equipment.name,
                'event_type': last_event.event_type,
                'description': last_event.description,
                'event_date': last_event.event_date,
                'cost': last_event.cost_involved
            })

        # 报废候选：使用推荐函数
        rec = LifecycleService.recommend_retirement(equipment.id)
        if rec and rec.get('should_retire'):
            # 构建候选条目（模板期望字段）
            candidates.append({
                'asset_no': equipment.id,
                'equipment_id': equipment.id,
                'equipment_name': equipment.name,
                'usage_years': int(age_years),
                'maintenance_cost_ratio': 0.0,  # 兼容占位，后续可计算
                'residual_value': 0.0,
                'risk_score': rec.get('risk_score', 0),
            })

    # 平均生命周期成本
    if counted_assets > 0:
        avg_purchase = total_purchase_acc / counted_assets
        avg_maintenance = total_maintenance_acc / counted_assets
        avg_upgrade = total_upgrade_acc / counted_assets
        avg_annual = (avg_purchase + avg_maintenance + avg_upgrade) / max(1, (1))
    else:
        avg_purchase = avg_maintenance = avg_upgrade = avg_annual = 0.0

    avg_lifecycle_cost = SimpleNamespace(
        purchase=avg_purchase,
        maintenance=avg_maintenance,
        upgrade=avg_upgrade,
        annual=avg_annual
    )

    lifecycle_dashboard_obj = SimpleNamespace(
        # 基本计数（兼容旧字段名）
        active_assets=dashboard_stats.get('total_assets', 0) - retired_count,
        aging_assets=dashboard_stats.get('aging_assets', 0),
        retirement_candidates=len(candidates),
        retired_assets=retired_count,
        # 详细统计
        age_distribution=age_distribution,
        avg_lifecycle_cost=avg_lifecycle_cost,
        candidates=candidates,
        # 模板中期待的可迭代列表
        aging_assets_list=aging_assets_list,
        recent_events=sorted(recent_events, key=lambda x: x['event_date'], reverse=True)[:30]
    )

    return render_template(
        'main/lifecycle_dashboard.html',
        title='资产生命周期管理',
        stats=dashboard_stats,
        lifecycle_dashboard=lifecycle_dashboard_obj,
        retirement_candidates=candidates
    )


@bp.route('/asset/lifecycle/retirement-analysis')
@login_required
def retirement_analysis():
    """资产报废分析"""
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    from app.services import LifecycleService

    all_equipment = Equipment.query.all()
    analysis_data = []
    
    for equipment in all_equipment:
        recommendation = LifecycleService.recommend_retirement(equipment.id)
        if recommendation:
            age_info = LifecycleService.get_asset_age(equipment.id)
            
            analysis_data.append({
                'equipment': equipment,
                'age_info': age_info,
                'recommendation': recommendation,
                'risk_score': recommendation['risk_score'],
                'reasons': recommendation['reasons']
            })
    
    # 按风险分数排序
    analysis_data.sort(key=lambda x: x['risk_score'], reverse=True)
    
    return render_template(
        'main/retirement_analysis.html',
        title='资产报废分析',
        analysis_data=analysis_data
    )


@bp.route('/api/asset/<int:equipment_id>/lifecycle/timeline')
@login_required
def api_asset_timeline(equipment_id):
    """API：获取资产时间线"""
    from app.services import LifecycleService

    timeline = LifecycleService.get_asset_timeline(equipment_id)
    return jsonify({'timeline': timeline})


@bp.route('/api/asset/<int:equipment_id>/retirement-recommendation')
@login_required
def api_retirement_recommendation(equipment_id):
    """API：获取资产报废建议"""
    from app.services import LifecycleService

    recommendation = LifecycleService.recommend_retirement(equipment_id)
    
    if recommendation:
        return jsonify(recommendation)
    
    return jsonify({'error': 'Not found'}), 404


@bp.route('/api/lifecycle/dashboard')
@login_required
def api_lifecycle_dashboard():
    """API：获取生命周期仪表板数据"""
    if current_user.role not in ['admin', 'technician']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    from app.services import LifecycleService

    stats = LifecycleService.get_lifecycle_dashboard()
    return jsonify(stats)
