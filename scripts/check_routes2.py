import sys
sys.path.append('.')
from app import create_app
app=create_app()
with app.app_context():
    routes = [str(r) for r in app.url_map.iter_rules() if '__dev_login_admin' in str(r) or '/__dev_login_admin' in str(r)]
    print('matches', routes)
    print('/chat in routes', any('/chat' in str(r) for r in app.url_map.iter_rules()))
