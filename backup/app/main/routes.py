from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timezone
from urllib.parse import urlparse
from app import db
from app.main import bp
from app.models import User, Equipment, RepairOrder, SparePart, Department, UserActivityLog, Notification, PartReplacement


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('main/index.html', title='首页')


@bp.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    return render_template('main/admin_dashboard.html', title='管理员仪表板')


@bp.route('/technician')
@login_required
def technician_dashboard():
    if current_user.role != 'technician':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    # 技术员仪表板逻辑
    return render_template('main/technician_dashboard.html', title='技术员仪表板')


@bp.route('/admin/users')
@login_required
def user_management():
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    return render_template('main/user_management.html', title='用户管理', users=users)


@bp.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('您没有权限执行此操作')
        return redirect(url_for('main.user_management'))
        
    departments = Department.query.all()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        department_id = request.form.get('department_id')
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('该用户名已存在')
            return redirect(url_for('main.add_user'))
            
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            flash('该邮箱已存在')
            return redirect(url_for('main.add_user'))
            
        # 获取部门信息
        department = Department.query.get(department_id)
        if not department:
            flash('请选择有效的部门')
            return redirect(url_for('main.add_user'))
            
        user = User(
            username=username,
            email=email,
            role=role,
            department_id=department_id,
            department=department.name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # 记录用户创建活动
        activity_log = UserActivityLog(
            user_id=current_user.id,
            action='创建用户',
            description=f'管理员 {current_user.username} 创建了用户 {user.username}'
        )
        db.session.add(activity_log)
        db.session.commit()
        
        flash('用户添加成功')
        return redirect(url_for('main.user_management'))
        
    return render_template('main/add_user.html', title='添加用户', departments=departments)


@bp.route('/admin/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if current_user.role != 'admin':
        flash('您没有权限执行此操作')
        return redirect(url_for('main.user_management'))
        
    user = User.query.get_or_404(id)
    departments = Department.query.all()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        department_id = request.form.get('department_id')
        
        # 检查用户名是否已存在（排除当前用户）
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user.id:
            flash('该用户名已存在')
            return redirect(url_for('main.edit_user', id=id))
            
        # 检查邮箱是否已存在（排除当前用户）
        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.id != user.id:
            flash('该邮箱已存在')
            return redirect(url_for('main.edit_user', id=id))
            
        # 获取部门信息
        department = Department.query.get(department_id)
        if not department:
            flash('请选择有效的部门')
            return redirect(url_for('main.edit_user', id=id))
            
        user.username = username
        user.email = email
        user.role = role
        user.department_id = department_id
        user.department = department.name
        
        db.session.commit()
        
        # 记录用户编辑活动
        activity_log = UserActivityLog(
            user_id=current_user.id,
            action='编辑用户',
            description=f'管理员 {current_user.username} 编辑了用户 {user.username}'
        )
        db.session.add(activity_log)
        db.session.commit()
        
        flash('用户信息更新成功')
        return redirect(url_for('main.user_management'))
        
    return render_template('main/edit_user.html', title='编辑用户', user=user, departments=departments)


@bp.route('/admin/users/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
        
    user = User.query.get_or_404(id)
    
    # 禁止删除自己
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': '不能删除当前登录用户'}), 400
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    # 记录用户删除活动
    activity_log = UserActivityLog(
        user_id=current_user.id,
        action='删除用户',
        description=f'管理员 {current_user.username} 删除了用户 {username}'
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '用户删除成功'})


@bp.route('/admin/departments')
@login_required
def department_management():
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    # 获取所有部门
    departments = Department.query.all()
    
    # 获取每个部门的员工数
    dept_list = []
    for dept in departments:
        user_count = User.query.filter_by(department=dept.name).count()
        dept_list.append({
            'id': dept.id,
            'name': dept.name,
            'code': dept.code,
            'cost_center': dept.cost_center,
            'location': dept.location,
            'description': dept.description,
            'user_count': user_count
        })
    
    return render_template('main/department_management.html', title='部门管理', departments=dept_list)


@bp.route('/admin/departments/add', methods=['POST'])
@login_required
def add_department():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    name = request.form.get('name')
    code = request.form.get('code')
    cost_center = request.form.get('cost_center')
    location = request.form.get('location')
    description = request.form.get('description')
    
    # 验证必填字段
    if not name or not code:
        return jsonify({'success': False, 'message': '部门名称和部门代码为必填项'})
    
    # 检查部门名称是否已存在
    if Department.query.filter_by(name=name).first():
        return jsonify({'success': False, 'message': '该部门名称已存在'})
    
    # 检查部门代码是否已存在
    if Department.query.filter_by(code=code).first():
        return jsonify({'success': False, 'message': '该部门代码已存在'})
    
    # 创建新部门
    department = Department(
        name=name,
        code=code,
        cost_center=cost_center,
        location=location,
        description=description
    )
    
    db.session.add(department)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '部门添加成功'})


@bp.route('/admin/departments/update', methods=['POST'])
@login_required
def update_department():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    department_id = request.form.get('department_id')
    name = request.form.get('name')
    code = request.form.get('code')
    cost_center = request.form.get('cost_center')
    location = request.form.get('location')
    description = request.form.get('description')
    
    # 获取部门
    department = Department.query.get(department_id)
    if not department:
        return jsonify({'success': False, 'message': '部门不存在'})
    
    # 检查部门名称是否已存在（排除当前部门）
    existing_dept = Department.query.filter_by(name=name).first()
    if existing_dept and existing_dept.id != int(department_id):
        return jsonify({'success': False, 'message': '该部门名称已存在'})
    
    # 检查部门代码是否已存在（排除当前部门）
    existing_code = Department.query.filter_by(code=code).first()
    if existing_code and existing_code.id != int(department_id):
        return jsonify({'success': False, 'message': '该部门代码已存在'})
    
    # 更新部门信息
    department.name = name
    department.code = code
    department.cost_center = cost_center
    department.location = location
    department.description = description
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': '部门信息更新成功'})


@bp.route('/admin/departments/delete/<int:id>', methods=['POST'])
@login_required
def delete_department(id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    department = Department.query.get_or_404(id)
    
    # 检查是否有用户属于这个部门
    user_count = User.query.filter_by(department=department.name).count()
    if user_count > 0:
        return jsonify({'success': False, 'message': '该部门下还有员工，无法删除'})
    
    # 检查是否有设备属于这个部门
    equipment_count = Equipment.query.filter_by(department=department.name).count()
    if equipment_count > 0:
        return jsonify({'success': False, 'message': '该部门下还有设备，无法删除'})
    
    db.session.delete(department)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '部门删除成功'})


@bp.route('/equipment')
@login_required
def equipment_list():
    # 根据用户角色确定查询条件
    if current_user.role == 'admin':
        equipments = Equipment.query.all()
    else:
        equipments = Equipment.query.filter_by(department=current_user.department).all()
        
    return render_template('main/equipment_list.html', title='设备列表', equipments=equipments)


@bp.route('/equipment/add', methods=['GET', 'POST'])
@login_required
def add_equipment():
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限添加设备')
        return redirect(url_for('main.equipment_list'))
        
    # 获取所有部门
    departments = Department.query.all()
        
    if request.method == 'POST':
        name = request.form.get('name')
        type = request.form.get('type')
        brand = request.form.get('brand')
        model = request.form.get('model')
        serial_number = request.form.get('serial_number')
        purchase_date = request.form.get('purchase_date')
        department_id = request.form.get('department_id')
        
        # 检查序列号是否已存在
        if Equipment.query.filter_by(serial_number=serial_number).first():
            flash('该序列号已存在')
            return redirect(url_for('main.add_equipment'))
            
        # 获取部门信息
        department = Department.query.get(department_id)
        if not department:
            flash('请选择有效的部门')
            return redirect(url_for('main.add_equipment'))
            
        equipment = Equipment(
            name=name,
            type=type,
            brand=brand,
            model=model,
            serial_number=serial_number,
            department_id=department_id,
            department=department.name
        )
        
        if purchase_date:
            try:
                equipment.purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
            except ValueError:
                flash('日期格式不正确')
                return redirect(url_for('main.add_equipment'))
        
        db.session.add(equipment)
        db.session.commit()
        
        # 记录设备添加活动
        activity_log = UserActivityLog(
            user_id=current_user.id,
            action='添加设备',
            description=f'用户 {current_user.username} 添加了设备 {equipment.name} (序列号: {equipment.serial_number})'
        )
        db.session.add(activity_log)
        db.session.commit()
        
        flash('设备添加成功')
        return redirect(url_for('main.equipment_list'))
        
    return render_template('main/add_equipment.html', title='添加设备', departments=departments)


@bp.route('/equipment/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_equipment(id):
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限编辑设备')
        return redirect(url_for('main.equipment_list'))
        
    equipment = Equipment.query.get_or_404(id)
    
    # 获取所有部门
    departments = Department.query.all()
    
    if request.method == 'POST':
        equipment.name = request.form.get('name')
        equipment.type = request.form.get('type')
        equipment.brand = request.form.get('brand')
        equipment.model = request.form.get('model')
        equipment.serial_number = request.form.get('serial_number')
        purchase_date = request.form.get('purchase_date')
        department_id = request.form.get('department_id')
        equipment.status = request.form.get('status')
        
        # 检查序列号是否已存在（排除当前设备）
        existing = Equipment.query.filter_by(serial_number=equipment.serial_number).first()
        if existing and existing.id != equipment.id:
            flash('该序列号已存在')
            return redirect(url_for('main.edit_equipment', id=id))
            
        # 获取部门信息
        department = Department.query.get(department_id)
        if not department:
            flash('请选择有效的部门')
            return redirect(url_for('main.edit_equipment', id=id))
            
        equipment.department_id = department_id
        equipment.department = department.name
            
        if purchase_date:
            try:
                equipment.purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
            except ValueError:
                flash('日期格式不正确')
                return redirect(url_for('main.edit_equipment', id=id))
        
        db.session.commit()
        
        # 记录设备编辑活动
        activity_log = UserActivityLog(
            user_id=current_user.id,
            action='编辑设备',
            description=f'用户 {current_user.username} 编辑了设备 {equipment.name} (序列号: {equipment.serial_number})'
        )
        db.session.add(activity_log)
        db.session.commit()
        
        flash('设备更新成功')
        return redirect(url_for('main.equipment_list'))
        
    return render_template('main/edit_equipment.html', title='编辑设备', equipment=equipment, departments=departments)


@bp.route('/equipment/delete/<int:id>', methods=['POST'])
@login_required
def delete_equipment(id):
    if current_user.role not in ['admin']:
        return jsonify({'success': False, 'message': '权限不足'}), 403
        
    equipment = Equipment.query.get_or_404(id)
    equipment_name = equipment.name
    serial_number = equipment.serial_number
    
    db.session.delete(equipment)
    db.session.commit()
    
    # 记录设备删除活动
    activity_log = UserActivityLog(
        user_id=current_user.id,
        action='删除设备',
        description=f'管理员 {current_user.username} 删除了设备 {equipment_name} (序列号: {serial_number})'
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '设备删除成功'})


@bp.route('/spare_parts')
@login_required
def spare_parts():
    # 根据用户角色确定查询条件
    if current_user.role == 'admin':
        spare_parts = SparePart.query.all()
    else:
        spare_parts = SparePart.query.filter_by(department=current_user.department).all()
        
    return render_template('main/spare_parts.html', title='配件列表', spare_parts=spare_parts)


@bp.route('/spare_parts/add', methods=['GET', 'POST'])
@login_required
def add_spare_part():
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限添加配件')
        return redirect(url_for('main.spare_parts'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        part_number = request.form.get('part_number')
        price = request.form.get('price')
        stock_quantity = request.form.get('stock_quantity')
        
        # 检查配件编号是否已存在
        if SparePart.query.filter_by(part_number=part_number).first():
            flash('该配件编号已存在')
            return redirect(url_for('main.add_spare_part'))
            
        spare_part = SparePart(
            name=name,
            part_number=part_number,
            price=float(price) if price else 0.0,
            stock_quantity=int(stock_quantity) if stock_quantity else 0
        )
        
        db.session.add(spare_part)
        db.session.commit()
        
        # 记录配件添加活动
        activity_log = UserActivityLog(
            user_id=current_user.id,
            action='添加配件',
            description=f'用户 {current_user.username} 添加了配件 {spare_part.name} (编号: {spare_part.part_number})'
        )
        db.session.add(activity_log)
        db.session.commit()
        
        flash('配件添加成功')
        return redirect(url_for('main.spare_parts'))
        
    return render_template('main/add_spare_part.html', title='添加配件')


@bp.route('/spare_parts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_spare_part(id):
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限编辑配件')
        return redirect(url_for('main.spare_parts'))
        
    spare_part = SparePart.query.get_or_404(id)
    
    if request.method == 'POST':
        spare_part.name = request.form.get('name')
        spare_part.part_number = request.form.get('part_number')
        price = request.form.get('price')
        stock_quantity = request.form.get('stock_quantity')
        
        # 检查配件编号是否已存在（排除当前配件）
        existing = SparePart.query.filter_by(part_number=spare_part.part_number).first()
        if existing and existing.id != spare_part.id:
            flash('该配件编号已存在')
            return redirect(url_for('main.edit_spare_part', id=id))
            
        spare_part.price = float(price) if price else 0.0
        spare_part.stock_quantity = int(stock_quantity) if stock_quantity else 0
        
        db.session.commit()
        
        # 记录配件编辑活动
        activity_log = UserActivityLog(
            user_id=current_user.id,
            action='编辑配件',
            description=f'用户 {current_user.username} 编辑了配件 {spare_part.name} (编号: {spare_part.part_number})'
        )
        db.session.add(activity_log)
        db.session.commit()
        
        flash('配件更新成功')
        return redirect(url_for('main.spare_parts'))
        
    return render_template('main/edit_spare_part.html', title='编辑配件', spare_part=spare_part)


@bp.route('/spare_parts/delete/<int:id>', methods=['POST'])
@login_required
def delete_spare_part(id):
    if current_user.role not in ['admin']:
        return jsonify({'success': False, 'message': '权限不足'}), 403
        
    spare_part = SparePart.query.get_or_404(id)
    part_name = spare_part.name
    part_number = spare_part.part_number
    
    db.session.delete(spare_part)
    db.session.commit()
    
    # 记录配件删除活动
    activity_log = UserActivityLog(
        user_id=current_user.id,
        action='删除配件',
        description=f'管理员 {current_user.username} 删除了配件 {part_name} (编号: {part_number})'
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '配件删除成功'})


@bp.route('/repair_orders')
@login_required
def repair_orders():
    # 根据用户角色确定查询条件
    if current_user.role == 'admin':
        orders = RepairOrder.query.all()
    elif current_user.role == 'technician':
        orders = RepairOrder.query.all()
    else:
        orders = RepairOrder.query.filter_by(requester_id=current_user.id).all()
        
    return render_template('main/repair_orders.html', title='维修工单', orders=orders)


@bp.route('/repair_orders/<int:id>')
@login_required
def repair_order_detail(id):
    order = RepairOrder.query.get_or_404(id)
    
    # 检查权限
    if current_user.role == 'user' and order.requester_id != current_user.id:
        flash('您没有权限查看此工单')
        return redirect(url_for('main.repair_orders'))
        
    return render_template('main/repair_order_detail.html', title='工单详情', order=order)


@bp.route('/create_repair_order', methods=['GET', 'POST'])
@login_required
def create_repair_order():
    # 获取当前用户所属部门的设备
    if current_user.role == 'admin':
        equipments = Equipment.query.all()
    else:
        equipments = Equipment.query.filter_by(department=current_user.department).all()
    
    if request.method == 'POST':
        equipment_id = request.form.get('equipment_id')
        fault_description = request.form.get('fault_description')
        priority = request.form.get('priority', 'medium')
        
        # 验证设备是否存在
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            flash('请选择有效的设备')
            return redirect(url_for('main.create_repair_order'))
        
        # 创建维修工单
        repair_order = RepairOrder(
            equipment_id=equipment_id,
            requester_id=current_user.id,
            fault_description=fault_description,
            priority=priority
        )
        
        db.session.add(repair_order)
        db.session.commit()
        
        # 记录创建工单活动
        activity_log = UserActivityLog(
            user_id=current_user.id,
            action='创建维修工单',
            description=f'用户 {current_user.username} 创建了维修工单 #{repair_order.id} (设备: {equipment.name})'
        )
        db.session.add(activity_log)
        db.session.commit()
        
        flash('维修工单创建成功')
        return redirect(url_for('main.repair_orders'))
        
    return render_template('main/create_repair_order.html', 
                         title='创建维修工单', 
                         equipments=equipments)


@bp.route('/repair_orders/<int:id>/update_status', methods=['POST'])
@login_required
def update_repair_order_status(id):
    repair_order = RepairOrder.query.get_or_404(id)
    
    # 检查权限（只有技术员和管理员可以更新状态）
    if current_user.role not in ['admin', 'technician']:
        flash('您没有权限执行此操作')
        return redirect(url_for('main.repair_orders'))
    
    new_status = request.form.get('status')
    repair_description = request.form.get('repair_description')
    technician_id = request.form.get('technician_id')
    
    # 更新工单状态
    old_status = repair_order.status
    repair_order.status = new_status
    
    if repair_description:
        repair_order.repair_description = repair_description
        
    if technician_id:
        repair_order.technician_id = technician_id
        
    if new_status == 'completed' and not repair_order.completed_date:
        repair_order.completed_date = datetime.now(timezone.utc)
        
    repair_order.updated_date = datetime.now(timezone.utc)
    
    db.session.commit()
    
    # 记录状态更新活动
    activity_log = UserActivityLog(
        user_id=current_user.id,
        action='更新维修工单状态',
        description=f'用户 {current_user.username} 将维修工单 #{repair_order.id} 状态从 "{old_status}" 更新为 "{new_status}"'
    )
    db.session.add(activity_log)
    db.session.commit()
    
    flash('工单状态更新成功')
    return redirect(url_for('main.repair_order_detail', id=id))


@bp.route('/notifications')
@login_required
def notifications():
    # 获取用户的通知，按时间倒序排列
    user_notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.timestamp.desc())\
        .all()
        
    return render_template('main/notifications.html', 
                         title='通知消息', 
                         notifications=user_notifications)


@bp.route('/mark_notification_as_read/<int:id>')
@login_required
def mark_notification_as_read(id):
    notification = Notification.query.get_or_404(id)
    
    # 检查权限
    if notification.user_id != current_user.id:
        flash('您没有权限操作此通知')
        return redirect(url_for('main.notifications'))
        
    notification.is_read = True
    db.session.commit()
    
    # 重定向到通知相关页面（如果有）
    return redirect(url_for('main.notifications'))


@bp.route('/reports')
@login_required
def reports():
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    # 获取统计信息
    total_users = User.query.count()
    total_equipment = Equipment.query.count()
    total_repair_orders = RepairOrder.query.count()
    total_spare_parts = SparePart.query.count()
    
    # 按状态统计设备
    equipment_by_status = db.session.query(
        Equipment.status,
        func.count(Equipment.id).label('count')
    ).group_by(Equipment.status).all()
    
    # 按类型统计设备
    equipment_by_type = db.session.query(
        Equipment.type,
        func.count(Equipment.id).label('count')
    ).group_by(Equipment.type).all()
    
    # 按部门统计设备
    equipment_by_department = db.session.query(
        Equipment.department,
        func.count(Equipment.id).label('count')
    ).group_by(Equipment.department).all()
    
    # 按状态统计维修工单
    repair_orders_by_status = db.session.query(
        RepairOrder.status,
        func.count(RepairOrder.id).label('count')
    ).group_by(RepairOrder.status).all()
    
    # 按优先级统计维修工单
    repair_orders_by_priority = db.session.query(
        RepairOrder.priority,
        func.count(RepairOrder.id).label('count')
    ).group_by(RepairOrder.priority).all()
    
    return render_template('main/reports.html', 
                          title='统计报表',
                          total_users=total_users,
                          total_equipment=total_equipment,
                          total_repair_orders=total_repair_orders,
                          total_spare_parts=total_spare_parts,
                          equipment_by_status=equipment_by_status,
                          equipment_by_type=equipment_by_type,
                          equipment_by_department=equipment_by_department,
                          repair_orders_by_status=repair_orders_by_status,
                          repair_orders_by_priority=repair_orders_by_priority)


@bp.route('/reports/export')
@login_required
def export_report():
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    # 获取报表类型
    report_type = request.args.get('type', 'summary')
    
    # 创建CSV数据
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    if report_type == 'equipment':
        # 导出设备报表
        writer.writerow(['设备名称', '类型', '品牌', '型号', '序列号', '所属部门', '状态', '购买日期'])
        equipments = Equipment.query.all()
        for eq in equipments:
            writer.writerow([
                eq.name, eq.type, eq.brand, eq.model, 
                eq.serial_number, eq.department, eq.status,
                eq.purchase_date.strftime('%Y-%m-%d') if eq.purchase_date else ''
            ])
        filename = 'equipment_report.csv'
    elif report_type == 'users':
        # 导出用户报表
        writer.writerow(['用户名', '邮箱', '角色', '所属部门'])
        users = User.query.all()
        for user in users:
            writer.writerow([user.username, user.email, user.role, user.department])
        filename = 'user_report.csv'
    elif report_type == 'repair_orders':
        # 导出维修工单报表
        writer.writerow(['工单ID', '设备名称', '申请人', '技术员', '故障描述', '状态', '优先级', '创建日期'])
        orders = RepairOrder.query.all()
        for order in orders:
            writer.writerow([
                order.id, 
                order.equipment.name if order.equipment else '',
                order.requester.username if order.requester else '',
                order.technician.username if order.technician else '',
                order.fault_description,
                order.status,
                order.priority,
                order.created_date.strftime('%Y-%m-%d %H:%M:%S') if order.created_date else ''
            ])
        filename = 'repair_order_report.csv'
    else:
        # 导出汇总报表
        writer.writerow(['统计项目', '数量'])
        writer.writerow(['总用户数', User.query.count()])
        writer.writerow(['总设备数', Equipment.query.count()])
        writer.writerow(['总维修工单数', RepairOrder.query.count()])
        writer.writerow(['总配件数', SparePart.query.count()])
        filename = 'summary_report.csv'
    
    # 创建响应
    from flask import Response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@bp.route('/user_activity_logs')
@login_required
def user_activity_logs():
    if current_user.role != 'admin':
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))
    
    # 分页查询用户活动日志
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    logs_query = UserActivityLog.query.join(User).order_by(UserActivityLog.timestamp.desc())
    logs = logs_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('main/user_activity_logs.html', 
                          title='用户活动日志', 
                          logs=logs)


@bp.route('/user_history')
@login_required
def user_history():
    # 获取当前用户的历史记录
    user_id = current_user.id
    
    # 分页查询用户相关的历史工单
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 查询用户创建的工单
    created_orders = RepairOrder.query.filter_by(requester_id=user_id)\
        .order_by(RepairOrder.created_date.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('main/user_history.html', 
                          title='我的历史记录',
                          orders=created_orders)


@bp.route('/part_request_history')
@login_required
def part_request_history():
    # 获取当前用户的历史配件申请
    user_id = current_user.id
    
    # 分页查询用户相关的配件申请单
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 查询用户创建的配件申请单
    requests = RepairOrder.query.filter_by(requester_id=user_id)\
        .order_by(RepairOrder.created_date.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('main/part_request_history.html', 
                          title='配件申请历史',
                          requests=requests)
