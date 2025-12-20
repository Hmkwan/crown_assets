from app import create_app
from app.models import Announcement

def main():
    app = create_app()

    with app.app_context():
        # 检查公告
        announcements = Announcement.get_active_announcements(limit=3)
        print(f"\n找到 {len(announcements)} 条活跃公告:")
        for ann in announcements:
            print(f"- ID: {ann.id}, 标题: {ann.title}, 发布: {ann.is_published}, 置顶: {ann.is_pinned}")
        
        # 测试首页路由
        with app.test_request_context('/'):
            from flask_login import login_user
            from app.models import User
            
            # 使用admin用户登录
            admin = User.query.filter_by(role='admin').first()
            if admin:
                print(f"\n使用用户: {admin.username}")
                
                # 模拟登录并访问首页
                from app.main.routes import index
                from flask import g
                
                # 手动设置current_user
                import flask_login
                flask_login.utils._request_ctx_stack.top.user = admin
                
                print("\n测试首页函数...")
                try:
                    result = index()
                    if 'announcements' in str(result):
                        print("✓ 首页包含公告数据")
                    else:
                        print("✗ 首页不包含公告数据")
                except Exception as e:
                    print(f"错误: {e}")


if __name__ == '__main__':
    main()
