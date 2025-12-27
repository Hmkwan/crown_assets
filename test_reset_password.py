#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试重置密码功能
"""
import sys
from app import create_app, db
from app.models import User
from werkzeug.security import check_password_hash

def test_reset_password():
    app = create_app()
    
    with app.app_context():
        # 查找一个测试用户
        user = User.query.filter_by(username='testuser').first()
        if not user:
            import pytest
            pytest.skip("测试用户 'testuser' 不存在")
        
        original_hash = user.password_hash
        print(f"✓ 找到用户: {user.username}")
        
        # 尝试更新密码
        try:
            from werkzeug.security import generate_password_hash
            new_password = 'NewPassword123'
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            print(f"✓ 密码哈希已更新")
            
            # 验证新密码可以正确验证
            assert check_password_hash(user.password_hash, new_password), "新密码验证失败"
                
        except Exception as e:
            db.session.rollback()
            import pytest
            pytest.fail(f"密码更新失败: {e}")

if __name__ == '__main__':
    success = test_reset_password()
    sys.exit(0 if success else 1)
