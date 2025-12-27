#!/usr/bin/env python
"""
测试审批页面现在支持设备借用类型
"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import User, Equipment, EquipmentLoan, ApprovalWorkflow, Department
from datetime import datetime, timedelta, timezone

def test_approvals_page_with_loan():
    """测试审批页面能够加载并显示贷款批准"""
    app = create_app()
    
    with app.app_context():
        # 清空现有数据
        db.drop_all()
        db.create_all()
        
        import uuid
        # 创建部门（使用唯一名称避免与系统默认/初始化数据冲突）
        dept_name = 'IT部门-' + uuid.uuid4().hex[:8]
        dept = Department(name=dept_name)
        db.session.add(dept)
        db.session.commit()
        
        # 创建用户（使用唯一用户名避免冲突）
        requester_username = 'requester_' + uuid.uuid4().hex[:8]
        approver_username = 'approver_' + uuid.uuid4().hex[:8]
        requester = User(username=requester_username, email=f'{requester_username}@test.com', department=dept_name, is_admin=False)
        requester.set_password('test')
        
        approver = User(username=approver_username, email=f'{approver_username}@test.com', department=dept_name, is_admin=True)
        approver.set_password('test')
        
        db.session.add(requester)
        db.session.add(approver)
        db.session.commit()
        
        # 创建设备
        equipment_serial = 'SN' + uuid.uuid4().hex[:8]
        equipment = Equipment(
            name='笔记本电脑',
            type='电子设备',
            model='ThinkPad',
            serial_number=equipment_serial,
            status='available'
        )
        db.session.add(equipment)
        db.session.commit()
        
        # 创建借用请求
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=7)
        
        loan = EquipmentLoan(
            equipment_id=equipment.id,
            requester_id=requester.id,
            requester_dept=dept_name,
            start_date=start_date,
            end_date=end_date,
            status='submitted'
        )
        db.session.add(loan)
        db.session.commit()
        
        # 创建批准工作流
        approval = ApprovalWorkflow(
            order_type='equipment_loan',
            order_id=loan.id,
            approver_id=approver.id,
            approval_level='admin',
            status='pending'
        )
        db.session.add(approval)
        db.session.commit()
        
        print(f"✓ 创建了设备借用请求：{loan.id}")
        print(f"✓ 创建了批准工作流：{approval.id}")
        
        # 现在使用测试客户端访问审批页面
        with app.test_client() as client:
            # 登录为审批者
            response = client.post('/auth/login', data={
                'username': approver_username,
                'password': 'test'
            }, follow_redirects=True)
            print(f"✓ 以审批者身份登录")
            
            # 访问审批页面（跟随重定向）
            response = client.get('/approvals', follow_redirects=True)
            print(f"✓ 访问审批页面，最终状态码: {response.status_code}")
            
            # 检查页面内容
            page_text = response.get_data(as_text=True)
            
            if '设备借用审批' in page_text:
                print(f"✓ 页面包含'设备借用审批'部分")
            else:
                print(f"✗ 页面不包含'设备借用审批'部分")
            
            if '笔记本电脑' in page_text:
                print(f"✓ 页面显示了借用的设备")
            else:
                print(f"✗ 页面不显示借用的设备")
            
            if 'requester' in page_text or 'loan' in page_text:
                print(f"✓ 页面包含相关数据")
            else:
                print(f"✗ 页面未包含相关数据")
            
            print("\n✓ 审批页面测试完成！")

if __name__ == '__main__':
    test_approvals_page_with_loan()
