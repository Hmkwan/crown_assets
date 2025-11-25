#!/usr/bin/env python
"""
详细调试审批页面的 loan_orders 加载
"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import User, Equipment, EquipmentLoan, ApprovalWorkflow, Department
from datetime import datetime, timedelta, timezone

def debug_approvals():
    """调试审批页面"""
    app = create_app()
    # 在测试中禁用 CSRF 以便使用 test_client 提交表单
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        # 清空现有数据
        db.drop_all()
        db.create_all()
        
        # 创建部门
        dept = Department(name='IT部门')
        db.session.add(dept)
        db.session.commit()
        
        # 创建用户
        approver = User(username='approver_test', email='approver@test.com', department='IT部门', is_admin=True)
        approver.set_password('test')
        
        requester = User(username='requester_test', email='requester@test.com', department='IT部门', is_admin=False)
        requester.set_password('test')
        
        db.session.add(approver)
        db.session.add(requester)
        db.session.commit()
        
        # 创建设备
        equipment = Equipment(
            name='笔记本电脑',
            type='电子设备',
            model='ThinkPad',
            serial_number='SN123456',
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
            requester_dept='IT部门',
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
        
        print(f"✓ 创建了用户: {approver.username} (ID: {approver.id})")
        print(f"✓ 创建了设备借用请求: {loan.id}")
        print(f"✓ 创建了批准工作流: {approval.id}")
        
        # 查询数据库中的待处理审批
        pending = ApprovalWorkflow.query.filter_by(
            approver_id=approver.id,
            status='pending'
        ).all()
        print(f"\n待处理审批数量: {len(pending)}")
        for p in pending:
            print(f"  - 类型: {p.order_type}, ID: {p.order_id}, 批准者: {p.approver_id}")
        
        # 直接调用路由逻辑来调试
        from flask_login import current_user
        from app.main.routes import approvals as approvals_view
        
        print("\n使用测试客户端...")
        with app.test_client() as client:
            # 登录
            response = client.post('/auth/login', data={
                'username': 'approver_test',
                'password': 'test'
            }, follow_redirects=True)
            
            print(f"✓ 登录状态码: 200")
            
            # 访问审批页面
            response = client.get('/approvals', follow_redirects=True)
            page_text = response.get_data(as_text=True)
            
            print(f"\n审批页面状态码: {response.status_code}")
            
            # 检查关键文本
            if '设备借用审批' in page_text:
                print("✓ 页面包含 '设备借用审批' 标题")
            else:
                print("✗ 页面未包含 '设备借用审批' 标题")
            
            if '笔记本电脑' in page_text:
                print("✓ 页面包含设备名称")
            else:
                print("✗ 页面未包含设备名称")
            
            if 'requester_test' in page_text or 'requester' in page_text.lower():
                print("✓ 页面包含申请人信息")
            else:
                print("✗ 页面未包含申请人信息")
            
            # 查看页面中的所有标题
            print("\n页面中的所有审批卡片标题:")
            import re
            titles = re.findall(r'<h5>(.*?)</h5>', page_text)
            for title in titles:
                print(f"  - {title}")
            
            # 打印页面前 2000 个字符以供调试
            print("\n页面前 2000 个字符:")
            print(page_text[:2000])
            # 打印页面长度和关键词是否存在
            print(f"\n页面总长度: {len(page_text)}")
            for kw in ['待审批工单', '设备借用审批', 'loan_orders', 'loan', '待审批']:
                print(f"包含关键词 '{kw}'?: {kw in page_text}")
            # 将完整页面写入文件以便人工查看
            with open('debug_approvals_output.html', 'w', encoding='utf-8') as f:
                f.write(page_text)
            print("已将完整页面写入 debug_approvals_output.html")

if __name__ == '__main__':
    debug_approvals()
