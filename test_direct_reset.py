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
            import pytest
            pytest.skip("testuser not found")
        
        print(f"✓ Found user: {user.username}")
        
        # 直接更新密码
        try:
            from werkzeug.security import generate_password_hash
            original_hash = user.password_hash
            
            test_password = 'TestPass123'
            user.password_hash = generate_password_hash(test_password)
            db.session.commit()
            
            # 验证
            assert check_password_hash(user.password_hash, test_password), "New password verification failed"
            # 验证旧密码不再有效
            assert not check_password_hash(user.password_hash, 'oldpass'), "Old password still works"
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            import pytest
            pytest.fail(f"Error: {e}")

if __name__ == '__main__':
    success = test_direct()
    sys.exit(0 if success else 1)
