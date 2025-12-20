import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import Config
from app import create_app, db
from app.models import User, Equipment, EquipmentType
from app.approval_models import WorkflowNode


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def main():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('secret')
        db.session.add(admin)
        et = EquipmentType(name='笔记本')
        db.session.add(et)
        eq = Equipment(name='设备X', serial_number='DEL123', type_id=None, department='信息部')
        db.session.add(eq)
        node = WorkflowNode(name='管理员审批', order_type='repair_order', role_required='admin', sequence=1)
        db.session.add(node)
        db.session.commit()

        c = app.test_client()
        c.post('/auth/login', data={'username': 'admin', 'password': 'secret'}, follow_redirects=True)

        r1 = c.post(f'/equipment/delete/{eq.id}')
        print('delete equipment:', r1.status_code, r1.get_json())

        r2 = c.post(f'/admin/workflow_nodes/delete/{node.id}')
        print('delete workflow node:', r2.status_code, r2.get_json())


if __name__ == '__main__':
    main()