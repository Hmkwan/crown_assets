import threading
import os
from app import create_app


def test_fd2_filter_not_installed_by_default():
    # 默认情况下不应该安装强力 fd2 过滤器（需要显式 ENABLE_FD2_FILTER=1）
    os.environ.pop('ENABLE_FD2_FILTER', None)
    create_app()
    names = [t.name for t in threading.enumerate()]
    assert 'fd2-filter' not in names
