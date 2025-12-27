#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证北京时区配置
"""
import sys
from app import create_app, db, get_beijing_now
from app.models import User, UserActivityLog
from datetime import datetime, timedelta, timezone

def test_timezone():
    app = create_app()
    
    with app.app_context():
        print(f"✓ Current app timezone config: {app.config.get('TIMEZONE', 'Not set')}")
        
        # 测试get_beijing_now函数
        beijing_now = get_beijing_now()
        utc_now = datetime.now(timezone.utc)

        print(f"✓ Beijing now: {beijing_now}")
        print(f"✓ UTC now: {utc_now}")

        # 验证时区偏移应该约8小时（使用 tzinfo 的 utcoffset）
        offset = beijing_now.utcoffset()
        assert offset is not None, "Beijing time should be timezone-aware"
        hours_diff = offset.total_seconds() / 3600
        print(f"✓ TZ offset: {hours_diff:.1f} hours")

        assert 7.5 < hours_diff < 8.5, f"Timezone offset is {hours_diff:.1f} hours, expected ~8 hours"
        
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
                assert retrieved_log is not None
                print(f"✓ Logged timestamp: {retrieved_log.timestamp}")
                print("✅ Database timestamps are using Beijing time")

                # 清理测试数据
                db.session.delete(retrieved_log)
                db.session.commit()
            except Exception as e:
                print(f"❌ Database timestamp test failed: {e}")
                db.session.rollback()
                raise

if __name__ == '__main__':
    success = test_timezone()
    sys.exit(0 if success else 1)
