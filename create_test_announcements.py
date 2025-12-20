#!/usr/bin/env python3
"""创建测试公告数据"""
import sys
import os
from datetime import datetime, timedelta

import os
# Avoid long Redis retry loops when running one-off scripts/tests
os.environ.setdefault('REDIS_DISABLED', '1')

# 添加app目录到路径
sys.path.insert(0, '/app')

from app import create_app, db
from app.models import Announcement, User

def create_test_announcements():
    """创建测试公告"""
    app = create_app()
    # 等待数据库准备好（最多重试 5 次），以防容器刚启动
    import time
    from sqlalchemy import inspect
    for i in range(5):
        try:
            with app.app_context():
                inspector = inspect(db.engine)
                if 'announcements' in inspector.get_table_names():
                    break
        except Exception:
            pass
        time.sleep(1)
    
    with app.app_context():
        # 获取管理员用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("❌ 未找到admin用户")
            return
        
        # 删除现有测试公告
        Announcement.query.delete()
        db.session.commit()
        print("✓ 已清理旧公告")
        
        # 测试公告数据
        announcements_data = [
            {
                'title': '🎉 新系统功能上线通知',
                'content': '''
<h3>亲爱的用户:</h3>
<p>我们很高兴地宣布,设备管理系统新增以下功能:</p>
<ul>
    <li><strong>实时聊天系统</strong>: 支持在线用户之间的实时通信</li>
    <li><strong>系统公告</strong>: 管理员可发布重要通知和更新信息</li>
    <li><strong>工作流审批</strong>: 完整的审批流程管理</li>
    <li><strong>设备生命周期</strong>: 全程追踪设备状态变化</li>
</ul>
<p>欢迎大家使用新功能,如有任何问题请联系系统管理员。</p>
<p><em>发布日期: 2025年12月6日</em></p>
                ''',
                'type': 'update',
                'priority': 'high',
                'is_pinned': True,
                'is_published': True,
                'publish_time': datetime.now()
            },
            {
                'title': '🔧 系统维护通知 - 12月10日',
                'content': '''
<h3>系统维护公告</h3>
<p><strong>维护时间:</strong> 2025年12月10日 22:00 - 23:00</p>
<p><strong>影响范围:</strong> 系统将暂时无法访问</p>
<h4>维护内容:</h4>
<ol>
    <li>数据库性能优化</li>
    <li>系统安全补丁更新</li>
    <li>缓存服务器升级</li>
</ol>
<p class="text-warning">⚠️ 请各位用户提前做好准备,维护期间请勿进行重要操作。</p>
<p>维护期间如有紧急情况,请联系值班人员。</p>
                ''',
                'type': 'system',
                'priority': 'urgent',
                'is_pinned': True,
                'is_published': True,
                'publish_time': datetime.now(),
                'expire_time': datetime.now() + timedelta(days=5)
            },
            {
                'title': '📢 设备盘点工作启动通知',
                'content': '''
<h3>关于开展年度设备盘点工作的通知</h3>
<p>各部门:</p>
<p>为全面掌握公司资产状况,现决定开展2025年度设备盘点工作。</p>
<h4>盘点时间:</h4>
<p>2025年12月15日 - 12月25日</p>
<h4>盘点要求:</h4>
<ul>
    <li>核对设备数量、型号、状态</li>
    <li>更新设备位置信息</li>
    <li>标记待报废设备</li>
    <li>及时录入盘点结果</li>
</ul>
<h4>注意事项:</h4>
<ol>
    <li>各部门指定专人负责盘点工作</li>
    <li>发现问题及时上报</li>
    <li>12月26日前提交盘点报告</li>
</ol>
<p>感谢大家的配合!</p>
<p style="text-align: right;"><em>行政部<br>2025年12月6日</em></p>
                ''',
                'type': 'notice',
                'priority': 'normal',
                'is_pinned': False,
                'is_published': True,
                'publish_time': datetime.now()
            },
            {
                'title': '✨ 用户体验优化更新',
                'content': '''
<h3>系统优化更新说明</h3>
<p>本次更新主要优化了用户体验:</p>
<h4>界面优化:</h4>
<ul>
    <li>✅ 优化了移动端显示效果</li>
    <li>✅ 改进了导航菜单布局</li>
    <li>✅ 统一了按钮和表单样式</li>
</ul>
<h4>性能提升:</h4>
<ul>
    <li>⚡ 页面加载速度提升30%</li>
    <li>⚡ 数据查询响应更快</li>
    <li>⚡ 减少了内存占用</li>
</ul>
<h4>功能增强:</h4>
<ul>
    <li>🔍 增强了搜索功能</li>
    <li>📊 新增数据导出功能</li>
    <li>🔔 优化了消息通知</li>
</ul>
<p>感谢大家的反馈和建议!</p>
                ''',
                'type': 'update',
                'priority': 'normal',
                'is_pinned': False,
                'is_published': True,
                'publish_time': datetime.now() - timedelta(days=1)
            },
            {
                'title': '⚠️ 安全提醒:请及时修改初始密码',
                'content': '''
<h3 class="text-danger">重要安全提醒</h3>
<p><strong>尊敬的用户:</strong></p>
<p>为保障账户安全,请务必遵守以下规定:</p>
<div class="alert alert-warning">
    <h4>⚠️ 密码安全要求:</h4>
    <ol>
        <li>首次登录后立即修改初始密码</li>
        <li>密码长度不少于8位</li>
        <li>包含大小写字母、数字和特殊字符</li>
        <li>不使用生日、电话等容易猜测的信息</li>
        <li>定期更换密码(建议每3个月)</li>
    </ol>
</div>
<h4>如何修改密码:</h4>
<ol>
    <li>点击右上角头像</li>
    <li>选择"个人设置"</li>
    <li>进入"安全设置"</li>
    <li>修改登录密码</li>
</ol>
<p class="text-danger"><strong>如发现异常登录,请立即联系管理员!</strong></p>
<p>系统安全电话: 1234567890</p>
                ''',
                'type': 'urgent',
                'priority': 'urgent',
                'is_pinned': False,
                'is_published': True,
                'publish_time': datetime.now() - timedelta(days=2)
            }
        ]
        
        # 创建公告
        for data in announcements_data:
            announcement = Announcement(
                title=data['title'],
                content=data['content'],
                type=data['type'],
                priority=data['priority'],
                is_pinned=data['is_pinned'],
                is_published=data['is_published'],
                publish_time=data['publish_time'],
                expire_time=data.get('expire_time'),
                creator_id=admin.id
            )
            db.session.add(announcement)
        
        db.session.commit()
        print(f"✓ 成功创建 {len(announcements_data)} 条测试公告")
        
        # 显示公告列表
        print("\n📋 公告列表:")
        announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
        for ann in announcements:
            status = "✓ 已发布" if ann.is_published else "✗ 未发布"
            pin = "📌" if ann.is_pinned else "  "
            print(f"{pin} ID:{ann.id:2d} | {status} | {ann.type_display:6s} | {ann.title}")

if __name__ == '__main__':
    create_test_announcements()
