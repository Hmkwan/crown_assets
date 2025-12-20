from app import create_app, db
from app.models import Equipment, Department

app = create_app()

with app.app_context():
    eqs = Equipment.query.all()
    
    print('\n所有设备列表:')
    print(f"{'ID':<5} {'设备名称':<30} {'品牌':<15} {'部门':<15} {'状态':<15} {'公开':<10}")
    print('-' * 100)
    
    for eq in eqs:
        dept = Department.query.get(eq.department_id) if eq.department_id else None
        dept_name = dept.name if dept else "无"
        is_public = "是" if eq.is_public_pool else "否"
        print(f"{eq.id:<5} {eq.name[:28]:<30} {eq.brand[:13]:<15} {dept_name[:13]:<15} {eq.status:<15} {is_public:<10}")
