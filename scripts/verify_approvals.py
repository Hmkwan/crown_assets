import importlib.util
import sys
import os
from config import Config

# 明确地从包目录加载 app 包，避免与顶层 app.py 冲突
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec_path = os.path.join(root, 'app', '__init__.py')
spec = importlib.util.spec_from_file_location('app', spec_path)
app_pkg = importlib.util.module_from_spec(spec)
sys.modules['app'] = app_pkg
spec.loader.exec_module(app_pkg)

from app import create_app, db
from app.models import User, Department, Equipment, EquipmentTransfer, ApprovalWorkflow


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


app = create_app(TestConfig)
with app.app_context():
    db.create_all()

    admin = User(username='admin', email='admin@example.com', role='admin')
    admin.set_password('secret')
    db.session.add(admin)
    db.session.commit()

    dept = Department(name='IT', code='IT01')
    db.session.add(dept)
    db.session.commit()

    equipment = Equipment(name='EQ1', serial_number='S1', department=dept.name, department_id=dept.id)
    db.session.add(equipment)
    db.session.commit()

    transfer = EquipmentTransfer(
        equipment_id=equipment.id,
        from_department=equipment.department,
        to_department='HR',
        requester_id=admin.id,
        description='测试调拨'
    )
    db.session.add(transfer)
    db.session.commit()

    from app.main.routes import _create_sequenced_approvals

    steps = [
        ('department_head', equipment.department),
        ('admin', None)
    ]
    _create_sequenced_approvals('equipment_transfer', transfer.id, steps)
    db.session.commit()

    approvals = ApprovalWorkflow.query.filter_by(order_type='equipment_transfer', order_id=transfer.id).order_by(ApprovalWorkflow.created_date).all()
    print('approvals count:', len(approvals))
    for a in approvals:
        print('approval:', a.id, a.approval_level, a.approver_id, a.status)
