from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    user = User.query.filter_by(username='test_admin').first()
    if not user:
        user = User(username='test_admin', email='test_admin@test.com', role='admin')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    with app.test_client() as client:
        client.post('/auth/login', data={'username':'test_admin','password':'password123'}, follow_redirects=True)
        r = client.get('/admin', follow_redirects=True)
        html = r.get_data(as_text=True)
        print(html)
