"""
审批服务模块
提供审批权限验证、智能审批人路由等核心功能
"""
from app import db
from app.models import User, WorkflowNode
from app.approval_roles import ApprovalRole, UserApprovalRole
from datetime import datetime


class ApprovalPermissionError(Exception):
    """审批权限错误"""
    pass


class ApprovalService:
    """审批服务类"""
    
    @staticmethod
    def check_user_permission(user_id, order_type, amount=None):
        """
        检查用户是否有权限审批指定类型和金额的工单
        
        Args:
            user_id: 用户ID
            order_type: 工单类型 (repair_order, part_request_order, equipment_transfer, etc.)
            amount: 工单金额 (可选)
            
        Returns:
            tuple: (bool, str, list) - (是否有权限, 原因描述, 可用角色列表)
        """
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return False, "用户不存在或未激活", []
        
        # 获取用户的所有有效审批角色
        user_roles = ApprovalService.get_user_approval_roles(user_id)
        
        if not user_roles:
            return False, "用户没有任何审批角色", []
        
        # 工单类型到权限字段的映射
        permission_map = {
            'repair_order': 'can_approve_repair',
            'part_request_order': 'can_approve_part_request',
            'equipment_transfer': 'can_approve_equipment_transfer',
            'equipment_scrap': 'can_approve_equipment_scrap',
            'equipment_loan': 'can_approve_equipment_loan',
            'equipment_application': 'can_approve_equipment_application'
        }
        
        permission_field = permission_map.get(order_type)
        if not permission_field:
            return False, f"未知的工单类型: {order_type}", []
        
        # 筛选有权限的角色
        valid_roles = []
        for role in user_roles:
            # 检查工单类型权限
            has_permission = getattr(role, permission_field, False)
            if not has_permission:
                continue
            
            # 检查金额限制
            if amount is not None and role.max_approval_amount is not None:
                if amount > role.max_approval_amount:
                    continue  # 超出金额限制
            
            valid_roles.append(role)
        
        if not valid_roles:
            if amount is not None:
                return False, f"用户没有权限审批此类型工单或金额超限(¥{amount:.2f})", []
            else:
                return False, f"用户没有权限审批此类型工单", []
        
        return True, "权限验证通过", valid_roles
    
    @staticmethod
    def get_user_approval_roles(user_id):
        """
        获取用户的所有有效审批角色
        
        Returns:
            list: ApprovalRole对象列表
        """
        assignments = UserApprovalRole.query.filter_by(
            user_id=user_id,
            is_active=True
        ).all()
        
        roles = []
        for assignment in assignments:
            if assignment.is_valid():
                role = assignment.role
                if role and role.is_active:
                    roles.append(role)
        
        return roles
    
    @staticmethod
    def find_suitable_approvers(order_type, amount=None, department_id=None, exclude_user_ids=None):
        """
        智能查找合适的审批人
        
        Args:
            order_type: 工单类型
            amount: 工单金额 (可选)
            department_id: 优先部门ID (可选)
            exclude_user_ids: 排除的用户ID列表 (可选)
            
        Returns:
            list: 合适的用户列表,按优先级排序 [(user, role, priority), ...]
        """
        if exclude_user_ids is None:
            exclude_user_ids = []
        
        # 工单类型到权限字段的映射
        permission_map = {
            'repair_order': 'can_approve_repair',
            'part_request_order': 'can_approve_part_request',
            'equipment_transfer': 'can_approve_equipment_transfer',
            'equipment_scrap': 'can_approve_equipment_scrap',
            'equipment_loan': 'can_approve_equipment_loan',
            'equipment_application': 'can_approve_equipment_application'
        }
        
        permission_field = permission_map.get(order_type)
        if not permission_field:
            return []
        
        # 查询所有有该权限的角色
        roles = ApprovalRole.query.filter_by(is_active=True).all()
        valid_roles = [r for r in roles if getattr(r, permission_field, False)]
        
        # 如果有金额限制,筛选满足金额的角色
        if amount is not None:
            valid_roles = [
                r for r in valid_roles 
                if r.max_approval_amount is None or amount <= r.max_approval_amount
            ]
        
        if not valid_roles:
            return []
        
        # 获取拥有这些角色的用户
        suitable_approvers = []
        
        for role in valid_roles:
            # 查找拥有此角色的用户
            assignments = UserApprovalRole.query.filter_by(
                role_id=role.id,
                is_active=True
            ).all()
            
            for assignment in assignments:
                if not assignment.is_valid():
                    continue
                
                user = assignment.user
                if not user or not user.is_active:
                    continue
                
                if user.id in exclude_user_ids:
                    continue
                
                # 计算优先级
                priority = ApprovalService._calculate_priority(
                    user, role, department_id, amount
                )
                
                suitable_approvers.append((user, role, priority))
        
        # 按优先级排序(降序)
        suitable_approvers.sort(key=lambda x: x[2], reverse=True)
        
        return suitable_approvers
    
    @staticmethod
    def _calculate_priority(user, role, department_id=None, amount=None):
        """
        计算审批人优先级
        
        优先级规则:
        1. 同部门 +100
        2. 角色级别 * 1 (级别越高优先级越高)
        3. 金额匹配度 (如果角色有金额限制且接近但高于工单金额,优先级更高)
        """
        priority = 0
        
        # 同部门优先
        if department_id and user.department_id == department_id:
            priority += 100
        
        # 角色级别
        priority += role.level
        
        # 金额匹配度
        if amount is not None and role.max_approval_amount is not None:
            # 金额越接近限额,优先级越高(但要在限额内)
            if amount <= role.max_approval_amount:
                ratio = amount / role.max_approval_amount
                priority += ratio * 50  # 最多加50分
        elif amount is not None and role.max_approval_amount is None:
            # 无限额角色对高金额优先级更高
            priority += 30
        
        return priority
    
    @staticmethod
    def auto_assign_approvers(workflow_node, order_amount=None, department_id=None, exclude_user_ids=None):
        """
        为工作流节点自动分配审批人
        
        Args:
            workflow_node: WorkflowNode对象
            order_amount: 工单金额
            department_id: 工单所属部门
            exclude_user_ids: 排除的用户ID列表
            
        Returns:
            list: 推荐的用户ID列表
        """
        # 如果节点已指定审批人,直接返回
        if workflow_node.approver_user_ids:
            import json
            try:
                ids = json.loads(workflow_node.approver_user_ids)
                if ids:
                    return ids
            except:
                pass
        
        # 如果节点指定了审批角色
        if workflow_node.approval_role_id:
            role = ApprovalRole.query.get(workflow_node.approval_role_id)
            if role:
                # 查找拥有此角色的用户
                assignments = UserApprovalRole.query.filter_by(
                    role_id=role.id,
                    is_active=True
                ).all()
                
                candidates = []
                for assignment in assignments:
                    if assignment.is_valid() and assignment.user.is_active:
                        user = assignment.user
                        if exclude_user_ids and user.id in exclude_user_ids:
                            continue
                        
                        # 检查金额限制
                        if order_amount and role.max_approval_amount:
                            if order_amount > role.max_approval_amount:
                                continue
                        
                        priority = ApprovalService._calculate_priority(
                            user, role, department_id, order_amount
                        )
                        candidates.append((user.id, priority))
                
                # 按优先级排序
                candidates.sort(key=lambda x: x[1], reverse=True)
                
                # 如果是并行审批,返回前N个
                if workflow_node.is_parallel and workflow_node.required_approvals:
                    count = min(workflow_node.required_approvals, len(candidates))
                    return [c[0] for c in candidates[:count]]
                else:
                    # 标准审批,返回优先级最高的
                    return [candidates[0][0]] if candidates else []
        
        # 使用智能路由查找
        # WorkflowNode没有order_type字段，需要通过template关系访问
        order_type = workflow_node.template.order_type if workflow_node.template else None
        if not order_type:
            return []
        
        approvers = ApprovalService.find_suitable_approvers(
            order_type,
            order_amount,
            department_id,
            exclude_user_ids
        )
        
        if not approvers:
            return []
        
        # 返回优先级最高的审批人
        if workflow_node.is_parallel and workflow_node.required_approvals:
            count = min(workflow_node.required_approvals, len(approvers))
            return [a[0].id for a in approvers[:count]]
        else:
            return [approvers[0][0].id]
    
    @staticmethod
    def validate_approval_action(user_id, workflow_node, order_amount=None):
        """
        验证用户是否可以对指定节点进行审批操作
        
        Args:
            user_id: 用户ID
            workflow_node: WorkflowNode对象
            order_amount: 工单金额
            
        Returns:
            tuple: (bool, str) - (是否允许, 原因描述)
        """
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return False, "用户不存在或未激活"
        
        # 检查是否是指定审批人
        if workflow_node.approver_user_ids:
            import json
            try:
                approver_ids = json.loads(workflow_node.approver_user_ids)
                if user_id in approver_ids:
                    return True, "用户是指定审批人"
            except:
                pass
        
        # 检查角色权限
        if workflow_node.approval_role_id:
            # 检查用户是否拥有此角色
            user_roles = ApprovalService.get_user_approval_roles(user_id)
            role_ids = [r.id for r in user_roles]
            
            if workflow_node.approval_role_id not in role_ids:
                return False, "用户没有所需的审批角色"
            
            # 获取角色信息
            role = ApprovalRole.query.get(workflow_node.approval_role_id)
            if not role:
                return False, "审批角色不存在"
            
            # 检查金额限制
            if order_amount and role.max_approval_amount:
                if order_amount > role.max_approval_amount:
                    return False, f"工单金额(¥{order_amount:.2f})超出角色审批限额(¥{role.max_approval_amount:.2f})"
            
            return True, "权限验证通过"
        
        # 使用工单类型检查权限
        # WorkflowNode没有order_type字段，需要通过template关系访问
        order_type = workflow_node.template.order_type if workflow_node.template else None
        if not order_type:
            return False, "无法获取工单类型"
        
        has_permission, reason, valid_roles = ApprovalService.check_user_permission(
            user_id,
            order_type,
            order_amount
        )
        
        if has_permission:
            return True, "权限验证通过"
        else:
            return False, reason
    
    @staticmethod
    def get_next_approvers(order_type, current_sequence, order_amount=None, department_id=None):
        """
        获取下一个审批节点的审批人
        
        Args:
            order_type: 工单类型
            current_sequence: 当前节点序号
            order_amount: 工单金额
            department_id: 工单部门
            
        Returns:
            tuple: (WorkflowNode, list) - (下一个节点, 推荐审批人ID列表)
        """
        # 查找下一个节点（通过join WorkflowTemplate来过滤order_type）
        next_node = WorkflowNode.query.join(WorkflowTemplate).filter(
            WorkflowTemplate.order_type == order_type,
            WorkflowNode.is_active == True,
            WorkflowNode.sequence > current_sequence
        ).order_by(
            WorkflowNode.sequence.asc()
        ).first()
        
        if not next_node:
            return None, []
        
        # 检查金额阈值
        if next_node.amount_threshold and order_amount is not None:
            if next_node.skip_if_below_threshold and order_amount < next_node.amount_threshold:
                # 跳过此节点,查找下一个
                return ApprovalService.get_next_approvers(
                    order_type,
                    next_node.sequence,
                    order_amount,
                    department_id
                )
        
        # 获取推荐审批人
        approver_ids = ApprovalService.auto_assign_approvers(
            next_node,
            order_amount,
            department_id
        )
        
        return next_node, approver_ids
