"""
资产生命周期管理服务
处理资产从购置到报废的全生命周期
"""
from datetime import datetime
from app import db
from app.models import AssetLifecycle, Equipment, UserActivityLog
from app import get_beijing_now


class LifecycleService:
    """资产生命周期管理"""
    
    # 生命周期事件类型定义
    EVENT_TYPES = {
        'purchase': '采购',
        'deployment': '部署',
        'maintenance': '维护',
        'upgrade': '升级',
        'transfer': '调拨',
        'retirement': '报废'
    }
    
    @staticmethod
    def record_event(equipment_id, event_type, new_status, old_status=None, 
                    user_id=None, description='', cost=0, documents=''):
        """记录资产生命周期事件"""
        event = AssetLifecycle(
            equipment_id=equipment_id,
            event_type=event_type,
            new_status=new_status,
            old_status=old_status,
            responsible_user_id=user_id,
            description=description,
            cost_involved=cost,
            documents=documents,
            event_date=get_beijing_now()
        )
        db.session.add(event)
        db.session.commit()
        return event
    
    @staticmethod
    def get_asset_timeline(equipment_id):
        """获取资产完整生命周期时间线"""
        events = AssetLifecycle.query.filter_by(
            equipment_id=equipment_id
        ).order_by(AssetLifecycle.event_date).all()
        
        timeline = []
        for event in events:
            timeline.append({
                'date': event.event_date.strftime('%Y-%m-%d %H:%M:%S'),
                'event_type': LifecycleService.EVENT_TYPES.get(event.event_type, event.event_type),
                'old_status': event.old_status,
                'new_status': event.new_status,
                'description': event.description,
                'user': event.responsible_user.username if event.responsible_user else 'System',
                'cost': event.cost_involved
            })
        
        return timeline
    
    @staticmethod
    def get_asset_age(equipment_id):
        """获取资产年龄"""
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            return None
        
        # 查找采购事件
        purchase_event = AssetLifecycle.query.filter_by(
            equipment_id=equipment_id,
            event_type='purchase'
        ).order_by(AssetLifecycle.event_date).first()
        
        if purchase_event:
            pe = purchase_event.event_date
            # 如果 event_date 是 naive datetime，将其视为本地北京时间并设置时区
            if getattr(pe, 'tzinfo', None) is None:
                from datetime import timezone, timedelta
                pe = pe.replace(tzinfo=timezone(timedelta(hours=8)))
            age_days = (get_beijing_now() - pe).days
            age_years = age_days / 365.25
            return {
                'purchase_date': purchase_event.event_date,
                'age_days': age_days,
                'age_years': round(age_years, 1),
                'age_display': f"{int(age_years)} 年 {int((age_years % 1) * 12)} 月"
            }
        
        # 如果数据库中没有 lifecycle 的采购事件，回退到 Equipment.purchase_date 字段（如果存在）
        if getattr(equipment, 'purchase_date', None):
            try:
                pd = equipment.purchase_date
                # ensure pd is a datetime/date
                if hasattr(pd, 'year'):
                    age_days = (get_beijing_now().date() - pd if hasattr(pd, 'date') else get_beijing_now().date() - pd).days
                else:
                    # if purchase_date stored as string, try parse conservatively
                    from datetime import datetime
                    parsed = None
                    try:
                        parsed = datetime.strptime(str(pd), '%Y-%m-%d').date()
                    except Exception:
                        try:
                            parsed = datetime.fromisoformat(str(pd)).date()
                        except Exception:
                            parsed = None
                    if parsed:
                        age_days = (get_beijing_now().date() - parsed).days
                    else:
                        return None

            except Exception:
                return None

            age_years = age_days / 365.25
            return {
                'purchase_date': getattr(equipment, 'purchase_date', None),
                'age_days': age_days,
                'age_years': round(age_years, 1),
                'age_display': f"{int(age_years)} 年 {int((age_years % 1) * 12)} 月"
            }

        return None
    
    @staticmethod
    def get_maintenance_history(equipment_id):
        """获取资产维护历史"""
        maintenance_events = AssetLifecycle.query.filter_by(
            equipment_id=equipment_id,
            event_type='maintenance'
        ).order_by(AssetLifecycle.event_date.desc()).all()
        
        return [{
            'date': event.event_date.strftime('%Y-%m-%d'),
            'description': event.description,
            'cost': event.cost_involved,
            'performed_by': event.responsible_user.username if event.responsible_user else 'Unknown'
        } for event in maintenance_events]
    
    @staticmethod
    def get_lifecycle_cost_summary(equipment_id):
        """获取资产生命周期成本汇总"""
        events = AssetLifecycle.query.filter_by(equipment_id=equipment_id).all()
        
        total_cost = 0
        cost_breakdown = {
            'purchase': 0,
            'maintenance': 0,
            'upgrade': 0,
            'other': 0
        }
        
        for event in events:
            if event.cost_involved:
                total_cost += event.cost_involved
                event_type = event.event_type
                if event_type in cost_breakdown:
                    cost_breakdown[event_type] += event.cost_involved
                else:
                    cost_breakdown['other'] += event.cost_involved
        
        return {
            'equipment_id': equipment_id,
            'total_lifecycle_cost': total_cost,
            'cost_breakdown': cost_breakdown
        }
    
    @staticmethod
    def recommend_retirement(equipment_id):
        """推荐资产是否应该报废"""
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            return None
        
        from app.models import AssetCost
        cost = AssetCost.query.filter_by(equipment_id=equipment.id).first()
        
        age_info = LifecycleService.get_asset_age(equipment_id)
        lifecycle_cost = LifecycleService.get_lifecycle_cost_summary(equipment_id)
        
        reasons = []
        recommendation = {
            'should_retire': False,
            'reasons': reasons,
            'risk_score': 0
        }
        
        # 超出预期使用年限
        if cost and age_info:
            if age_info['age_years'] > cost.expected_lifespan:
                reasons.append(f"已超出预期使用年限 ({age_info['age_years']:.1f} / {cost.expected_lifespan} 年)")
                recommendation['risk_score'] += 30
        
        # 生命周期成本超过购置成本
        if cost and lifecycle_cost['total_lifecycle_cost'] > cost.purchase_price * 1.5:
            reasons.append(f"维护成本高于购置成本 (成本比: {lifecycle_cost['total_lifecycle_cost'] / cost.purchase_price:.1f}x)")
            recommendation['risk_score'] += 25
        
        # 当前价值过低
        if cost:
            current_value = cost.calculate_current_value()
            if current_value < cost.purchase_price * 0.1:
                reasons.append(f"残值过低 (残值率: {current_value / cost.purchase_price * 100:.1f}%)")
                recommendation['risk_score'] += 25
        
        # 维修频率高
        maintenance_history = LifecycleService.get_maintenance_history(equipment_id)
        if age_info and len(maintenance_history) > age_info['age_years'] * 2:
            reasons.append(f"维修频繁 ({len(maintenance_history)} 次 / {age_info['age_years']:.1f} 年)")
            recommendation['risk_score'] += 20
        
        recommendation['should_retire'] = recommendation['risk_score'] >= 50
        
        return recommendation
    
    @staticmethod
    def get_lifecycle_dashboard():
        """获取生命周期仪表板统计"""
        from sqlalchemy import func
        
        all_equipment = Equipment.query.all()
        
        stats = {
            'total_assets': len(all_equipment),
            'new_assets': 0,      # < 1 年
            'mature_assets': 0,   # 1-5 年
            'aging_assets': 0,    # 5-10 年
            'retired_assets': 0,  # > 10 年或已报废
            'recommended_for_retirement': 0
        }
        
        for equipment in all_equipment:
            age_info = LifecycleService.get_asset_age(equipment.id)
            
            if not age_info:
                continue
            
            age_years = age_info['age_years']
            
            if age_years < 1:
                stats['new_assets'] += 1
            elif age_years < 5:
                stats['mature_assets'] += 1
            elif age_years < 10:
                stats['aging_assets'] += 1
            else:
                stats['aging_assets'] += 1
            
            # 检查是否推荐报废
            recommendation = LifecycleService.recommend_retirement(equipment.id)
            if recommendation['should_retire']:
                stats['recommended_for_retirement'] += 1
        
        return stats
