"""创建测试数据并测试所有审批流程"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import (User, Equipment, SparePart, SparePartType,
                        PartRequestOrder, EquipmentApplication,
                        EquipmentLoan, EquipmentTransfer, EquipmentScrap)
from datetime import datetime, timedelta, timezone

app = create_app()

with app.app_context():
    print("\n" + "="*80)
    print("创建测试数据")
    print("="*80 + "\n")
    
    # 获取用户
    admin = User.query.filter_by(username='admin').first()
    zhuxu = User.query.filter_by(username='朱绪').first()
    chensong = User.query.filter_by(username='陈松').first()
    
    print(f"用户: admin={admin.id if admin else None}, 朱绪={zhuxu.id if zhuxu else None}, 陈松={chensong.id if chensong else None}")
    
    # 检查是否有配件
    part_count = SparePart.query.count()
    if part_count == 0:
        print("\n创建配件数据...")
        # 创建配件类型
        part_type = SparePartType(
            name='电脑配件',
            description='电脑相关配件'
        )
        db.session.add(part_type)
        db.session.flush()
        
        # 创建配件
        parts_data = [
            ('内存条', 'MEM-DDR4-8GB', 299.00, 50),
            ('硬盘', 'SSD-512GB', 399.00, 30),
            ('键盘', 'KB-MECH-01', 199.00, 100),
            ('鼠标', 'MOUSE-WIRELESS', 89.00, 150),
        ]
        
        for name, part_num, price, stock in parts_data:
            part = SparePart(
                name=name,
                part_number=part_num,
                type_id=part_type.id,
                price=price,
                stock_quantity=stock,
                min_stock_level=10,
                department='企管部',
                is_public=True
            )
            db.session.add(part)
        db.session.commit()
        print(f"   - 已创建 {len(parts_data)} 个配件")
    
    # 检查是否有设备
    eq_count = Equipment.query.count()
    if eq_count <= 1:
        print("\n创建设备数据...")
        equipments_data = [
            ('台式机-001', '企管部', '在用'),
            ('台式机-002', '信息部', '在用'),
            ('打印机-001', '企管部', '在用'),
            ('扫描仪-001', '信息部', '维修中'),
        ]
        
        for name, dept, status in equipments_data:
            eq = Equipment(
                name=name,
                department=dept,
                status=status
            )
            db.session.add(eq)
        db.session.commit()
        print(f"   - 已创建 {len(equipments_data)} 个设备")
    
    print("\n" + "="*80)
    print("创建测试工单")
    print("="*80 + "\n")
    
    # 1. 配件申请
    print("1. 创建配件申请工单...")
    memory = SparePart.query.filter_by(part_number='MEM-DDR4-8GB').first()
    if memory and zhuxu and not PartRequestOrder.query.filter_by(requester_id=zhuxu.id).first():
        part_order = PartRequestOrder(
            requester_id=zhuxu.id,
            part_name=memory.name,
            part_number=memory.part_number,
            quantity=2,
            reason='部门电脑升级需要',
            urgency='normal',
            status='submitted'
        )
        db.session.add(part_order)
        db.session.commit()
        print(f"   - 工单ID: {part_order.id}")
    else:
        existing = PartRequestOrder.query.filter_by(requester_id=zhuxu.id).first()
        print(f"   - 已存在工单 #{existing.id if existing else 'N/A'}")
    
    # 2. 设备申请
    print("\n2. 创建设备申请工单...")
    if zhuxu and not EquipmentApplication.query.filter_by(requester_id=zhuxu.id).first():
        eq_app = EquipmentApplication(
            requester_id=zhuxu.id,
            equipment_type='笔记本电脑',
            specifications='i5处理器, 16GB内存, 512GB SSD',
            quantity=1,
            reason='新员工入职需要',
            urgency='normal',
            status='submitted'
        )
        db.session.add(eq_app)
        db.session.commit()
        print(f"   - 工单ID: {eq_app.id}")
    else:
        existing = EquipmentApplication.query.filter_by(requester_id=zhuxu.id).first()
        print(f"   - 已存在工单 #{existing.id if existing else 'N/A'}")
    
    # 3. 设备借用
    print("\n3. 创建设备借用工单...")
    printer = Equipment.query.filter_by(name='打印机-001').first()
    if printer and zhuxu and not EquipmentLoan.query.filter_by(requester_id=zhuxu.id).first():
        loan = EquipmentLoan(
            requester_id=zhuxu.id,
            requester_dept='企管部',
            equipment_id=printer.id,
            reason='临时会议需要打印资料',
            start_date=datetime.now(timezone.utc).date(),
            end_date=(datetime.now(timezone.utc) + timedelta(days=7)).date(),
            status='submitted'
        )
        db.session.add(loan)
        db.session.commit()
        print(f"   - 工单ID: {loan.id}")
    else:
        existing = EquipmentLoan.query.filter_by(requester_id=zhuxu.id).first()
        print(f"   - 已存在工单 #{existing.id if existing else 'N/A'}")
    
    # 4. 设备调拨
    print("\n4. 创建设备调拨工单...")
    desktop = Equipment.query.filter_by(name='台式机-001').first()
    if desktop and zhuxu and not EquipmentTransfer.query.filter_by(requester_id=zhuxu.id).first():
        transfer = EquipmentTransfer(
            requester_id=zhuxu.id,
            equipment_id=desktop.id,
            from_department='企管部',
            to_department='信息部',
            reason='部门调整,设备重新分配',
            status='submitted'
        )
        db.session.add(transfer)
        db.session.commit()
        print(f"   - 工单ID: {transfer.id}")
    else:
        existing = EquipmentTransfer.query.filter_by(requester_id=zhuxu.id).first()
        print(f"   - 已存在工单 #{existing.id if existing else 'N/A'}")
    
    # 5. 设备报废
    print("\n5. 创建设备报废工单...")
    scanner = Equipment.query.filter_by(name='扫描仪-001').first()
    if scanner and zhuxu and not EquipmentScrap.query.filter_by(requester_id=zhuxu.id).first():
        scrap = EquipmentScrap(
            requester_id=zhuxu.id,
            equipment_id=scanner.id,
            reason='设备老化严重,无法正常使用',
            scrap_reason='设备已使用超过10年,维修成本过高',
            status='submitted'
        )
        db.session.add(scrap)
        db.session.commit()
        print(f"   - 工单ID: {scrap.id}")
    else:
        existing = EquipmentScrap.query.filter_by(requester_id=zhuxu.id).first()
        print(f"   - 已存在工单 #{existing.id if existing else 'N/A'}")
    
    print("\n" + "="*80)
    print("测试数据创建完成!")
    print("="*80)
    print("\n提示: 现在可以登录系统测试各个审批流程:")
    print("  1. 配件申请审批流程")
    print("  2. 设备申请审批流程")
    print("  3. 设备借用审批流程")
    print("  4. 设备调拨审批流程")
    print("  5. 设备报废审批流程")
