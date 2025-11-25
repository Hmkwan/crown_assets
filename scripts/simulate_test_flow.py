import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import Config
from app import create_app, db
from app.models import User, Department, Equipment, EquipmentLoan, ApprovalWorkflow

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

app = create_app(TestConfig)
with app.app_context():
    db.create_all()
    admin = User(username='admin', email='admin@example.com', role='admin')
    admin.set_password('secret')
    user = User(username='alice', email='alice@example.com', role='user', department='IT')
    user.set_password('secret')
    db.session.add_all([admin, user])
    db.session.commit()
    dept = Department(name='IT', code='IT01')
    db.session.add(dept)
    db.session.commit()
    eq = Equipment(name='EQLoan', serial_number='LSN001', department=dept.name, department_id=dept.id)
    db.session.add(eq)
    db.session.commit()

    client = app.test_client()
    def login(u, p):
        return client.post('/auth/login', data={'username':u, 'password':p}, follow_redirects=True)

    login('alice','secret')
    data = {'equipment_id': str(eq.id), 'start_date':'2025-11-16T09:00', 'end_date':'2025-11-20T18:00', 'notes':'测试借用'}
    r = client.post('/create_loan_request', data=data, follow_redirects=True)
    print('create loan status', r.status_code)
    loan = EquipmentLoan.query.filter_by(requester_id=user.id).first()
    print('loan after create: id', loan.id, 'status', loan.status)
    print('approvals:')
    for a in ApprovalWorkflow.query.filter_by(order_type='equipment_loan', order_id=loan.id).order_by(ApprovalWorkflow.created_date).all():
        print(a.id, a.approver_id, a.approval_level, a.status, a.auto_assigned)

    login('admin','secret')
    r2 = client.post(f'/approvals/loan/{loan.id}/approve', data={'comments':'ok'}, follow_redirects=True)
    print('approve status', r2.status_code)
    loan = EquipmentLoan.query.get(loan.id)
    print('loan after approve: status', loan.status)

    r3 = client.post(f'/loans/{loan.id}/mark_borrowed', follow_redirects=True)
    print('mark_borrowed status', r3.status_code)
    print('mark_borrowed response len', len(r3.data or b''))
    try:
        print('mark_borrowed response snippet:', r3.data.decode('utf-8')[:200])
    except Exception:
        pass
    loan = EquipmentLoan.query.get(loan.id)
    print('loan after mark_borrowed:', loan.status, loan.borrowed_date)

    r4 = client.post(f'/loans/{loan.id}/mark_returned', follow_redirects=True)
    print('mark_returned status', r4.status_code)
    print('mark_returned response len', len(r4.data or b''))
    try:
        print('mark_returned response snippet:', r4.data.decode('utf-8')[:200])
    except Exception:
        pass
    loan = EquipmentLoan.query.get(loan.id)
    print('loan after mark_returned:', loan.status, loan.returned_date)
