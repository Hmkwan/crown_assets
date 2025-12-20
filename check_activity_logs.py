"""测试操作日志记录功能

验证新功能模块的操作日志是否正常记录
"""

from app import create_app, db
from app.models import UserActivityLog, User
from datetime import datetime, timedelta

app = create_app()

def check_recent_logs(hours=24):
    """检查最近的操作日志"""
    with app.app_context():
        # 获取最近N小时的日志
        since = datetime.utcnow() - timedelta(hours=hours)
        recent_logs = UserActivityLog.query.filter(
            UserActivityLog.timestamp >= since
        ).order_by(UserActivityLog.timestamp.desc()).all()
        
        print(f"\n{'='*80}")
        print(f"最近{hours}小时的操作日志 (共{len(recent_logs)}条)")
        print(f"{'='*80}\n")
        
        if not recent_logs:
            print("暂无日志记录")
            return
        
        # 按操作类型分组统计
        action_stats = {}
        for log in recent_logs:
            action = log.action
            if action not in action_stats:
                action_stats[action] = 0
            action_stats[action] += 1
        
        print("操作统计:")
        print("-" * 80)
        for action, count in sorted(action_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {action:30s} : {count:3d} 次")
        
        print("\n详细日志:")
        print("-" * 80)
        for log in recent_logs[:50]:  # 只显示最近50条
            user = User.query.get(log.user_id)
            username = user.username if user else '未知用户'
            timestamp = log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            print(f"{timestamp} | {username:10s} | {log.action:30s} | {log.description}")


def check_announcement_logs():
    """检查公告相关的操作日志"""
    with app.app_context():
        announcement_actions = [
            '查看公告', '查看公告详情', '管理公告',
            '创建公告', '编辑公告', '删除公告',
            '发布公告', '取消发布公告', '置顶公告', '取消置顶'
        ]
        
        logs = UserActivityLog.query.filter(
            UserActivityLog.action.in_(announcement_actions)
        ).order_by(UserActivityLog.timestamp.desc()).limit(100).all()
        
        print(f"\n{'='*80}")
        print(f"公告模块操作日志 (共{len(logs)}条)")
        print(f"{'='*80}\n")
        
        if not logs:
            print("暂无公告相关日志")
            print("\n提示:")
            print("1. 尝试访问 /announcements 查看公告列表")
            print("2. 尝试创建一条新公告")
            print("3. 然后重新运行此脚本检查日志")
            return
        
        for log in logs:
            user = User.query.get(log.user_id)
            username = user.username if user else '未知用户'
            timestamp = log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            print(f"{timestamp} | {username:10s} | {log.action:20s} | {log.description}")


def check_wework_logs():
    """检查企业微信相关的操作日志"""
    with app.app_context():
        wework_actions = [
            '访问企业微信管理', '同步企业微信部门', '同步企业微信用户',
            '预览企业微信部门', '预览企业微信用户', '测试企业微信连接'
        ]
        
        logs = UserActivityLog.query.filter(
            UserActivityLog.action.in_(wework_actions)
        ).order_by(UserActivityLog.timestamp.desc()).limit(100).all()
        
        print(f"\n{'='*80}")
        print(f"企业微信模块操作日志 (共{len(logs)}条)")
        print(f"{'='*80}\n")
        
        if not logs:
            print("暂无企业微信相关日志")
            print("\n提示:")
            print("1. 访问 /admin/wework 查看企业微信管理页面")
            print("2. 尝试测试连接或预览数据")
            print("3. 然后重新运行此脚本检查日志")
            return
        
        for log in logs:
            user = User.query.get(log.user_id)
            username = user.username if user else '未知用户'
            timestamp = log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            print(f"{timestamp} | {username:10s} | {log.action:25s} | {log.description}")


def check_workflow_logs():
    """检查流程查询相关日志"""
    with app.app_context():
        # 查询访问流程状态页面的日志
        logs = UserActivityLog.query.filter(
            UserActivityLog.description.like('%流程状态%')
        ).order_by(UserActivityLog.timestamp.desc()).limit(50).all()
        
        print(f"\n{'='*80}")
        print(f"流程查询操作日志 (共{len(logs)}条)")
        print(f"{'='*80}\n")
        
        if logs:
            for log in logs:
                user = User.query.get(log.user_id)
                username = user.username if user else '未知用户'
                timestamp = log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                print(f"{timestamp} | {username:10s} | {log.action:20s} | {log.description}")
        else:
            print("暂无流程查询相关日志")


if __name__ == '__main__':
    print("="*80)
    print("操作日志检查工具")
    print("="*80)
    
    # 1. 检查最近的所有日志
    check_recent_logs(hours=24)
    
    # 2. 检查公告模块日志
    check_announcement_logs()
    
    # 3. 检查企业微信模块日志
    check_wework_logs()
    
    # 4. 检查流程查询日志
    check_workflow_logs()
    
    print("\n" + "="*80)
    print("检查完成!")
    print("="*80)
    print("\n说明:")
    print("1. 所有操作都会记录在 user_activity_log 表中")
    print("2. 可以在系统中访问 /user_activity_logs 查看完整日志")
    print("3. 日志包含: 时间、用户、操作类型、详细描述、IP地址")
