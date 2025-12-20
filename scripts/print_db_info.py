from app import create_app, db
import os
os.environ['TEST_DATABASE_URI'] = 'postgresql://postgres:difyai123456@localhost:15432/it_asset'
app = create_app()
with app.app_context():
    print('SQLALCHEMY_DATABASE_URI=', app.config['SQLALCHEMY_DATABASE_URI'])
    print('engine dialect=', db.engine.dialect.name)
    try:
        r = db.session.execute('SELECT 1').fetchone()
        print('select 1 ->', r)
    except Exception as e:
        print('connect error', type(e), e)
