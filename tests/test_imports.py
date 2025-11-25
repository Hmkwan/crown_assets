import io
import pytest
from config import Config
from app import create_app, db
from app.models import User, SparePart, Equipment


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


def login_client(client, username, password):
    return client.post('/auth/login', data={'username': username, 'password': password}, follow_redirects=True)


def test_import_spare_parts_csv():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('secret')
        db.session.add(admin)
        db.session.commit()

        client = app.test_client()
        # login
        login_client(client, 'admin', 'secret')

        csv_data = (
            '配件名称,配件编号,价格,库存数量,入库日期,所属部门,位置\n'
            'TestPart,TP001,9.99,5,2020-01-01,IT,仓库A\n'
        )

        data = {
            'file': (io.BytesIO(csv_data.encode('utf-8')), 'spares.csv')
        }
        resp = client.post('/spare_parts/import', data=data, content_type='multipart/form-data')
        assert resp.status_code == 200
        j = resp.get_json()
        assert j and j.get('success') is True

        part = SparePart.query.filter_by(part_number='TP001').first()
        assert part is not None
        assert part.name == 'TestPart'


def test_import_equipment_csv():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        admin = User(username='admin', email='admin2@example.com', role='admin')
        admin.set_password('secret')
        db.session.add(admin)
        db.session.commit()

        client = app.test_client()
        login_client(client, 'admin', 'secret')

        csv_data = (
            '名称,类型,品牌,型号,序列号,所属部门,购买日期\n'
            'EQTest,Server,BrandX,ModelY,SN123,IT,2021-01-01\n'
        )

        data = {
            'file': (io.BytesIO(csv_data.encode('utf-8')), 'equip.csv')
        }
        resp = client.post('/equipment/import', data=data, content_type='multipart/form-data')
        assert resp.status_code == 200
        j = resp.get_json()
        assert j and j.get('success') is True

        eq = Equipment.query.filter_by(serial_number='SN123').first()
        assert eq is not None
        assert eq.name == 'EQTest'
