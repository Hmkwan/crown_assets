import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import Config
from app import create_app, db
from app.models import User, Department, EquipmentType, Equipment, SparePart, WorkflowNode


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def post_json(client, url, data):
    r = client.post(url, data=data)
    try:
        return r.status_code, r.get_json()
    except Exception:
        return r.status_code, {'raw': r.get_data(as_text=True)}


def main():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('secret')
        db.session.add(admin)
        db.session.commit()

        client = app.test_client()
        client.post('/auth/login', data={'username': 'admin', 'password': 'secret'}, follow_redirects=True)

        # Departments CRUD
        s, j = post_json(client, '/admin/departments/add', {'name': '销售部', 'code': 'SALE', 'cost_center': 'CC01', 'location': '上海', 'description': '销售'})
        print('dept add:', s, j)
        dep = Department.query.filter_by(name='销售部').first()
        s, j = post_json(client, '/admin/departments/update', {'department_id': str(dep.id), 'name': '销售部', 'code': 'SALE', 'cost_center': 'CC02', 'location': '上海', 'description': '销售更新'})
        print('dept update:', s, j)
        s, j = post_json(client, f'/admin/departments/delete/{dep.id}', {})
        print('dept delete:', s, j)

        # Users CRUD
        dep_user = Department(name='人事部', code='HR')
        db.session.add(dep_user)
        db.session.commit()
        s, j = post_json(client, '/admin/users/add', {'username': 'u1', 'email': 'u1@example.com', 'password': 'x', 'role': 'user', 'department_id': str(dep_user.id)})
        print('user add:', s, j)
        u = User.query.filter_by(username='u1').first()
        s, j = post_json(client, f'/admin/users/edit/{u.id}', {'username': 'u1', 'email': 'u1@example.com', 'role': 'user', 'department_id': '1'})
        print('user edit:', s, j)
        s, j = post_json(client, f'/admin/users/delete/{u.id}', {})
        print('user delete:', s, j)

        # EquipmentType add (used by equipment)
        s, j = post_json(client, '/equipment/types/add', {'name': '笔记本', 'description': '描述'})
        print('type add:', s, j)
        et = EquipmentType.query.filter_by(name='笔记本').first()

        # Equipment CRUD
        # need a department
        d = Department(name='技术部', code='TECH')
        db.session.add(d)
        db.session.commit()
        s = client.post('/equipment/add', data={'name':'设备A','type_id':str(et.id),'brand':'联想','model':'T490','serial_number':'SNX','purchase_date':'2025-01-02','department_id':str(d.id)}, follow_redirects=True).status_code
        print('equipment add:', s)
        eq = Equipment.query.filter_by(serial_number='SNX').first()
        s = client.post(f'/equipment/edit/{eq.id}', data={'name':'设备A','type_id':'','brand':'联想','model':'T490','serial_number':'SNX','purchase_date':'2025-01-02','department_id':str(d.id), 'status':'active'}, follow_redirects=True).status_code
        print('equipment edit:', s)
        s, j = post_json(client, f'/equipment/delete/{eq.id}', {})
        print('equipment delete:', s, j)

        # SparePart CRUD
        s = client.post('/spare_parts/add', data={'name':'内存条','part_number':'PNX','price':'199','stock_quantity':'10','purchase_date':'2025-01-01','department':'技术部','location':'库位A'}, follow_redirects=True).status_code
        print('sp add:', s)
        sp = SparePart.query.filter_by(part_number='PNX').first()
        s = client.post(f'/spare_parts/edit/{sp.id}', data={'name':'内存条','part_number':'PNX','price':'200','stock_quantity':'8','purchase_date':'2025-01-03','department':'技术部','location':'库位A'}, follow_redirects=True).status_code
        print('sp edit:', s)
        s, j = post_json(client, f'/spare_parts/delete/{sp.id}', {})
        print('sp delete:', s, j)

        # WorkflowNodes CRUD
        s, j = post_json(client, '/admin/workflow_nodes/add', {'name':'管理员审批','order_type':'repair_order','role_required':'admin','sequence':'1'})
        print('node add:', s, j)
        wn = WorkflowNode.query.filter_by(name='管理员审批').first()
        s, j = post_json(client, f'/admin/workflow_nodes/edit/{wn.id}', {'name':'管理员审批','order_type':'repair_order','role_required':'admin','sequence':'2'})
        print('node edit:', s, j)
        s, j = post_json(client, f'/admin/workflow_nodes/delete/{wn.id}', {})
        print('node delete:', s, j)

        s, j = post_json(client, f'/equipment/types/delete/{et.id}', {})
        print('type delete:', s, j)


if __name__ == '__main__':
    main()