"""
库存预警服务
处理库存监控、预警规则、采购建议
"""
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models import InventoryWarning, SparePart, Notification, Equipment
from app import get_beijing_now


class InventoryService:
    """库存管理和预警"""
    
    @staticmethod
    def get_warning_status():
        """获取所有库存预警状态"""
        warnings = InventoryWarning.query.filter_by(enabled=True).all()
        
        status_data = {
            'critical': [],
            'warning': [],
            'normal': [],
            'overstock': []
        }
        
        for warning in warnings:
            spare_part = warning.spare_part
            if not spare_part:
                continue
            
            item_info = {
                'id': spare_part.id,
                'name': spare_part.name,
                'current_stock': spare_part.stock_quantity,
                'min_threshold': warning.min_threshold,
                'critical_threshold': warning.critical_threshold,
                'reorder_quantity': warning.reorder_quantity,
                'last_updated': spare_part.purchase_date
            }
            
            if spare_part.stock_quantity <= warning.critical_threshold:
                status_data['critical'].append(item_info)
            elif spare_part.stock_quantity <= warning.min_threshold:
                status_data['warning'].append(item_info)
            elif spare_part.stock_quantity > spare_part.min_stock_level * 3:
                status_data['overstock'].append(item_info)
            else:
                status_data['normal'].append(item_info)
        
        return status_data
    
    @staticmethod
    def check_and_alert():
        """检查库存并发送预警"""
        warnings = InventoryWarning.query.filter_by(enabled=True).all()
        alerts_created = 0
        
        for warning in warnings:
            spare_part = warning.spare_part
            if not spare_part:
                continue
            
            # 检查是否需要发送紧急预警
            if spare_part.stock_quantity <= warning.critical_threshold:
                # 检查是否在最近 6 小时内已发送预警
                if not warning.last_warned_date or \
                   (get_beijing_now() - warning.last_warned_date).total_seconds() > 21600:
                    
                    # 发送通知给所有管理员
                    from app.models import User
                    admins = User.query.filter_by(role='admin').all()
                    
                    for admin in admins:
                        notification = Notification(
                            user_id=admin.id,
                            title=f'配件库存紧急预警',
                            message=f'配件《{spare_part.name}》库存已低于紧急值 ({spare_part.stock_quantity}/{warning.critical_threshold})，建议立即采购 {warning.reorder_quantity} 件',
                            order_type='inventory_warning',
                            order_id=spare_part.id
                        )
                        db.session.add(notification)
                    
                    warning.last_warned_date = get_beijing_now()
                    alerts_created += 1
        
        db.session.commit()
        return alerts_created
    
    @staticmethod
    def get_procurement_suggestion():
        """获取采购建议"""
        warnings = InventoryWarning.query.filter_by(enabled=True).all()
        suggestions = []
        
        for warning in warnings:
            spare_part = warning.spare_part
            if not spare_part:
                continue
            
            if spare_part.stock_quantity <= warning.min_threshold:
                shortage = warning.reorder_quantity - (spare_part.stock_quantity - warning.min_threshold)
                
                suggestions.append({
                    'spare_part_id': spare_part.id,
                    'part_name': spare_part.name,
                    'part_number': spare_part.part_number,
                    'current_stock': spare_part.stock_quantity,
                    'min_threshold': warning.min_threshold,
                    'suggested_quantity': warning.reorder_quantity,
                    'unit_price': spare_part.price,
                    'total_estimated_cost': warning.reorder_quantity * spare_part.price,
                    'supplier': spare_part.location,  # 这里可以改为供应商字段
                    'lead_time_days': warning.lead_time_days,
                    'urgency': 'CRITICAL' if spare_part.stock_quantity <= warning.critical_threshold else 'HIGH'
                })
        
        # 按紧急程度排序
        suggestions.sort(key=lambda x: (x['urgency'] != 'CRITICAL', -x['total_estimated_cost']))
        return suggestions
    
    @staticmethod
    def get_stock_turnover_rate(spare_part_id, days=30):
        """获取配件周转率"""
        from app.models import PartReplacement
        
        spare_part = SparePart.query.get(spare_part_id)
        if not spare_part:
            return None
        
        since_date = get_beijing_now() - timedelta(days=days)
        replacements = PartReplacement.query.filter(
            PartReplacement.spare_part_id == spare_part_id,
            PartReplacement.replacement_date >= since_date
        ).count()
        
        turnover_rate = replacements / (days / 7) if days > 0 else 0  # 每周周转次数
        
        return {
            'spare_part_id': spare_part_id,
            'spare_part_name': spare_part.name,
            'replacements_count': replacements,
            'period_days': days,
            'turnover_rate': round(turnover_rate, 2),
            'average_usage_per_day': round(replacements / days, 2) if days > 0 else 0
        }
    
    @staticmethod
    def update_warning_rule(spare_part_id, min_threshold=None, critical_threshold=None,
                           reorder_quantity=None, lead_time_days=None):
        """更新库存预警规则"""
        warning = InventoryWarning.query.filter_by(spare_part_id=spare_part_id).first()
        
        if not warning:
            warning = InventoryWarning(spare_part_id=spare_part_id)
            db.session.add(warning)
        
        if min_threshold is not None:
            warning.min_threshold = min_threshold
        if critical_threshold is not None:
            warning.critical_threshold = critical_threshold
        if reorder_quantity is not None:
            warning.reorder_quantity = reorder_quantity
        if lead_time_days is not None:
            warning.lead_time_days = lead_time_days
        
        db.session.commit()
        return warning
    
    @staticmethod
    def get_inventory_summary():
        """获取库存概览"""
        total_parts = SparePart.query.count()
        total_value = db.session.query(
            func.sum(SparePart.price * SparePart.stock_quantity)
        ).scalar() or 0
        
        critical_count = db.session.query(func.count()).select_from(
            InventoryWarning
        ).filter(
            InventoryWarning.enabled == True
        ).scalar() or 0
        
        # 设备统计：按 Equipment 表统计数量与总价值（按 price 字段）
        total_equipment = Equipment.query.count()
        total_equipment_value = db.session.query(func.sum(func.coalesce(Equipment.price, 0))).scalar() or 0

        return {
            'total_parts': total_parts,
            'total_inventory_value': total_value,
            'critical_warnings': critical_count,
            'status_breakdown': InventoryService.get_warning_status(),
            'total_equipment': total_equipment,
            'total_equipment_value': total_equipment_value
        }
