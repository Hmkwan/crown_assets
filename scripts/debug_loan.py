import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app, db
from config import Config
from app.models import User, Department, Equipment, EquipmentLoan, ApprovalWorkflow

app = create_app(Config)
with app.app_context():
    db.drop_all()
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
    # Now simulate submitting a loan via the test client (to match behavior in unit tests)
    client = app.test_client()
    # login as alice
    client.post('/auth/login', data={'username':'alice','password':'secret'}, follow_redirects=True)
    data = {'equipment_id': str(eq.id), 'start_date':'2025-11-16T09:00', 'end_date':'2025-11-20T18:00', 'notes':'debug'}
    resp = client.post('/create_loan_request', data=data, follow_redirects=True)
    print('POST /create_loan_request status:', resp.status_code)
    loan = EquipmentLoan.query.filter_by(requester_id=user.id).first()
    print('Loan created id:', loan.id, 'status:', loan.status)
    print('Approvals after HTTP create:')
    for a in ApprovalWorkflow.query.filter_by(order_type='equipment_loan', order_id=loan.id).order_by(ApprovalWorkflow.created_date).all():
        print('approval', a.id, 'approver_id', a.approver_id, 'level', a.approval_level, 'status', a.status, 'auto', a.auto_assigned)
    # login as admin and try to post approval
    client.post('/auth/login', data={'username':'admin','password':'secret'}, follow_redirects=True)
    resp2 = client.post(f'/approvals/loan/{loan.id}/approve', data={'comments':'ok'}, follow_redirects=True)
    print('POST approve status:', resp2.status_code)
