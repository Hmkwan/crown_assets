from app import create_app, db
from config import Config
from app.models import User, Equipment
import io

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

    client = app.test_client()
    # login
    client.post('/auth/login', data={'username': 'admin', 'password': 'secret'}, follow_redirects=True)

    csv_data = (
        '名称,类型,品牌,型号,序列号,所属部门,价格,购买日期\n'
        '宏碁笔记本高配,电脑,宏碁,2044,SN2044,信息部,1221,2025/12/07\n'
    )

    data = {
        'file': (io.BytesIO(csv_data.encode('utf-8')), 'equip.csv')
    }
    resp = client.post('/equipment/import', data=data, content_type='multipart/form-data')
    print('status', resp.status_code)
    print('json', resp.get_json())

    eq = Equipment.query.filter_by(serial_number='SN2044').first()
    if eq:
        print('Found:', eq.name, eq.serial_number, eq.purchase_date, eq.price)
    else:
        print('Not found')
