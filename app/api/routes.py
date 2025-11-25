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
        start_date = now - timedelta(days=7)
        query = query.filter(RepairOrder.created_date >= start_date)
    elif filter_type == 'month':
        start_date = now - timedelta(days=30)
        query = query.filter(RepairOrder.created_date >= start_date)
    
    # 根据用户角色确定查询条件
    if current_user.role not in ['admin', 'technician']:
        query = query.filter_by(requester_id=current_user.id)
        
    orders = query.order_by(RepairOrder.created_date.desc()).all()
    
    return jsonify([{
        'id': order.id,
        'equipment_name': order.equipment.name if order.equipment else '',
        'requester_name': order.requester.username if order.requester else '',
        'description': order.fault_description,
        'status': order.status,
        'created_date': order.created_date.isoformat() if order.created_date else None,
        'updated_date': order.updated_date.isoformat() if order.updated_date else None
    } for order in orders])


@bp.route('/repair_order/<int:id>')
@login_required
def get_repair_order(id):
    order = RepairOrder.query.get_or_404(id)
    
    # 确保用户有权查看此工单
    if current_user.role not in ['admin', 'technician'] and order.requester_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = {
        'id': order.id,
        'equipment_id': order.equipment_id,
        'equipment_name': order.equipment.name if order.equipment else '',
        'requester_id': order.requester_id,
        'requester_name': order.requester.username if order.requester else '',
        'technician_id': order.technician_id,
        'technician_name': order.technician.username if order.technician else '',
        'description': order.fault_description,
        'status': order.status,
        'created_date': order.created_date.isoformat() if order.created_date else None,
        'updated_date': order.updated_date.isoformat() if order.updated_date else None,
        'completed_date': order.completed_date.isoformat() if order.completed_date else None,
        'part_replacements': []
    }
    
    # 添加配件更换记录
    for replacement in order.part_replacements:
        data['part_replacements'].append({
            'id': replacement.id,
            'spare_part_name': replacement.spare_part.name if replacement.spare_part else '',
            'quantity': replacement.quantity,
            'replacement_date': replacement.replacement_date.isoformat() if replacement.replacement_date else None
        })
    
    return jsonify(data)
