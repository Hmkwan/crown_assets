@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # 获取当前用户的待处理事项数量
    pending_repairs = RepairOrder.query.filter_by(status='submitted').count()
    pending_approvals = ApprovalWorkflow.query.filter_by(status='pending').count()
    
    # 构建仪表盘卡片列表（后端构造更稳定，便于测试与调整顺序）
    tiles = []
    if current_user.role in ['admin', 'technician']:
        tiles.extend([
            {'title':'维修工单','text':'查看和管理所有维修工单','url': url_for('repair_orders')},  // 修改：移除 'main.' 前缀
            {'title':'设备管理','text':'查看和管理所有 IT 设备','url': url_for('main.equipment_list')},
            {'title':'配件管理','text':'查看和管理配件库存','url': url_for('main.spare_parts')},
            {'title':'创建维修工单','text':'提交新的维修工单','url': url_for('main.create_repair_order')},
            {'title':'我的工单','text':'查看我提交的维修工单','url': url_for('repair_orders')},  // 修改：移除 'main.' 前缀
            {'title':'审批管理','text':'审批待处理的工单/申请','url': url_for('main.approvals')},
            {'title':'配件申请管理','text':'查看配件申请与历史','url': url_for('main.part_request_orders')},
            {'title':'提交配件申请','text':'提交新的配件申请','url': url_for('main.create_part_request_order')},
            {'title':'仪表板','text':'管理员仪表板与统计','url': url_for('main.admin_dashboard')},
            {'title':'用户管理','text':'添加/编辑/删除用户','url': url_for('main.user_management')},
            {'title':'部门管理','text':'管理部门与成员','url': url_for('main.department_management')},
            {'title':'设备类型','text':'管理设备类型','url': url_for('main.equipment_types')},
            {'title':'添加设备','text':'登记新设备','url': url_for('main.add_equipment')},
            {'title':'添加配件','text':'登记新配件','url': url_for('main.add_spare_part')},
            {'title':'发起设备调拨','text':'发起设备调拨','url': url_for('main.create_transfer')},
            {'title':'发起设备报废','text':'发起设备报废','url': url_for('main.create_scrap')},
            {'title':'调拨管理','text':'管理调拨申请','url': url_for('main.admin_transfers')},
            {'title':'报废管理','text':'管理报废申请','url': url_for('main.admin_scraps')},
            {'title':'通知','text':'查看系统通知','url': url_for('main.notifications')},
            {'title':'操作日志','text':'查看用户操作记录','url': url_for('main.user_activity_logs')}
        ])
    else:
        tiles.extend([
            {'title':'提交维修申请','text':'提交新的设备维修申请','url': url_for('main.create_repair_order')},
            {'title':'我的工单','text':'查看我提交的维修工单','url': url_for('repair_orders')},  // 修改：移除 'main.' 前缀
            {'title':'提交配件申请','text':'提交配件申请','url': url_for('main.create_part_request_order')},
            {'title':'通知','text':'查看系统通知','url': url_for('main.notifications')}
        ])

    return render_template('main/index.html', 
                         title='首页',
                         pending_repairs=pending_repairs,
                         pending_approvals=pending_approvals,
                         tiles=tiles)

@bp.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': '您没有权限执行此操作'}), 403
        
    departments = Department.query.all()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        role = request.form.get('role')
        department_id = request.form.get('department_id')
        
        # 验证密码：如果管理员没有提供 password2，则只要 password 非空即可；
        # 如果提供了 password2，则校验两次输入是否一致。
        if not password:
            return jsonify({'success': False, 'message': '密码不能为空'})

        if password2 is not None and password != password2:
            return jsonify({'success': False, 'message': '两次输入的密码不一致'})
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': '该用户名已存在'})
            
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': '该邮箱已存在'})
            
        # 获取部门信息
        department = Department.query.get(department_id)
        if not department:
            return jsonify({'success': False, 'message': '请选择有效的部门'})
            
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
        

        
        
        

        
            
            
            
        
        
        

