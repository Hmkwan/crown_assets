from app import create_app, db
from app.models import User, Equipment, SparePart, Department, UserActivityLog, Notification, PartReplacement
from werkzeug.security import generate_password_hash


def init_db():
    app = create_app()
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建默认部门
        default_departments = [
            {'name': 'IT部', 'code': 'IT', 'cost_center': 'CC001', 'location': 'A座5楼', 'description': '信息技术部门'},
            {'name': '财务部', 'code': 'FIN', 'cost_center': 'CC002', 'location': 'A座3楼', 'description': '财务管理部门'},
            {'name': '人事部', 'code': 'HR', 'cost_center': 'CC003', 'location': 'A座2楼', 'description': '人力资源部门'},
            {'name': '销售部', 'code': 'SALES', 'cost_center': 'CC004', 'location': 'B座1楼', 'description': '销售部门'},
            {'name': '生产部', 'code': 'PROD', 'cost_center': 'CC005', 'location': 'C厂房', 'description': '生产制造部门'}
        ]
        
        for dept_data in default_departments:
            dept = Department.query.filter_by(code=dept_data['code']).first()
            if not dept:
                dept = Department(**dept_data)
                db.session.add(dept)
                
        # 提交部门数据
        db.session.commit()
                
        # 创建默认管理员用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # 获取IT部门
            it_dept = Department.query.filter_by(code='IT').first()
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin',
                department='IT部'
            )
            if it_dept:
                admin.department_id = it_dept.id
            admin.set_password('admin123')
            db.session.add(admin)
            
        # 创建示例设备
        equipments = [
            {
                'name': '办公电脑001',
                'type': '电脑',
                'brand': '联想',
                'model': 'ThinkCentre M720',
                'serial_number': 'PC2023001',
                'department': '财务部'
            },
            {
                'name': '激光打印机001',
                'type': '打印机',
                'brand': '惠普',
                'model': 'LaserJet Pro MFP M428fdw',
                'serial_number': 'PR2023001',
                'department': '人事部'
            },
            {
                'name': '办公电脑002',
                'type': '电脑',
                'brand': '戴尔',
                'model': 'OptiPlex 3080',
                'serial_number': 'PC2023002',
                'department': '销售部'
            }
        ]
        
        for equip_data in equipments:
            equip = Equipment.query.filter_by(serial_number=equip_data['serial_number']).first()
            if not equip:
                equip = Equipment(**equip_data)
                # 关联部门
                dept = Department.query.filter_by(name=equip_data['department']).first()
                if dept:
                    equip.department_id = dept.id
                db.session.add(equip)
                
        # 创建示例配件
        parts = [
            {'name': '内存条 8GB DDR4', 'part_number': 'MEM001', 'price': 280.0, 'stock_quantity': 10},
            {'name': '固态硬盘 256GB SATA', 'part_number': 'SSD001', 'price': 180.0, 'stock_quantity': 5},
            {'name': '电源适配器 65W', 'part_number': 'PWR001', 'price': 95.0, 'stock_quantity': 8}
        ]
        
        for part_data in parts:
            part = SparePart.query.filter_by(part_number=part_data['part_number']).first()
            if not part:
                part = SparePart(**part_data)
                db.session.add(part)
                
        db.session.commit()
        print('数据库初始化完成')
        print('默认管理员账号: admin / admin123')


if __name__ == '__main__':
    init_db()