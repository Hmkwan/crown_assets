import sys
import os
import io
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import Config
from app import create_app, db
from app.models import User


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
        db.session.commit()

        client = app.test_client()
        client.post('/auth/login', data={'username': 'admin', 'password': 'secret'}, follow_redirects=True)

        csv_dept = '部门名称,部门代码,成本中心,位置,描述\n技术部,TECH,CC,上海,说明'
        r1 = client.post('/admin/departments/import', data={'file': (io.BytesIO(csv_dept.encode('gbk')), 'depts.csv')}, content_type='multipart/form-data')
        print('departments import:', r1.status_code, r1.get_json())

        csv_users = '用户名,邮箱,角色,所属部门\n张三,zhang@example.com,user,销售部'
        r2 = client.post('/admin/users/import', data={'file': (io.BytesIO(csv_users.encode('utf-8-sig')), 'users.csv')}, content_type='multipart/form-data')
        print('users import:', r2.status_code, r2.get_json())

        csv_sp = '名称,编号,价格,库存,日期,部门,位置\n内存条,PN001,199,10,2025-01-01,技术部,仓库'
        r3 = client.post('/spare_parts/import', data={'file': (io.BytesIO(csv_sp.encode('utf-8')), 'sp.csv')}, content_type='multipart/form-data')
        print('sp import:', r3.status_code, r3.get_json())

        csv_eq = 'name,type,brand,model,serial_number,department,purchase_date\n笔记本,电脑,联想,T490,SN999,技术部,2025-01-02'
        r4 = client.post('/equipment/import', data={'file': (io.BytesIO(csv_eq.encode('utf-8')), 'eq.csv')}, content_type='multipart/form-data')
        print('eq import:', r4.status_code, r4.get_json())


if __name__ == '__main__':
    main()