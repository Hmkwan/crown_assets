"""
资产成本分析服务
处理资产购置成本、折旧、维修成本等计算
"""
from datetime import datetime, timedelta
from app import db
from app.models import AssetCost, Equipment, RepairOrder
from app import get_beijing_now
from sqlalchemy import func, extract


class CostService:
    """资产成本管理和分析"""
    
    @staticmethod
    def get_asset_current_value(equipment_id):
        """获取资产当前价值"""
        cost = AssetCost.query.filter_by(equipment_id=equipment_id).first()
        if not cost:
            return 0
        return cost.calculate_current_value()
    
    @staticmethod
    def get_asset_total_cost(equipment_id):
        """获取资产总投入成本"""
        cost = AssetCost.query.filter_by(equipment_id=equipment_id).first()
        if cost:
            return cost.calculate_total_cost()
        return 0
    
    @staticmethod
    def get_department_cost_analysis(department_id=None):
        """获取部门资产成本分析

        使用 AssetCost.purchase_price 优先，如果不存在则回退到 Equipment.price。
        使用 outerjoin 以确保没有 AssetCost 的设备也能被统计。
        """
        total_purchase_expr = func.sum(func.coalesce(AssetCost.purchase_price, Equipment.price)).label('total_purchase')
        total_maintenance_expr = func.sum(func.coalesce(AssetCost.maintenance_cost, 0)).label('total_maintenance')

        query = db.session.query(
            Equipment.department,
            func.count(Equipment.id).label('asset_count'),
            total_purchase_expr,
            total_maintenance_expr
        ).outerjoin(AssetCost, Equipment.id == AssetCost.equipment_id)

        if department_id:
            query = query.filter(Equipment.department_id == department_id)

        return query.group_by(Equipment.department).all()
    
    @staticmethod
    def get_depreciation_analysis(year=None):
        """获取折旧分析报告"""
        if not year:
            year = get_beijing_now().year
        
        depreciation_data = []

        # 优先基于 AssetCost 生成折旧数据（可按年份过滤）
        if year:
            try:
                costs = AssetCost.query.filter(extract('year', AssetCost.purchase_date) == year).all()
            except Exception:
                # 某些数据库后端可能不支持 extract，回退到在 Python 中过滤
                costs = [c for c in AssetCost.query.all() if getattr(c.purchase_date, 'year', None) == year]
        else:
            costs = AssetCost.query.all()
        for cost in costs:
            current_value = cost.calculate_current_value()
            original_value = cost.purchase_price or 0
            depreciation = original_value - current_value

            depreciation_data.append({
                'equipment_id': cost.equipment_id,
                'equipment_name': cost.equipment.name if cost.equipment else 'Unknown',
                'original_value': original_value,
                'current_value': current_value,
                'depreciation': depreciation,
                'depreciation_rate': (depreciation / original_value * 100) if original_value > 0 else 0,
                'purchase_date': cost.purchase_date,
                'lifespan_years': cost.expected_lifespan
            })

        # 对于没有 AssetCost 的设备，回退使用 Equipment.price 和 Equipment.purchase_date
        equipments_without_cost = Equipment.query.outerjoin(AssetCost, Equipment.id == AssetCost.equipment_id).filter(AssetCost.id == None).all()
        for eq in equipments_without_cost:
            # 如果指定了年份，只统计购买年份匹配的设备
            if year and getattr(eq, 'purchase_date', None):
                if getattr(eq.purchase_date, 'year', None) != year:
                    continue
            if year and not getattr(eq, 'purchase_date', None):
                # 没有 purchase_date，无法判定年份，跳过以避免误计
                continue
            original_value = float(eq.price or 0)
            purchase_date = getattr(eq, 'purchase_date', None)
            # 使用保守的默认寿命（5年）作为估算
            expected_lifespan = 5
            if not purchase_date or original_value == 0:
                # 无法估算折旧，跳过或返回当前价格作为 current_value
                current_value = original_value
                depreciation = original_value - current_value
                depreciation_rate = 0
            else:
                months_used = (get_beijing_now().date() - purchase_date).days / 30
                total_months = expected_lifespan * 12
                if months_used >= total_months:
                    current_value = 0
                else:
                    depreciation_amount = original_value * (months_used / total_months)
                    current_value = original_value - depreciation_amount
                depreciation = original_value - current_value
                depreciation_rate = (depreciation / original_value * 100) if original_value > 0 else 0

            depreciation_data.append({
                'equipment_id': eq.id,
                'equipment_name': eq.name,
                'original_value': original_value,
                'current_value': current_value,
                'depreciation': depreciation,
                'depreciation_rate': depreciation_rate,
                'purchase_date': purchase_date,
                'lifespan_years': expected_lifespan
            })

        return depreciation_data
    
    @staticmethod
    def get_cost_by_asset_type():
        """按资产类型统计成本"""
        total_purchase_expr = func.sum(func.coalesce(AssetCost.purchase_price, Equipment.price)).label('total_purchase')
        avg_price_expr = func.avg(func.coalesce(AssetCost.purchase_price, Equipment.price)).label('avg_price')

        result = db.session.query(
            Equipment.type,
            func.count(Equipment.id).label('count'),
            total_purchase_expr,
            avg_price_expr
        ).outerjoin(AssetCost, Equipment.id == AssetCost.equipment_id).group_by(Equipment.type).all()

        return result

    @staticmethod
    def get_annual_summary(years):
        """按年份返回年度汇总统计：每年采购总额、当前价值、累计折旧和资产数量"""
        summaries = []

        # 预拉取没有 AssetCost 的设备以便按年份判断
        equipments_without_cost = Equipment.query.outerjoin(AssetCost, Equipment.id == AssetCost.equipment_id).filter(AssetCost.id == None).all()

        for y in years:
            total_purchase = 0.0
            total_current = 0.0
            count = 0

            # AssetCost 按购买年份聚合
            try:
                costs = AssetCost.query.filter(extract('year', AssetCost.purchase_date) == y).all()
            except Exception:
                costs = [c for c in AssetCost.query.all() if getattr(c.purchase_date, 'year', None) == y]

            for c in costs:
                original = float(c.purchase_price or 0)
                current = float(c.calculate_current_value() or 0)
                total_purchase += original
                total_current += current
                count += 1

            # 没有 AssetCost 的设备，使用 Equipment.purchase_date 判断年份
            for eq in equipments_without_cost:
                if not getattr(eq, 'purchase_date', None):
                    continue
                if getattr(eq.purchase_date, 'year', None) != y:
                    continue

                original = float(eq.price or 0)
                # 估算当前价值（使用与 get_depreciation_analysis 相同的逻辑）
                expected_lifespan = 5
                purchase_date = getattr(eq, 'purchase_date', None)
                if not purchase_date or original == 0:
                    current = original
                else:
                    months_used = (get_beijing_now().date() - purchase_date).days / 30
                    total_months = expected_lifespan * 12
                    if months_used >= total_months:
                        current = 0
                    else:
                        depreciation_amount = original * (months_used / total_months)
                        current = original - depreciation_amount

                total_purchase += original
                total_current += current
                count += 1

            total_depreciation = total_purchase - total_current

            summaries.append({
                'year': y,
                'asset_count': count,
                'total_purchase': total_purchase,
                'total_current_value': total_current,
                'total_depreciation': total_depreciation
            })

        return summaries
    
    @staticmethod
    def get_maintenance_cost_analysis(days=365):
        """获取维修成本分析"""
        from app.models import Department
        since_date = get_beijing_now() - timedelta(days=days)
        
        result = db.session.query(
            Equipment.id,
            Equipment.name,
            Equipment.type,
            func.count(RepairOrder.id).label('repair_count'),
            func.sum(AssetCost.maintenance_cost).label('total_maintenance'),
            Department.name.label('department_name'),
            Equipment.status
        ).outerjoin(RepairOrder, Equipment.id == RepairOrder.equipment_id).outerjoin(
            AssetCost, Equipment.id == AssetCost.equipment_id
        ).outerjoin(Department, Equipment.department_id == Department.id).filter(
            RepairOrder.created_date >= since_date if RepairOrder.created_date else True
        ).group_by(
            Equipment.id, Equipment.name, Equipment.type, 
            Department.name, Equipment.status
        ).all()
        
        return result
    
    @staticmethod
    def calculate_roi(equipment_id, years=None):
        """计算投资回报率（基于使用率和折旧）"""
        equipment = Equipment.query.get(equipment_id)
        cost = AssetCost.query.filter_by(equipment_id=equipment_id).first()
        
        if not equipment or not cost:
            return None
        
        if not years:
            years = cost.expected_lifespan
        
        total_cost = cost.calculate_total_cost()
        current_value = cost.calculate_current_value()
        
        # 简单 ROI = (原值 - 当前值) / 原值
        if cost.purchase_price > 0:
            roi = ((cost.purchase_price - current_value) / cost.purchase_price) * 100
        else:
            roi = 0
        
        return {
            'equipment_id': equipment_id,
            'total_investment': total_cost,
            'current_value': current_value,
            'depreciation': cost.purchase_price - current_value,
            'roi_percentage': roi,
            'yearly_cost': total_cost / years if years > 0 else 0
        }
    
    @staticmethod
    def add_cost_record(equipment_id, purchase_price=0, maintenance_cost=0, 
                       depreciation_rate=0.2, expected_lifespan=5, **kwargs):
        """添加资产成本记录"""
        existing = AssetCost.query.filter_by(equipment_id=equipment_id).first()
        
        if existing:
            existing.purchase_price = purchase_price
            existing.maintenance_cost = maintenance_cost
            existing.depreciation_rate = depreciation_rate
            existing.expected_lifespan = expected_lifespan
            for key, value in kwargs.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
        else:
            cost = AssetCost(
                equipment_id=equipment_id,
                purchase_price=purchase_price,
                maintenance_cost=maintenance_cost,
                depreciation_rate=depreciation_rate,
                expected_lifespan=expected_lifespan,
                **kwargs
            )
            db.session.add(cost)
        
        db.session.commit()
        return existing or cost
