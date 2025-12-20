"""
审批流程增强代码 - 维修金额和条件路由
复制此代码到 app/main/routes.py 中替换 approve_repair_order 函数
"""

@bp.route('/approvals/repair_order/<int:order_id>/<action>', methods=['POST'])
@login_required
def approve_repair_order(order_id, action):
    """审批维修工单 - 支持维修金额和条件路由"""
    # 获取审批记录
    approval = ApprovalWorkflow.query.filter_by(
        order_type='repair_order',
        order_id=order_id,
        approver_id=current_user.id,
        status='pending'
    ).first_or_404()
    
    # 获取工单
    repair_order = RepairOrder.query.get_or_404(order_id)
    beijing_now = get_beijing_now()
    
    if action == 'approve':
        # 更新审批状态
        approval.status = 'approved'
        approval.approved_date = beijing_now
        approval.comments = request.form.get('comments', '')
        
        # 管理员输入维修金额评估
        if approval.approval_level == 'admin':
            repair_cost = request.form.get('repair_cost', type=float)
            if repair_cost and repair_cost > 0:
                approval.repair_cost_input = repair_cost
                repair_order.repair_cost = repair_cost
                
                # 记录活动
                _log_activity('管理员评估', 
                             f'{current_user.username} 评估维修单 #{repair_order.id} 维修金额为 ¥{repair_cost:.2f}')
        
        # 部门负责人确认管理员评估的金额
        elif approval.approval_level == 'department_head':
            # 如果管理员已输入金额,部门负责人需确认
            if repair_order.repair_cost and repair_order.repair_cost > 0:
                confirm_cost = request.form.get('confirm_cost', 'yes')
                if confirm_cost == 'no':
                    # 打回给管理员重新评估
                    approval.status = 'returned'
                    approval.action_type = 'return'
                    approval.comments = f'[金额不符,要求重新评估] {approval.comments}'
                    
                    # 创建新的管理员审批
                    admin_node = WorkflowNode.query.filter_by(
                        order_type='repair_order',
                        role_required='admin',
                        is_active=True
                    ).first()
                    
                    if admin_node:
                        admin_user = User.query.filter_by(role='admin').first()
                        
                        if admin_user:
                            new_approval = ApprovalWorkflow(
                                order_type='repair_order',
                                order_id=repair_order.id,
                                approver_id=admin_user.id,
                                approval_level='admin',
                                node_id=admin_node.id,
                                status='pending'
                            )
                            db.session.add(new_approval)
                            
                            # 通知管理员
                            notification = Notification(
                                user_id=admin_user.id,
                                title='维修工单被退回',
                                message=f'部门负责人要求重新评估维修单 #{repair_order.id} 的维修金额',
                                order_type='repair_order',
                                order_id=repair_order.id
                            )
                            db.session.add(notification)
                    
                    db.session.commit()
                    flash('已退回给管理员重新评估', 'warning')
                    return redirect(url_for('main.approvals'))
        
        # 根据审批级别更新工单状态
        if approval.approval_level == 'department_head':
            repair_order.department_head_approved = True
            repair_order.department_head_id = current_user.id
            repair_order.status = 'department_head_approved'
                
        elif approval.approval_level == 'admin':
            repair_order.admin_approved = True
            repair_order.admin_id = current_user.id
            repair_order.status = 'admin_approved'
            
        # 检查是否还有后续审批节点 - 支持金额条件跳过
        next_node = get_next_approval_node('repair_order', repair_order.id, 
                                          repair_cost=float(repair_order.repair_cost) if repair_order.repair_cost else None)
        if next_node:
            # 创建下一个审批节点
            next_approver_id = get_approver_id(next_node, repair_order.requester.department)
            if not next_approver_id:
                flash(f'错误: 无法找到 {next_node.name} 的审批人 (角色: {next_node.role_required}, 部门: {repair_order.requester.department})', 'danger')
                db.session.rollback()
                return redirect(url_for('main.approvals'))
                
            next_approval = ApprovalWorkflow(
                order_type='repair_order',
                order_id=repair_order.id,
                approver_id=next_approver_id,
                approval_level=next_node.role_required,
                node_id=next_node.id,
                status='pending'
            )
            db.session.add(next_approval)
            
            # 发送通知给下一个审批人
            next_approver = User.query.get(next_approver_id)
            if next_approver:
                cost_info = f' (维修金额: ¥{repair_order.repair_cost:.2f})' if repair_order.repair_cost else ''
                notification = Notification(
                    user_id=next_approver.id,
                    title='待审批维修工单',
                    message=f'维修工单 #{repair_order.id} 需要您审批 ({next_node.name}){cost_info}',
                    order_type='repair_order',
                    order_id=repair_order.id
                )
                db.session.add(notification)
            
            # 审批进行中，发送进度通知给申请人
            notification = Notification(
                user_id=repair_order.requester_id,
                title='维修工单审批状态更新',
                message=f'您的维修工单 #{repair_order.id} 已被 {current_user.username} 批准，进入下一审批节点: {next_node.name}',
                order_type='repair_order',
                order_id=repair_order.id
            )
            db.session.add(notification)
        else:
            # 所有审批完成，更新工单状态为已批准
            repair_order.status = 'approved'
            
            # 发送审批完成通知给申请人
            cost_info = f', 维修金额: ¥{repair_order.repair_cost:.2f}' if repair_order.repair_cost else ''
            notification = Notification(
                user_id=repair_order.requester_id,
                title='维修工单审批完成',
                message=f'您的维修工单 #{repair_order.id} 已通过所有审批，可以开始维修{cost_info}',
                order_type='repair_order',
                order_id=repair_order.id
            )
            db.session.add(notification)
            
            # 发送通知给管理员和该部门技术员
            admins = User.query.filter_by(role='admin').all()
            # 只通知该工单所属部门的技术员
            technicians = User.query.filter_by(
                role='technician',
                department=repair_order.requester.department
            ).all()
            
            for user in admins + technicians:
                if user.id != current_user.id:
                    user_notification = Notification(
                        user_id=user.id,
                        title='维修工单已批准',
                        message=f'维修工单 #{repair_order.id} 已通过审批，等待处理{cost_info}',
                        order_type='repair_order',
                        order_id=repair_order.id
                    )
                    db.session.add(user_notification)
            
            # 记录审批活动
            _log_activity('审批维修工单', f'用户 {current_user.username} 批准了维修工单 #{repair_order.id}')
            
        flash('维修工单审批成功')
        
    elif action == 'reject':
        # 拒绝工单
        approval.status = 'rejected'
        approval.approved_date = beijing_now
        approval.comments = request.form.get('comments', '')
        
        # 更新工单状态
        repair_order.status = 'cancelled'
        
        # 记录审批活动
        _log_activity('审批维修工单', f'用户 {current_user.username} 拒绝了维修工单 #{repair_order.id}')
        
        # 创建通知给申请人
        notification = Notification(
            user_id=repair_order.requester_id,
            title='维修工单被拒绝',
            message=f'您的维修工单 #{repair_order.id} 已被 {current_user.username} 拒绝',
            order_type='repair_order',
            order_id=repair_order.id
        )
        db.session.add(notification)
        
        flash('维修工单已拒绝')
        
    db.session.commit()
    return redirect(url_for('main.approvals'))
