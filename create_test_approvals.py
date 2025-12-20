#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建测试审批数据
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import (
    User, RepairOrder, ApprovalWorkflow, Equipment, 
    EquipmentLoan, EquipmentApplication
)
from datetime import datetime

def create_test_approvals():
    """创建测试审批数据"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("创建测试审批数据")
        print("=" * 60)
        
        # 1. 查找测试用户
        print("\n1. 查找用户...")
        admin_user = User.query.filter_by(username='admin').first()
        manager_user = User.query.filter_by(role='department_manager').first()
        
        if not admin_user:
            print("   ❌ 未找到admin用户")
            return
        
        if not manager_user:
            # 创建一个部门经理
            print("   创建测试部门经理...")
            manager_user = User(
                username='test_manager',
                email='test_manager@example.com',
                role='department_manager',
                department='测试部门'
            )
            manager_user.set_password('123456')
            db.session.add(manager_user)
            db.session.commit()
        
        print(f"   管理员: {admin_user.username}")
        print(f"   经理: {manager_user.username}")
        
        # 2. 创建测试维修工单
        print("\n2. 创建测试维修工单...")
        equipment = Equipment.query.first()
        if not equipment:
            print("   ❌ 未找到设备")
            return
        
        repair_order = RepairOrder(
            equipment_id=equipment.id,
            description='测试故障 - 用于审批提醒测试',
            requester_id=admin_user.id,
            status='submitted',
            created_date=datetime.now()
        )
        db.session.add(repair_order)
        db.session.flush()
        
        # 创建审批流程节点
        approval1 = ApprovalWorkflow(
            order_type='repair_order',
            order_id=repair_order.id,
            step_order=1,
            step_name='部门经理审批',
            approver_id=manager_user.id,
            status='pending',
            created_at=datetime.now()
        )
        db.session.add(approval1)
        
        approval2 = ApprovalWorkflow(
            order_type='repair_order',
            order_id=repair_order.id,
            step_order=2,
            step_name='管理员审批',
            approver_id=admin_user.id,
            status='waiting',
            created_at=datetime.now()
        )
        db.session.add(approval2)
        
        print(f"   ✅ 创建维修工单 ID={repair_order.id}")
        print(f"      - 节点1: {approval1.step_name} (审批人: {manager_user.username})")
        print(f"      - 节点2: {approval2.step_name} (审批人: {admin_user.username})")
        
        # 3. 创建测试借用申请
        print("\n3. 创建测试借用申请...")
        loan = EquipmentLoan(
            equipment_id=equipment.id,
            applicant_id=admin_user.id,
            start_date=datetime.now(),
            planned_return_date=datetime(2025, 12, 10),
            purpose='测试借用 - 用于审批提醒测试',
            status='pending',
            created_at=datetime.now()
        )
        db.session.add(loan)
        db.session.flush()
        
        approval3 = ApprovalWorkflow(
            order_type='equipment_loan',
            order_id=loan.id,
            step_order=1,
            step_name='部门经理审批',
            approver_id=manager_user.id,
            status='pending',
            created_at=datetime.now()
        )
        db.session.add(approval3)
        
        print(f"   ✅ 创建借用申请 ID={loan.id}")
        print(f"      - 节点1: {approval3.step_name} (审批人: {manager_user.username})")
        
        # 4. 创建测试设备申请
        print("\n4. 创建测试设备申请...")
        application = EquipmentApplication(
            equipment_name='测试设备',
            specifications='测试规格',
            quantity=1,
            estimated_price=1000.0,
            purpose='测试申请 - 用于审批提醒测试',
            applicant_id=admin_user.id,
            status='pending',
            created_at=datetime.now()
        )
        db.session.add(application)
        db.session.flush()
        
        approval4 = ApprovalWorkflow(
            order_type='equipment_application',
            order_id=application.id,
            step_order=1,
            step_name='管理员审批',
            approver_id=admin_user.id,
            status='pending',
            created_at=datetime.now()
        )
        db.session.add(approval4)
        
        print(f"   ✅ 创建设备申请 ID={application.id}")
        print(f"      - 节点1: {approval4.step_name} (审批人: {admin_user.username})")
        
        # 提交事务
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("测试数据创建完成!")
        print("=" * 60)
        print("\n📊 汇总:")
        print(f"   - 维修工单: 1 个 (2个审批节点)")
        print(f"   - 借用申请: 1 个 (1个审批节点)")
        print(f"   - 设备申请: 1 个 (1个审批节点)")
        print(f"\n   涉及审批人:")
        print(f"   - {manager_user.username}: 2 条待审批")
        print(f"   - {admin_user.username}: 1 条待审批")
        print("\n   现在可以运行 test_approval_notification.py 测试提醒功能")


if __name__ == '__main__':
    create_test_approvals()
