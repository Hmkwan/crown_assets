#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
审批流程引擎 - 核心业务逻辑
负责流程实例化、节点路由、状态流转、条件判断等
"""

from app import db
from app.approval_models import (
    WorkflowTemplate, WorkflowNode, ApprovalInstance, 
    ApprovalStep, ApprovalLog, ApprovalDelegate
)
from app.models import User, ApprovalRole, UserApprovalRole
from datetime import datetime, timedelta, timezone
from sqlalchemy import and_, or_
import json
import ast
import operator

# 导入通知服务
try:
    from app.services.approval_notification_service import ApprovalNotificationService
    NOTIFICATION_ENABLED = True
except ImportError:
    NOTIFICATION_ENABLED = False


class ApprovalEngine:
    """审批流程引擎"""
    
    @staticmethod
    def start_workflow(order_type, order_id, requester_id, form_data=None, template_id=None):
        """
        启动审批流程
        
        Args:
            order_type: 工单类型
            order_id: 工单ID
            requester_id: 申请人ID
            form_data: 表单数据
            template_id: 指定模板ID(可选,默认使用该类型的默认模板)
        
        Returns:
            ApprovalInstance: 审批实例
        """
        # 1. 获取模板
        if template_id:
            template = WorkflowTemplate.query.get(template_id)
        else:
            template = WorkflowTemplate.query.filter_by(
                order_type=order_type,
                is_active=True,
                is_default=True
            ).first()
        
        if not template:
            raise Exception(f'未找到工单类型 {order_type} 的审批流程模板')
        
        # 2. 创建审批实例
        instance_no = ApprovalEngine._generate_instance_no(order_type)
        requester = User.query.get(requester_id)
        
        instance = ApprovalInstance(
            instance_no=instance_no,
            template_id=template.id,
            order_type=order_type,
            order_id=order_id,
            requester_id=requester_id,
            requester_dept_id=requester.department_id if requester else None,
            status='in_progress',
            form_data=form_data or {},
            context_data={
                'requester_id': requester_id,
                'order_type': order_type,
                'order_id': order_id
            }
        )
        db.session.add(instance)
        db.session.flush()
        
        # 3. 记录日志
        ApprovalEngine._log_action(instance.id, None, 'start', requester_id, '流程启动')
        
        # 4. 执行第一个节点
        first_node = template.nodes.filter_by(is_active=True).order_by(WorkflowNode.sequence).first()
        if first_node:
            ApprovalEngine._execute_node(instance, first_node)
        
        db.session.commit()
        return instance
    
    @staticmethod
    def _execute_node(instance, node):
        """
        执行节点
        
        Args:
            instance: 审批实例
            node: 工作流节点
        """
        # 1. 检查条件
        if not ApprovalEngine._check_node_condition(instance, node):
            # 条件不满足,跳过节点
            ApprovalEngine._log_action(instance.id, None, 'skip_node', None, 
                                       f'节点 {node.name} 条件不满足,自动跳过')
            ApprovalEngine._move_to_next_node(instance, node)
            return
        
        # 2. 更新实例当前节点
        instance.current_node_id = node.id
        
        # 3. 根据节点类型执行
        if node.node_type == 'approval':
            ApprovalEngine._create_approval_step(instance, node)
        elif node.node_type == 'condition':
            ApprovalEngine._handle_condition_node(instance, node)
        elif node.node_type == 'parallel':
            ApprovalEngine._create_parallel_approval(instance, node)
        elif node.node_type == 'auto':
            ApprovalEngine._handle_auto_node(instance, node)
    
    @staticmethod
    def _create_approval_step(instance, node):
        """创建审批步骤"""
        # 1. 查找审批人
        approvers = ApprovalEngine._find_approvers(instance, node)
        
        if not approvers:
            # 没有找到审批人,记录日志并跳过
            ApprovalEngine._log_action(instance.id, None, 'no_approver', None,
                                       f'节点 {node.name} 未找到审批人,自动跳过')
            ApprovalEngine._move_to_next_node(instance, node)
            return
        
        # 2. 选择审批人(负载均衡/轮询/随机)
        approver = ApprovalEngine._select_approver(approvers, node)
        
        # 3. 检查代理
        delegate = ApprovalEngine._check_delegate(approver.id, instance.order_type, node.approval_role_id)
        if delegate:
            actual_approver = delegate.delegate_to
            ApprovalEngine._log_action(instance.id, None, 'delegate', approver.id,
                                       f'审批代理: {approver.username} -> {actual_approver.username}')
        else:
            actual_approver = approver
        
        # 4. 创建审批步骤
        step_no = f'{instance.instance_no}-{instance.steps.count() + 1:03d}'
        deadline = None
        if node.timeout_hours:
            deadline = datetime.now(timezone.utc) + timedelta(hours=node.timeout_hours)
        
        step = ApprovalStep(
            instance_id=instance.id,
            node_id=node.id,
            sequence=instance.steps.count() + 1,
            step_no=step_no,
            approver_id=actual_approver.id,
            approver_role_id=node.approval_role_id,
            status='pending',
            deadline=deadline
        )
        db.session.add(step)
        db.session.flush()
        
        # 5. 发送通知
        if node.notify_on_start:
            ApprovalEngine._send_notification(step, 'pending')
        
        # 6. 记录日志
        ApprovalEngine._log_action(instance.id, step.id, 'assign', None,
                                   f'分配给审批人: {actual_approver.username}')
    
    @staticmethod
    def _create_parallel_approval(instance, node):
        """创建并行审批步骤"""
        # 1. 查找所有审批人
        approvers = ApprovalEngine._find_approvers(instance, node)
        
        if not approvers:
            ApprovalEngine._log_action(instance.id, None, 'no_approver', None,
                                       f'并行节点 {node.name} 未找到审批人,自动跳过')
            ApprovalEngine._move_to_next_node(instance, node)
            return
        
        # 2. 生成并行组ID
        parallel_group_id = f'{instance.instance_no}-PG-{instance.steps.count() + 1}'
        
        # 3. 为每个审批人创建步骤
        approver_ids = []
        for approver in approvers:
            # 检查代理
            delegate = ApprovalEngine._check_delegate(approver.id, instance.order_type, node.approval_role_id)
            actual_approver = delegate.delegate_to if delegate else approver
            approver_ids.append(actual_approver.id)
            
            step_no = f'{instance.instance_no}-{instance.steps.count() + 1:03d}'
            deadline = None
            if node.timeout_hours:
                deadline = datetime.now(timezone.utc) + timedelta(hours=node.timeout_hours)
            
            step = ApprovalStep(
                instance_id=instance.id,
                node_id=node.id,
                sequence=instance.steps.count() + 1,
                step_no=step_no,
                approver_id=actual_approver.id,
                approver_role_id=node.approval_role_id,
                status='pending',
                deadline=deadline,
                parallel_group_id=parallel_group_id,
                parallel_approvers=approver_ids
            )
            db.session.add(step)
            
            # 发送通知
            if node.notify_on_start and NOTIFICATION_ENABLED:
                try:
                    ApprovalNotificationService.notify_new_approval(step)
                except Exception as e:
                    # 通知失败不影响主流程
                    print(f"发送通知失败: {e}")
        
        db.session.flush()
        
        # 4. 记录日志
        ApprovalEngine._log_action(instance.id, None, 'parallel_start', None,
                                   f'并行审批开始,需要{node.required_approvals}人审批')
    
    @staticmethod
    def approve_step(step_id, approver_id, comment='', form_data=None):
        """
        审批通过
        
        Args:
            step_id: 步骤ID
            approver_id: 审批人ID
            comment: 审批意见
            form_data: 审批时提交的表单数据
        
        Returns:
            dict: 审批结果
        """
        step = ApprovalStep.query.get(step_id)
        if not step:
            raise Exception('审批步骤不存在')
        
        if step.approver_id != approver_id:
            raise Exception('您不是该步骤的审批人')
        
        if step.status != 'pending':
            raise Exception(f'该步骤状态为 {step.status},无法审批')
        
        # 更新步骤
        step.status = 'approved'
        step.result = 'approved'
        step.comment = comment
        step.approved_date = datetime.now(timezone.utc)
        
        instance = step.instance
        
        # 记录日志
        ApprovalEngine._log_action(instance.id, step.id, 'approve', approver_id, comment)
        
        # 处理并行审批
        if step.parallel_group_id:
            ApprovalEngine._handle_parallel_result(step, 'approved')
        else:
            # 普通审批,进入下一节点
            ApprovalEngine._move_to_next_node(instance, step.node)
        
        db.session.commit()
        
        return {'success': True, 'message': '审批通过'}
    
    @staticmethod
    def reject_step(step_id, approver_id, comment=''):
        """审批拒绝"""
        step = ApprovalStep.query.get(step_id)
        if not step:
            raise Exception('审批步骤不存在')
        
        if step.approver_id != approver_id:
            raise Exception('您不是该步骤的审批人')
        
        if step.status != 'pending':
            raise Exception(f'该步骤状态为 {step.status},无法审批')
        
        # 更新步骤
        step.status = 'rejected'
        step.result = 'rejected'
        step.comment = comment
        step.approved_date = datetime.now(timezone.utc)
        
        instance = step.instance
        
        # 记录日志
        ApprovalEngine._log_action(instance.id, step.id, 'reject', approver_id, comment)
        
        # 处理并行审批
        if step.parallel_group_id:
            ApprovalEngine._handle_parallel_result(step, 'rejected')
        else:
            # 普通审批被拒绝,终止流程
            ApprovalEngine._terminate_workflow(instance, 'rejected', comment)
        
        db.session.commit()
        
        return {'success': True, 'message': '审批已拒绝'}
    
    @staticmethod
    def _handle_parallel_result(step, result):
        """处理并行审批结果"""
        instance = step.instance
        node = step.node
        
        # 获取同组的所有步骤
        parallel_steps = ApprovalStep.query.filter_by(
            instance_id=instance.id,
            parallel_group_id=step.parallel_group_id
        ).all()
        
        approved_count = sum(1 for s in parallel_steps if s.result == 'approved')
        rejected_count = sum(1 for s in parallel_steps if s.result == 'rejected')
        pending_count = sum(1 for s in parallel_steps if s.status == 'pending')
        
        # 根据并行模式判断
        should_continue = False
        should_reject = False
        
        if node.parallel_mode == 'all':
            # 全部通过才继续
            if approved_count == len(parallel_steps):
                should_continue = True
            elif rejected_count > 0:
                should_reject = True
        elif node.parallel_mode == 'any':
            # 任一通过就继续
            if approved_count > 0:
                should_continue = True
            elif rejected_count == len(parallel_steps):
                should_reject = True
        elif node.parallel_mode == 'count':
            # 达到指定数量
            if approved_count >= node.required_approvals:
                should_continue = True
            elif rejected_count > len(parallel_steps) - node.required_approvals:
                should_reject = True
        
        if should_continue:
            # 更新所有待审批步骤为已完成
            for s in parallel_steps:
                if s.status == 'pending':
                    s.status = 'skipped'
            ApprovalEngine._move_to_next_node(instance, node)
        elif should_reject:
            # 终止流程
            ApprovalEngine._terminate_workflow(instance, 'rejected', '并行审批被拒绝')
    
    @staticmethod
    def _move_to_next_node(instance, current_node):
        """移动到下一个节点"""
        # 查找下一个节点
        next_node = WorkflowNode.query.filter(
            WorkflowNode.template_id == instance.template_id,
            WorkflowNode.sequence > current_node.sequence,
            WorkflowNode.is_active == True
        ).order_by(WorkflowNode.sequence).first()
        
        if next_node:
            # 执行下一个节点
            ApprovalEngine._execute_node(instance, next_node)
        else:
            # 没有下一个节点,流程完成
            ApprovalEngine._complete_workflow(instance, 'approved')
    
    @staticmethod
    def _complete_workflow(instance, result, comment=''):
        """完成工作流"""
        instance.status = result
        instance.completed_date = datetime.now(timezone.utc)
        instance.final_result = result
        instance.final_comment = comment
        instance.current_node_id = None
        
        ApprovalEngine._log_action(instance.id, None, 'complete', None,
                                   f'流程完成,结果: {result}')
    
    @staticmethod
    def _terminate_workflow(instance, result, reason):
        """终止工作流"""
        instance.status = 'terminated'
        instance.completed_date = datetime.now(timezone.utc)
        instance.final_result = result
        instance.final_comment = reason
        
        # 取消所有待审批步骤
        pending_steps = ApprovalStep.query.filter_by(
            instance_id=instance.id,
            status='pending'
        ).all()
        
        for step in pending_steps:
            step.status = 'cancelled'
        
        ApprovalEngine._log_action(instance.id, None, 'terminate', None, reason)
    
    @staticmethod
    def _check_node_condition(instance, node):
        """检查节点条件"""
        # 金额阈值检查
        if node.amount_threshold:
            amount = instance.context_data.get('amount', 0)
            if amount < node.amount_threshold:
                if node.skip_if_below_threshold:
                    return False
        
        # 条件表达式检查
        if node.condition_expr:
            # 创建安全的执行环境
            context = instance.context_data.copy()
            context['form_data'] = instance.form_data
            try:
                result = ApprovalEngine._evaluate_condition_expr(node.condition_expr, context)
                return bool(result)
            except Exception as e:
                ApprovalEngine._log_action(instance.id, None, 'condition_error', None,
                                          f'条件表达式错误: {str(e)}')
                return True  # 出错时默认执行

    @staticmethod
    def _evaluate_condition_expr(expr: str, context: dict):
        """安全评估条件表达式，仅允许子集语法（比较、逻辑、算术、索引访问）。

        限制：不允许函数调用、属性访问或导入等危险操作。
        当表达式包含不允许的节点时抛出 ValueError。
        """
        # 解析为 AST
        node = ast.parse(expr, mode='eval')

        # 映射操作符
        binops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
        }
        unops = {
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
            ast.Not: operator.not_,
        }
        boolops = {
            ast.And: all,
            ast.Or: any,
        }
        cmpops = {
            ast.Eq: operator.eq,
            ast.NotEq: operator.ne,
            ast.Lt: operator.lt,
            ast.LtE: operator.le,
            ast.Gt: operator.gt,
            ast.GtE: operator.ge,
            ast.In: lambda a, b: a in b,
            ast.NotIn: lambda a, b: a not in b,
            ast.Is: operator.is_,
            ast.IsNot: operator.is_not,
        }

        def _eval(n):
            # Expression wrapper
            if isinstance(n, ast.Expression):
                return _eval(n.body)
            # Constants (py3.8+)
            if isinstance(n, ast.Constant):
                return n.value
            # Legacy numeric/string nodes - handle n/s for older AST nodes (avoid direct ast.Num/Str checks)
            if hasattr(n, 'n'):
                return n.n
            if hasattr(n, 's'):
                return n.s
            if isinstance(n, ast.Tuple):
                return tuple(_eval(e) for e in n.elts)
            if isinstance(n, ast.List):
                return [_eval(e) for e in n.elts]
            if isinstance(n, ast.Dict):
                return {_eval(k): _eval(v) for k, v in zip(n.keys, n.values)}
            # Names - only allow names present in context or True/False/None
            if isinstance(n, ast.Name):
                if n.id in context:
                    return context[n.id]
                if n.id == 'True':
                    return True
                if n.id == 'False':
                    return False
                if n.id == 'None':
                    return None
                raise ValueError(f"未允许的变量: {n.id}")
            # Disallow function calls and attribute access explicitly
            if isinstance(n, ast.Call):
                raise ValueError('函数调用不允许')
            if isinstance(n, ast.Attribute):
                raise ValueError('属性访问不允许')

            # Subscript like form_data['field'] or dict access
            if isinstance(n, ast.Subscript):
                value = _eval(n.value)
                # slice can be Constant or Name
                idx = None
                if isinstance(n.slice, ast.Constant):
                    idx = n.slice.value
                else:
                    # Python <3.9 index wrapper
                    if hasattr(ast, 'Index') and isinstance(n.slice, ast.Index):
                        idx = _eval(n.slice.value)
                    else:
                        idx = _eval(n.slice)
                try:
                    return value[idx]
                except Exception as e:
                    raise
            # Boolean ops
            if isinstance(n, ast.BoolOp):
                values = [_eval(v) for v in n.values]
                op = type(n.op)
                if op in boolops:
                    if op is ast.And:
                        return all(values)
                    if op is ast.Or:
                        return any(values)
                raise ValueError('不支持的布尔操作')
            # Binary ops
            if isinstance(n, ast.BinOp):
                left = _eval(n.left)
                right = _eval(n.right)
                op_type = type(n.op)
                if op_type in binops:
                    return binops[op_type](left, right)
                raise ValueError('不支持的二元操作')
            # Unary ops
            if isinstance(n, ast.UnaryOp):
                operand = _eval(n.operand)
                op_type = type(n.op)
                if op_type in unops:
                    return unops[op_type](operand)
                raise ValueError('不支持的一元操作')
            # Compare
            if isinstance(n, ast.Compare):
                left = _eval(n.left)
                for op, comp in zip(n.ops, n.comparators):
                    right = _eval(comp)
                    op_type = type(op)
                    if op_type in cmpops:
                        if not cmpops[op_type](left, right):
                            return False
                        left = right
                    else:
                        raise ValueError('不支持的比较操作')
                return True
            # Disallow calls, attributes, comprehensions, lambdas, etc.
            raise ValueError(f'不支持的表达式节点: {type(n).__name__}')

        return _eval(node)
        
        return True
    
    @staticmethod
    def _find_approvers(instance, node):
        """查找审批人"""
        if not node.approval_role_id:
            return []
        
        # 查找有该角色的所有用户
        assignments = UserApprovalRole.query.filter_by(
            role_id=node.approval_role_id,
            is_active=True
        ).all()
        
        approvers = []
        for assignment in assignments:
            user = assignment.user
            if user and user.is_active:
                # 可以添加更多过滤条件,如部门、金额权限等
                approvers.append(user)
        
        return approvers
    
    @staticmethod
    def _select_approver(approvers, node):
        """从候选人中选择审批人(负载均衡)"""
        # 简单实现:返回第一个
        # TODO: 实现负载均衡、轮询等策略
        return approvers[0] if approvers else None
    
    @staticmethod
    def _check_delegate(user_id, order_type, role_id):
        """检查审批代理"""
        now = datetime.now(timezone.utc)
        delegate = ApprovalDelegate.query.filter(
            ApprovalDelegate.user_id == user_id,
            ApprovalDelegate.is_active == True,
            ApprovalDelegate.start_date <= now,
            ApprovalDelegate.end_date >= now
        ).first()
        
        if delegate:
            # 检查代理范围
            if order_type and delegate.order_types:
                if order_type not in delegate.order_types:
                    return None
            
            if role_id and delegate.role_ids:
                if role_id not in delegate.role_ids:
                    return None
            
            return delegate
        
        return None
    
    @staticmethod
    def _send_notification(step, notification_type):
        """发送通知"""
        # TODO: 实现通知功能
        pass
    
    @staticmethod
    def _log_action(instance_id, step_id, action, operator_id, comment):
        """记录操作日志"""
        log = ApprovalLog(
            instance_id=instance_id,
            step_id=step_id,
            action=action,
            operator_id=operator_id,
            comment=comment
        )
        db.session.add(log)
    
    @staticmethod
    def _generate_instance_no(order_type):
        """生成实例编号"""
        prefix = order_type.upper()[:4]
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        # TODO: 添加序列号
        return f'{prefix}-{timestamp}'
    
    @staticmethod
    def _handle_condition_node(instance, node):
        """处理条件节点"""
        # 条件节点根据表达式选择下一个分支
        # TODO: 实现条件分支逻辑
        ApprovalEngine._move_to_next_node(instance, node)
    
    @staticmethod
    def _handle_auto_node(instance, node):
        """处理自动节点"""
        # 自动节点执行自动化操作
        # TODO: 实现自动化逻辑
        ApprovalEngine._move_to_next_node(instance, node)
