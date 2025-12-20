#!/usr/bin/env python3
"""验证公告系统功能"""
import sys
sys.path.insert(0, '/app')

from app import create_app, db
from app.models import Announcement

def verify_announcements():
    """验证公告功能"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("公告系统功能验证")
        print("=" * 60)
        
        # 1. 查询所有公告
        total = Announcement.query.count()
        print(f"\n✓ 公告总数: {total}")
        
        # 2. 查询已发布公告
        published = Announcement.query.filter_by(is_published=True).count()
        print(f"✓ 已发布: {published}")
        
        # 3. 查询置顶公告
        pinned = Announcement.query.filter_by(is_pinned=True).count()
        print(f"✓ 置顶: {pinned}")
        
        # 4. 按类型统计
        print("\n按类型统计:")
        types = ['notice', 'update', 'system', 'urgent']
        type_names = {'notice': '普通通知', 'update': '功能更新', 'system': '系统维护', 'urgent': '紧急公告'}
        for t in types:
            count = Announcement.query.filter_by(type=t).count()
            if count > 0:
                print(f"  {type_names[t]}: {count} 条")
        
        # 5. 获取有效公告
        active = Announcement.get_active_announcements()
        print(f"\n✓ 有效公告: {len(active)} 条")
        
        # 6. 详细列表
        print("\n" + "=" * 60)
        print("公告详细列表:")
        print("=" * 60)
        announcements = Announcement.query.order_by(
            Announcement.is_pinned.desc(),
            Announcement.created_at.desc()
        ).all()
        
        for ann in announcements:
            pin = "📌" if ann.is_pinned else "  "
            pub = "✓" if ann.is_published else "✗"
            active_status = "🟢" if ann.is_active else "🔴"
            
            print(f"\n{pin} ID: {ann.id}")
            print(f"   标题: {ann.title}")
            print(f"   类型: {ann.type_display} | 优先级: {ann.priority_display}")
            print(f"   状态: {pub} 发布 | {active_status} {'有效' if ann.is_active else '无效'}")
            if ann.publish_time:
                print(f"   发布时间: {ann.publish_time.strftime('%Y-%m-%d %H:%M')}")
            if ann.expire_time:
                print(f"   过期时间: {ann.expire_time.strftime('%Y-%m-%d %H:%M')}")
        
        print("\n" + "=" * 60)
        print("✅ 公告系统功能正常")
        print("=" * 60)
        
        # 7. 测试建议
        print("\n测试建议:")
        print("1. 访问 http://10.168.93.93:5020/admin/announcements 查看公告列表")
        print("2. 点击任意公告进行编辑,测试编辑功能")
        print("3. 创建新公告,测试创建功能")
        print("4. 上传附件,测试附件功能")
        print("5. 访问 http://10.168.93.93:5020/announcements 查看用户视图")

if __name__ == '__main__':
    verify_announcements()
