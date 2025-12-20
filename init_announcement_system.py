#!/usr/bin/env python3
"""初始化公告系统和企业微信配置

此脚本用于:
1. 创建 announcements 表
2. 添加示例公告数据
3. 显示企业微信配置说明
"""

from app import create_app, db, get_beijing_now
from app.models import Announcement, User
from datetime import datetime, timedelta
import sys

def init_announcement_system():
    """初始化公告系统"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("系统公告模块初始化")
        print("=" * 60)
        
        # 检查表是否存在
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        if 'announcements' not in inspector.get_table_names():
            print("\n✓ 创建 announcements 表...")
            try:
                # 创建表
                db.create_all()
                print("  表创建成功!")
            except Exception as e:
                print(f"  ✗ 表创建失败: {e}")
                return False
        else:
            print("\n✓ announcements 表已存在")
        
        # 检查是否有管理员用户
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("\n✗ 未找到管理员用户,无法创建示例公告")
            print("  请先创建管理员账户")
            return False
        
        # 检查是否已有公告
        existing_count = Announcement.query.count()
        if existing_count > 0:
            print(f"\n✓ 数据库中已有 {existing_count} 条公告,跳过示例数据创建")
        else:
            # 创建示例公告
            print("\n✓ 创建示例公告...")
            
            announcements = [
                {
                    'title': '欢迎使用IT资产管理系统!',
                    'content': '''
                    <h4>系统已正式上线</h4>
                    <p>欢迎使用皇冠新材IT资产管理系统。本系统提供以下功能:</p>
                    <ul>
                        <li>设备和配件管理</li>
                        <li>维修工单管理</li>
                        <li>设备借用和调拨</li>
                        <li>审批流程管理</li>
                        <li>报表统计分析</li>
                    </ul>
                    <p>如有任何问题,请联系系统管理员。</p>
                    ''',
                    'type': 'notice',
                    'priority': 'normal',
                    'is_pinned': True,
                    'is_published': True,
                    'publish_time': get_beijing_now(),
                    'expire_time': None,
                    'creator_id': admin.id
                },
                {
                    'title': '系统新功能上线 - 公告模块',
                    'content': '''
                    <h4>新功能介绍</h4>
                    <p>系统新增公告模块,管理员可以通过以下路径管理公告:</p>
                    <ul>
                        <li>访问 <strong>首页 → 系统公告 → 公告管理</strong></li>
                        <li>或直接访问 <code>/admin/announcements</code></li>
                    </ul>
                    <h5>功能特点:</h5>
                    <ul>
                        <li>支持多种公告类型(系统维护、功能更新、普通通知、紧急公告)</li>
                        <li>可设置发布时间和过期时间</li>
                        <li>支持置顶显示</li>
                        <li>富文本编辑器,支持图文混排</li>
                    </ul>
                    ''',
                    'type': 'update',
                    'priority': 'high',
                    'is_pinned': False,
                    'is_published': True,
                    'publish_time': get_beijing_now(),
                    'expire_time': None,
                    'creator_id': admin.id
                },
                {
                    'title': '系统维护通知 - 本周六凌晨',
                    'content': '''
                    <div class="alert alert-warning">
                        <h4>⚠️ 维护通知</h4>
                        <p><strong>维护时间:</strong> 2025年12月7日(本周六) 凌晨 02:00 - 04:00</p>
                        <p><strong>影响范围:</strong> 系统将暂时无法访问</p>
                        <p><strong>维护内容:</strong></p>
                        <ul>
                            <li>数据库性能优化</li>
                            <li>系统安全更新</li>
                            <li>备份系统升级</li>
                        </ul>
                        <p>请各位用户提前安排好工作,维护期间造成的不便敬请谅解。</p>
                    </div>
                    ''',
                    'type': 'system',
                    'priority': 'high',
                    'is_pinned': True,
                    'is_published': True,
                    'publish_time': datetime.utcnow(),
                    'expire_time': datetime.utcnow() + timedelta(days=7),
                    'creator_id': admin.id
                }
            ]
            
            try:
                for ann_data in announcements:
                    announcement = Announcement(**ann_data)
                    db.session.add(announcement)
                
                db.session.commit()
                print(f"  ✓ 成功创建 {len(announcements)} 条示例公告")
            except Exception as e:
                db.session.rollback()
                print(f"  ✗ 创建示例公告失败: {e}")
                return False
        
        print("\n" + "=" * 60)
        print("✓ 公告系统初始化完成!")
        print("=" * 60)
        
        print("\n访问路径:")
        print("  - 查看公告: /announcements")
        print("  - 管理公告(管理员): /admin/announcements")
        print("  - API接口: /api/announcements/active")
        
        return True


def show_wework_config():
    """显示企业微信配置说明"""
    print("\n" + "=" * 60)
    print("企业微信集成配置说明")
    print("=" * 60)
    
    print("""
企业微信集成接口已预留,使用前需要配置以下环境变量:

1. WEWORK_CORP_ID      - 企业ID (必需)
2. WEWORK_AGENT_ID     - 应用AgentId (必需)
3. WEWORK_SECRET       - 应用Secret (必需)
4. WEWORK_ENABLED      - 是否启用 (true/false)

配置方法:

方法1: 在 .env 文件中添加
----------------------------
WEWORK_CORP_ID=your_corp_id
WEWORK_AGENT_ID=your_agent_id
WEWORK_SECRET=your_secret
WEWORK_ENABLED=true

方法2: 在 Docker Compose 中配置
-------------------------------
在 docker-compose.yml 的 environment 中添加:
  - WEWORK_CORP_ID=your_corp_id
  - WEWORK_AGENT_ID=your_agent_id
  - WEWORK_SECRET=your_secret
  - WEWORK_ENABLED=true

获取企业微信凭证:
----------------
1. 登录企业微信管理后台
2. 进入"应用管理" → "应用" → "自建应用"
3. 创建应用并获取 AgentId 和 Secret
4. 在"我的企业"中获取企业ID

预留接口说明:
------------
文件位置: app/integrations/wework.py

主要接口:
- get_access_token()          # 获取访问令牌
- get_user_info(code)          # 获取用户信息
- get_user_detail(userid)      # 获取用户详细信息
- get_department_list()        # 获取部门列表
- get_department_users()       # 获取部门成员
- sync_departments_to_local()  # 同步组织架构
- generate_wework_login_url()  # 生成登录URL

使用示例:
--------
from app.integrations import get_wework_client

# 获取客户端
client = get_wework_client()

# 获取部门列表
departments = client.get_department_list()

# 同步组织架构
result = client.sync_departments_to_local()

注意事项:
--------
- 当前所有接口返回示例数据
- 实际使用前需要取消注释 TODO 部分的代码
- 建议先在测试环境验证配置正确性
""")
    
    print("=" * 60)


if __name__ == '__main__':
    # 初始化公告系统
    success = init_announcement_system()
    
    # 显示企业微信配置说明
    show_wework_config()
    
    sys.exit(0 if success else 1)
