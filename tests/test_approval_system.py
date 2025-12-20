"""
审批系统单元测试
测试审批流程引擎的核心功能
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db, get_beijing_now
from app.approval_models import (
    WorkflowTemplate, WorkflowNode, ApprovalInstance,
    ApprovalStep, ApprovalLog, ApprovalDelegate
)
from app.approval_engine import ApprovalEngine
from app.models import User
from app.approval_roles import ApprovalRole, UserApprovalRole
from datetime import datetime, timedelta
import json


class ApprovalEngineTestCase(unittest.TestCase):
    """审批引擎测试"""
    
    def setUp(self):
        """每个测试前的设置"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # 生成唯一标识符
        import random
        self.test_id = random.randint(10000, 99999)
        
        # 创建测试用户
        self.user1 = User(username=f'test_user1_{self.test_id}', email=f'test1_{self.test_id}@example.com')
        self.user1.set_password('password')
        db.session.add(self.user1)
        
        self.user2 = User(username=f'test_user2_{self.test_id}', email=f'test2_{self.test_id}@example.com')
        self.user2.set_password('password')
        db.session.add(self.user2)
        
        self.user3 = User(username=f'test_user3_{self.test_id}', email=f'test3_{self.test_id}@example.com')
        self.user3.set_password('password')
        db.session.add(self.user3)
        
        # 创建审批角色(使用唯一code)
        self.role_dept = ApprovalRole(
            name='部门主管',
            code=f'department_head_{self.test_id}',
            icon='fa-user-tie',
            description='部门主管'
        )
        db.session.add(self.role_dept)
        
        self.role_finance = ApprovalRole(
            name='财务',
            code=f'finance_{self.test_id}',
            icon='fa-dollar-sign',
            description='财务审批'
        )
        db.session.add(self.role_finance)
        
        db.session.flush()
        
        # 分配角色
        user_role1 = UserApprovalRole(user_id=self.user2.id, role_id=self.role_dept.id, is_active=True)
        user_role2 = UserApprovalRole(user_id=self.user3.id, role_id=self.role_finance.id, is_active=True)
        db.session.add(user_role1)
        db.session.add(user_role2)
        
        db.session.commit()
    
    def tearDown(self):
        """每个测试后的清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_simple_workflow(self):
        """测试创建简单工作流"""
        # 创建模板
        template = WorkflowTemplate(
            code='test_workflow_v1',
            name='测试工作流',
            order_type='test_order',
            version=1,
            is_active=True,
            is_default=True
        )
        db.session.add(template)
        db.session.flush()
        
        # 创建节点
        node1 = WorkflowNode(
            template_id=template.id,
            code='NODE1',
            name='部门审批',
            sequence=1,
            node_type='approval',
            approval_role_id=self.role_dept.id,
            is_active=True
        )
        db.session.add(node1)
        db.session.commit()
        
        # 启动工作流
        instance = ApprovalEngine.start_workflow(
            order_type='test_order',
            order_id=1,
            requester_id=self.user1.id
        )
        
        self.assertIsNotNone(instance)
        self.assertEqual(instance.status, 'in_progress')
        self.assertEqual(instance.current_node_id, node1.id)
        
        # 检查是否创建了审批步骤
        steps = ApprovalStep.query.filter_by(instance_id=instance.id).all()
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0].approver_id, self.user2.id)
        self.assertEqual(steps[0].status, 'pending')
    
    def test_approve_workflow(self):
        """测试审批通过流程"""
        # 创建模板和节点
        template = WorkflowTemplate(
            code='test_approve_v1',
            name='测试审批',
            order_type='test_approve',
            version=1,
            is_active=True,
            is_default=True
        )
        db.session.add(template)
        db.session.flush()
        
        node1 = WorkflowNode(
            template_id=template.id,
            code='NODE1',
            name='部门审批',
            sequence=1,
            node_type='approval',
            approval_role_id=self.role_dept.id,
            is_active=True
        )
        db.session.add(node1)
        db.session.commit()
        
        # 启动工作流
        instance = ApprovalEngine.start_workflow(
            order_type='test_approve',
            order_id=2,
            requester_id=self.user1.id
        )
        
        # 获取待审批步骤
        step = ApprovalStep.query.filter_by(
            instance_id=instance.id,
            status='pending'
        ).first()
        
        # 审批通过
        ApprovalEngine.approve_step(
            step_id=step.id,
            approver_id=self.user2.id,
            comment='同意'
        )
        
        # 刷新实例
        db.session.refresh(instance)
        
        # 检查状态
        self.assertEqual(instance.status, 'approved')
        
        # 检查步骤状态
        db.session.refresh(step)
        self.assertEqual(step.status, 'approved')
        self.assertEqual(step.comment, '同意')
        self.assertIsNotNone(step.approved_date)
    
    def test_reject_workflow(self):
        """测试审批拒绝流程"""
        # 创建模板和节点
        template = WorkflowTemplate(
            code='test_reject_v1',
            name='测试拒绝',
            order_type='test_reject',
            version=1,
            is_active=True,
            is_default=True
        )
        db.session.add(template)
        db.session.flush()
        
        node1 = WorkflowNode(
            template_id=template.id,
            code='NODE1',
            name='部门审批',
            sequence=1,
            node_type='approval',
            approval_role_id=self.role_dept.id,
            is_active=True
        )
        db.session.add(node1)
        db.session.commit()
        
        # 启动工作流
        instance = ApprovalEngine.start_workflow(
            order_type='test_reject',
            order_id=3,
            requester_id=self.user1.id
        )
        
        # 获取待审批步骤
        step = ApprovalStep.query.filter_by(
            instance_id=instance.id,
            status='pending'
        ).first()
        
        # 审批拒绝
        ApprovalEngine.reject_step(
            step_id=step.id,
            approver_id=self.user2.id,
            comment='不同意'
        )
        
        # 刷新实例
        db.session.refresh(instance)
        
        # 检查状态
        self.assertEqual(instance.status, 'terminated')
        
        # 检查步骤状态
        db.session.refresh(step)
        self.assertEqual(step.status, 'rejected')
    
    def test_multi_level_approval(self):
        """测试多级审批"""
        # 创建模板
        template = WorkflowTemplate(
            code='test_multi_v1',
            name='测试多级',
            order_type='test_multi',
            version=1,
            is_active=True,
            is_default=True
        )
        db.session.add(template)
        db.session.flush()
        
        # 创建两个节点
        node1 = WorkflowNode(
            template_id=template.id,
            code='NODE1',
            name='部门审批',
            sequence=1,
            node_type='approval',
            approval_role_id=self.role_dept.id,
            is_active=True
        )
        db.session.add(node1)
        
        node2 = WorkflowNode(
            template_id=template.id,
            code='NODE2',
            name='财务审批',
            sequence=2,
            node_type='approval',
            approval_role_id=self.role_finance.id,
            is_active=True
        )
        db.session.add(node2)
        db.session.commit()
        
        # 启动工作流
        instance = ApprovalEngine.start_workflow(
            order_type='test_multi',
            order_id=4,
            requester_id=self.user1.id
        )
        
        # 第一级审批
        step1 = ApprovalStep.query.filter_by(
            instance_id=instance.id,
            node_id=node1.id
        ).first()
        
        ApprovalEngine.approve_step(
            step_id=step1.id,
            approver_id=self.user2.id,
            comment='部门同意'
        )
        
        # 刷新实例
        db.session.refresh(instance)
        
        # 应该还在进行中
        self.assertEqual(instance.status, 'in_progress')
        
        # 应该移到第二个节点
        self.assertEqual(instance.current_node_id, node2.id)
        
        # 第二级审批
        step2 = ApprovalStep.query.filter_by(
            instance_id=instance.id,
            node_id=node2.id,
            status='pending'
        ).first()
        
        self.assertIsNotNone(step2)
        
        ApprovalEngine.approve_step(
            step_id=step2.id,
            approver_id=self.user3.id,
            comment='财务同意'
        )
        
        # 刷新实例
        db.session.refresh(instance)
        
        # 应该已完成
        self.assertEqual(instance.status, 'approved')
    
    def test_delegate_approval(self):
        """测试审批委托"""
        # 创建委托
        delegate = ApprovalDelegate(
            user_id=self.user2.id,
            delegate_to_id=self.user3.id,
            start_date=get_beijing_now() - timedelta(days=1),
            end_date=get_beijing_now() + timedelta(days=7),
            order_types=['test_delegate'],
            is_active=True,
            reason='出差'
        )
        db.session.add(delegate)
        
        # 创建模板和节点
        template = WorkflowTemplate(
            code='test_delegate_v1',
            name='测试委托',
            order_type='test_delegate',
            version=1,
            is_active=True,
            is_default=True
        )
        db.session.add(template)
        db.session.flush()
        
        node1 = WorkflowNode(
            template_id=template.id,
            code='NODE1',
            name='部门审批',
            sequence=1,
            node_type='approval',
            approval_role_id=self.role_dept.id,
            is_active=True
        )
        db.session.add(node1)
        db.session.commit()
        
        # 启动工作流
        instance = ApprovalEngine.start_workflow(
            order_type='test_delegate',
            order_id=5,
            requester_id=self.user1.id
        )
        
        # 检查审批人是否被委托
        step = ApprovalStep.query.filter_by(
            instance_id=instance.id,
            status='pending'
        ).first()
        
        # 应该分配给被委托人
        self.assertEqual(step.approver_id, self.user3.id)
        # 注意:当前实现中委托是在查找审批人时处理的,不会在步骤中记录委托关系


class ApprovalNotificationTestCase(unittest.TestCase):
    """审批通知测试"""
    
    def setUp(self):
        """测试前设置"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # 生成唯一标识符
        import random
        self.test_id = random.randint(10000, 99999)
        
        # 创建测试用户
        self.user = User(username=f'test_user_{self.test_id}', email=f'test_{self.test_id}@example.com')
        self.user.set_password('password')
        db.session.add(self.user)
        db.session.commit()
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_notification_creation(self):
        """测试通知创建"""
        from app.models import Notification
        from app.services.approval_notification_service import ApprovalNotificationService
        
        # 模拟创建通知(需要有实例和步骤)
        # 这里简化测试,直接创建通知
        notification = Notification(
            user_id=self.user.id,
            title='测试通知',
            message='这是一条测试通知',
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()
        
        # 验证通知
        saved_notification = Notification.query.filter_by(user_id=self.user.id).first()
        self.assertIsNotNone(saved_notification)
        self.assertEqual(saved_notification.title, '测试通知')
        self.assertFalse(saved_notification.is_read)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试用例
    suite.addTests(loader.loadTestsFromTestCase(ApprovalEngineTestCase))
    suite.addTests(loader.loadTestsFromTestCase(ApprovalNotificationTestCase))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
