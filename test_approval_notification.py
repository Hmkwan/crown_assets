#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试审批待办提醒功能
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import ApprovalWorkflow, User, Notification
from app.scheduler import check_pending_approvals

def test_approval_notification():
    """测试审批提醒功能"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("审批待办提醒功能测试")
        print("=" * 60)
        
        # 1. 查询待审批工作流
        print("\n1. 查询待审批工作流...")
        pending_approvals = ApprovalWorkflow.query.filter_by(status='pending').all()
        print(f"   找到 {len(pending_approvals)} 个待审批节点")
        
        if pending_approvals:
            # 按审批人分组统计
            approver_stats = {}
            for approval in pending_approvals:
                if not approval.approver_id:
                    continue
                    
                approver = approval.approver
                if approver.id not in approver_stats:
                    approver_stats[approver.id] = {
                        'username': approver.username,
                        'items': []
                    }
                
                approver_stats[approver.id]['items'].append({
                    'approval_id': approval.id,
                    'order_type': approval.order_type,
                    'order_id': approval.order_id,
                    'step_name': (approval.workflow_node.name if approval.workflow_node else (approval.approval_level or ''))
                })
            
            print(f"\n   涉及 {len(approver_stats)} 个审批人:")
            for approver_id, stats in approver_stats.items():
                print(f"   - @{stats['username']}: {len(stats['items'])} 条待审批")
                for item in stats['items'][:3]:  # 只显示前3条
                    print(f"     · {item['order_type']} (ID:{item['order_id']}) - {item['step_name']}")
                if len(stats['items']) > 3:
                    print(f"     ... 还有 {len(stats['items']) - 3} 条")
        
        # 2. 记录执行前的通知数量
        print("\n2. 执行提醒前的通知统计...")
        before = Notification.query.count()
        print(f"   当前通知总数: {before}")

        # 3. 执行审批提醒任务
        print("\n3. 执行审批提醒任务...")
        try:
            check_pending_approvals()
            print("   ✅ 审批提醒任务执行成功")
        except Exception as e:
            print(f"   ❌ 任务执行失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return

        # 4. 检查新增的通知
        print("\n4. 检查新增的通知...")
        after = Notification.query.count()
        new_notifications = after - before
        print(f"   新增通知数: {new_notifications}")

        if new_notifications > 0:
            # 显示新增的通知
            print("\n   新增通知详情:")
        
        print("=" * 60)
        print("测试完成!")
        print("=" * 60)
        
        # 5. 显示总结
        print("\n📊 总结:")
        print(f"   - 待审批节点: {len(pending_approvals)} 个")
        if pending_approvals:
            print(f"   - 涉及审批人: {len(approver_stats)} 人")
        
        if new_notifications == 0 and len(pending_approvals) > 0:
            print("\n⚠️  注意: 有待审批节点但未发送通知,可能的原因:")
            print("   - 审批节点没有指定审批人(approver_id为空)")
            print("   - 审批提醒任务配置被禁用")
            print("   - 任务执行中遇到异常")


if __name__ == '__main__':
    test_approval_notification()
