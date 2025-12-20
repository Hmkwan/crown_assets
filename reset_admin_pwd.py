from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # 重置admin密码为 Admin@123
    admin = User.query.filter_by(username='admin').first()
    admin.password_hash = generate_password_hash('Admin@123')
    db.session.commit()
    
    print("Admin账号密码已重置为: Admin@123")
    print(f"用户名: {admin.username}")
    print(f"角色: {admin.role}")
