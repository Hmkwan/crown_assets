from app import create_app, db
from app.models import Equipment

app = create_app()

with app.app_context():
    eqs = Equipment.query.all()
    public_eqs = [eq for eq in eqs if eq.is_public_pool]
    
    print(f'\n总计: {len(eqs)} 台设备')
    print(f'公开设备: {len(public_eqs)} 台')
    print(f'私有设备: {len(eqs) - len(public_eqs)} 台')
    
    print('\n公开设备列表:')
    for eq in public_eqs:
        from app.models import Department
        dept = Department.query.get(eq.department_id) if eq.department_id else None
        dept_name = dept.name if dept else "无"
        print(f'  - ID:{eq.id} {eq.name} (部门:{dept_name}, 状态:{eq.status})')
