import pytest
from config import Config
from app import create_app, db
from app.models import User, Department, Equipment, EquipmentTransfer, ApprovalWorkflow


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def test_create_sequenced_approvals_auto_assign():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        # 创建一个管理员用户（如果已存在则复用）
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('secret')
            db.session.add(admin)
            db.session.commit()

        # 创建部门和设备（若存在则复用，避免冲突）
        dept = Department.query.filter_by(code='IT01').first()
        if not dept:
            dept = Department(name='IT', code='IT01')
            db.session.add(dept)
            db.session.commit()

        equipment = Equipment(name='EQ1', serial_number='S1', department=dept.name, department_id=dept.id)
        db.session.add(equipment)
        db.session.commit()

        # 创建一个调拨申请
        transfer = EquipmentTransfer(
            equipment_id=equipment.id,
            from_department=equipment.department,
            to_department='HR',
            requester_id=admin.id,
            description='测试调拨'
        )
        db.session.add(transfer)
        db.session.commit()

        # 调用内部 helper 创建审批——第一个节点是 department_head（但我们未创建该角色），应自动回退给 admin
        from app.main.routes import _create_sequenced_approvals

        steps = [
            ('department_head', equipment.department),
            ('admin', None)
        ]
        _create_sequenced_approvals('equipment_transfer', transfer.id, steps)
        db.session.commit()

        approvals = ApprovalWorkflow.query.filter_by(order_type='equipment_transfer', order_id=transfer.id).order_by(ApprovalWorkflow.created_date).all()
        assert len(approvals) == 2
        # 第一个审批原本应由 department_head 执行，但应被自动分配给 admin
        assert approvals[0].approver_id == admin.id
        # 第二个审批本来就是 admin
        assert approvals[1].approver_id == admin.id
