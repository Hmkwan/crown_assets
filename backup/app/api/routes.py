from flask import jsonify, request
from flask_login import login_required, current_user
from app import db
from app.api import bp
from app.models import RepairOrder, Equipment, User, PartReplacement, SparePart
from datetime import datetime, timedelta, timezone


@bp.route('/repair_orders')
@login_required
def get_repair_orders():
    filter_type = request.args.get('filter', 'all')  # today, week, month, all
    now = datetime.now(timezone.utc)
    
    query = RepairOrder.query
    
    if filter_type == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(RepairOrder.created_date >= start_date)
    elif filter_type == 'week':
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(RepairOrder.created_date >= start_date)
    elif filter_type == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(RepairOrder.created_date >= start_date)
    
    # 根据用户角色确定查询条件
    if current_user.role not in ['admin', 'technician']:
        query = query.filter_by(requester_id=current_user.id)
        
    orders = query.order_by(RepairOrder.created_date.desc()).all()
    
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': order.id,
            'equipment_name': order.equipment.name,
            'requester': order.requester.username,
            'department': order.equipment.department,
            'fault_description': order.fault_description,
            'status': order.status,
            'priority': order.priority,
            'created_date': order.created_date.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_date': order.updated_date.strftime('%Y-%m-%d %H:%M:%S') if order.updated_date else None
        })
    
    return jsonify(orders_data)


@bp.route('/repair_order/<int:id>')
@login_required
def get_repair_order(id):
    order = RepairOrder.query.get_or_404(id)
    
    # 检查权限
    if current_user.role not in ['admin', 'technician'] and order.requester_id != current_user.id:
        return jsonify({'error': '权限不足'}), 403
    
    order_data = {
        'id': order.id,
        'equipment_name': order.equipment.name,
        'equipment_type': order.equipment.type,
        'equipment_brand': order.equipment.brand,
        'equipment_model': order.equipment.model,
        'requester': order.requester.username,
        'department': order.equipment.department,
        'fault_description': order.fault_description,
        'repair_description': order.repair_description,
        'status': order.status,
        'priority': order.priority,
        'is_external_repair': order.is_external_repair,
        'external_repair_details': order.external_repair_details,
        'created_date': order.created_date.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_date': order.updated_date.strftime('%Y-%m-%d %H:%M:%S') if order.updated_date else None,
        'completed_date': order.completed_date.strftime('%Y-%m-%d %H:%M:%S') if order.completed_date else None
    }
    
    return jsonify(order_data)