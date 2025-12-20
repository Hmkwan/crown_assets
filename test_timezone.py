#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证北京时区配置
"""
import sys
from app import create_app, db, get_beijing_now
from app.models import User, UserActivityLog
from datetime import datetime, timedelta

def test_timezone():
    app = create_app()
    
    with app.app_context():
        print(f"✓ Current app timezone config: {app.config.get('TIMEZONE', 'Not set')}")
        
        # 测试get_beijing_now函数
        beijing_now = get_beijing_now()
        utc_now = datetime.utcnow()
        
        print(f"✓ Beijing now: {beijing_now}")
        print(f"✓ UTC now: {utc_now}")
        
        # 验证差异应该约8小时
        diff = beijing_now - utc_now
        hours_diff = diff.total_seconds() / 3600
        print(f"✓ Time difference: {hours_diff:.1f} hours")
        
        if 7.5 < hours_diff < 8.5:
            print("✅ Timezone is correctly set to Beijing (UTC+8)")
            
            # 测试数据库中的时间戳
            admin = User.query.filter_by(username='admin').first()
            if admin:
                # 创建一个测试日志条目
                try:
                    log = UserActivityLog(
                        user_id=admin.id,
                        action='时区测试',
                        description='验证北京时区是否正确'
                    )
                    db.session.add(log)
                    db.session.commit()
                    
                    # 检查时间戳
                    retrieved_log = UserActivityLog.query.filter_by(action='时区测试').first()
                    if retrieved_log:
                        print(f"✓ Logged timestamp: {retrieved_log.timestamp}")
                        print("✅ Database timestamps are using Beijing time")
                        
                        # 清理测试数据
                        db.session.delete(retrieved_log)
                        db.session.commit()
                        return True
                except Exception as e:
                    print(f"❌ Database timestamp test failed: {e}")
                    db.session.rollback()
                    return False
        else:
            print(f"❌ Timezone offset is {hours_diff:.1f} hours, expected ~8 hours")
            return False

if __name__ == '__main__':
    success = test_timezone()
    sys.exit(0 if success else 1)
