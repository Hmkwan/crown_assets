#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工作流配置示例：为特定节点分配特定用户

这个脚本演示了如何为审批流程中的特定节点分配特定的用户作为审批人，
而不是仅依赖基于角色的自动查找。

示例场景：
1. 为维修工单的"管理员审批"节点分配特定的管理员用户
2. 为配件申请的"部门领导审批"节点分配跨部门的领导
3. 创建"并行审批"配置（需要多个人同时批准）
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from app import create_app, db
from app.approval_models import WorkflowNode, WorkflowTemplate
from app.models import User
from datetime import datetime

def list_users_by_role(app, role=None):
    """列出系统中的所有用户（按角色分类）"""
    with app.app_context():
        if role:
            users = User.query.filter_by(role=role, is_active=True).all()
            print(f"\n{role} 角色的用户:")
        else:
            users = User.query.filter_by(is_active=True).all()
            print(f"\n系统中的所有用户:")
        
        for user in users:
            print(f"  ID: {user.id:3d} | 用户名: {user.username:15s} | 角色: {user.role:15s} | 部门: {user.get_department_name()}")
        
        return users

def assign_specific_approver_to_node(app, node_id, approver_user_id):
    """为特定节点分配特定的审批人"""
    with app.app_context():
        node = WorkflowNode.query.get(node_id)
        if not node:
            print(f"✗ 节点 ID {node_id} 不存在")
            return False
        
        user = User.query.get(approver_user_id)
        if not user:
            print(f"✗ 用户 ID {approver_user_id} 不存在")
            return False
        
        node.approver_user_id = approver_user_id
        db.session.commit()
        
        print(f"✓ 已为节点 '{node.name}' (ID: {node.id}) 分配审批人: {user.username} (ID: {approver_user_id})")
        return True

def create_parallel_approval_node(app, name, order_type, sequence, approver_user_ids, role_required='admin'):
    """创建并行审批节点（需要多个人批准）"""
    with app.app_context():
        if len(approver_user_ids) < 2:
            print("✗ 并行审批至少需要 2 个审批人")
            return None
        
        # 验证所有用户存在
        for uid in approver_user_ids:
            user = User.query.get(uid)
            if not user:
                print(f"✗ 用户 ID {uid} 不存在")
                return None
        
        # 创建并行审批节点（通常只创建一个主节点，然后为其分配第一个审批人）
        node = WorkflowNode(
            name=name,
            order_type=order_type,
            role_required=role_required,
            sequence=sequence,
            is_active=True,
            is_parallel=True,  # 标记为并行审批
            required_approvals=len(approver_user_ids),  # 需要所有审批人批准
            approver_user_id=approver_user_ids[0],  # 分配第一个审批人
            actions_on_reject='{"return_to": "requester"}'  # 拒绝时返回给申请人
        )
        db.session.add(node)
        db.session.commit()
        
        user_names = [User.query.get(uid).username for uid in approver_user_ids]
        print(f"✓ 创建并行审批节点: {name}")
        print(f"  需要的批准人数: {len(approver_user_ids)}")
        print(f"  审批人: {', '.join(user_names)}")
        
        return node

def print_node_configuration(app, order_type=None):
    """打印节点配置信息"""
    with app.app_context():
        print("\n" + "="*80)
        print("当前工作流节点配置")
        print("="*80)
        
        if order_type:
            nodes = WorkflowNode.query.filter_by(order_type=order_type).order_by(WorkflowNode.sequence).all()
            print(f"\n订单类型: {order_type}")
        else:
            nodes = WorkflowNode.query.order_by(WorkflowNode.order_type, WorkflowNode.sequence).all()
        
        current_type = None
        for node in nodes:
            if order_type is None and node.order_type != current_type:
                current_type = node.order_type
                print(f"\n【{current_type}】")
            
            approver_info = ""
            if node.approver_user_id:
                approver = User.query.get(node.approver_user_id)
                if approver:
                    approver_info = f" → 指定审批人: {approver.username}"
                else:
                    approver_info = " → 指定审批人已删除"
            else:
                approver_info = f" → 根据角色匹配: {node.role_required}"
            
            parallel_info = " (并行审批)" if node.is_parallel else ""
            print(f"  {node.sequence}. {node.name}{approver_info}{parallel_info}")
        
        print("\n" + "="*80 + "\n")

def demonstrate_scenarios(app):
    """演示各种工作流配置场景"""
    print("\n" + "="*80)
    print("工作流配置示例场景")
    print("="*80)
    
    with app.app_context():
        # 获取不同角色的用户示例
        admins = User.query.filter_by(role='admin', is_active=True).all()
        dept_heads = User.query.filter_by(role='department_head', is_active=True).all()
        technicians = User.query.filter_by(role='technician', is_active=True).all()
        
        print("\n【场景 1】基于角色的标准审批（默认配置）")
        print("  - 部门领导审批 (角色匹配)")
        print("  - 管理员审批 (角色匹配)")
        print("  - 技术员处理 (角色匹配)")
        print("  说明: 系统会根据申请人的部门自动查找相应角色的用户")
        
        print("\n【场景 2】特定用户审批")
        print("  - 部门领导审批 (角色匹配)")
        if admins:
            print(f"  - 管理员审批 → 指定用户: {admins[0].username} (ID: {admins[0].id})")
            print(f"  说明: 所有工单的管理员审批阶段都由 {admins[0].username} 处理")
        
        print("\n【场景 3】并行审批（需要多人同时批准）")
        if len(admins) >= 2:
            print(f"  - 需要 {min(2, len(admins))} 个管理员同时批准")
            print(f"  - 审批人: {', '.join([a.username for a in admins[:2]])}")
            print("  说明: 必须所有指定审批人都批准，工单才能进入下一步")
        
        print("\n【场景 4】跨部门审批")
        if dept_heads:
            print(f"  - 部门领导审批 → 指定跨部门审批人: {dept_heads[0].username}")
            print("  说明: 某些工单需要特定部门的领导审批，而不是申请人所在部门的领导")
        
        print("\n【场景 5】拒绝时自动处理")
        print("  - 配置 actions_on_reject: {\"return_to\": \"requester\"}")
        print("  说明: 工单被拒绝时自动返回给申请人，而不是直接取消")
        print("="*80 + "\n")

if __name__ == '__main__':
    app = create_app()
    
    print("工作流配置示例和演示\n")
    
    # 1. 列出所有用户
    print("\n【步骤 1】查看系统中的用户")
    list_users_by_role(app)
    
    # 2. 打印当前节点配置
    print("\n【步骤 2】查看当前工作流节点配置")
    print_node_configuration(app)
    
    # 3. 演示配置场景
    print("\n【步骤 3】工作流配置场景说明")
    demonstrate_scenarios(app)
    
    # 4. 交互式配置示例（如果需要）
    print("\n【步骤 4】配置示例")
    print("""
如要为特定节点分配特定用户，可使用以下方式：

方式 A: 使用管理员 UI
  1. 访问 /workflow_nodes 页面
  2. 点击"添加节点"或"编辑"按钮
  3. 在"指定审批人"下拉菜单中选择用户
  4. 保存配置

方式 B: 使用 Python 脚本
  from scripts.config_workflow_examples import assign_specific_approver_to_node
  app = create_app()
  assign_specific_approver_to_node(app, node_id=1, approver_user_id=5)
  
方式 C: SQL 直接更新
  UPDATE workflow_node SET approver_user_id = 5 WHERE id = 1;
    """)
    
    print("✓ 演示完成！")
