# 批量重置所有 scrypt 密码为 pbkdf2:sha256（默认密码：12345678）
# 适用于 PostgreSQL，需在容器内执行



from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def reset_all_scrypt_passwords(new_password='12345678'):
    app = create_app()
    with app.app_context():
        users = User.query.filter(User.password_hash.startswith('scrypt:')).all()
        if not users:
            print('没有检测到 scrypt 加密的用户密码，无需重置。')
            return
        for user in users:
            user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
            print(f"用户 {user.username} 密码已重置为 {new_password}")
        db.session.commit()
        print(f"共重置 {len(users)} 个用户密码。")

if __name__ == '__main__':
    reset_all_scrypt_passwords()
