# 工具模块

from datetime import datetime, timedelta, timezone


def get_beijing_now():
    """获取当前北京时间(Asia/Shanghai) - 返回时区感知的 datetime"""
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz)
