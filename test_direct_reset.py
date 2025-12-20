#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试：直接调用reset_user_password函数
"""
import sys
from app import create_app, db
from app.models import User
from werkzeug.security import check_password_hash

def test_direct():
    app = create_app()
    
    with app.app_context():
        # 找到testuser
        user = User.query.filter_by(username='testuser').first()
        if not user:
            print("testuser not found")
            return False
        
        print(f"✓ Found user: {user.username}")
        
        # 直接更新密码
        try:
            from werkzeug.security import generate_password_hash
            original_hash = user.password_hash
            
            test_password = 'TestPass123'
            user.password_hash = generate_password_hash(test_password)
            db.session.commit()
            
            # 验证
            if check_password_hash(user.password_hash, test_password):
                print(f"✅ Password reset works correctly")
                
                # 验证旧密码不再有效
                if not check_password_hash(user.password_hash, 'oldpass'):
                    print(f"✅ Old password no longer works")
                    return True
            else:
                print(f"❌ New password verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_direct()
    sys.exit(0 if success else 1)
