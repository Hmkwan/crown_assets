# 工具模块

from datetime import datetime, timedelta


def get_beijing_now():
    """获取当前北京时间(Asia/Shanghai)"""
    try:
        import pytz
        tz = pytz.timezone('Asia/Shanghai')
        return datetime.now(tz).replace(tzinfo=None)
    except:
        # 如果pytz不可用,使用UTC+8
        return datetime.utcnow() + timedelta(hours=8)
