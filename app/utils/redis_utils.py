import os
import time
try:
    import redis
    REDIS_AVAILABLE = True
except Exception:
    redis = None
    REDIS_AVAILABLE = False
import socket
import errno
import logging

logger = logging.getLogger(__name__)


def _host_resolves(host: str, port: int = None) -> bool:
    try:
        # 使用端口参数可以避免部分系统的 getaddrinfo 行为差异
        service = str(port) if port else None
        socket.getaddrinfo(host, service)
        return True
    except socket.gaierror as e:
        # EAI_AGAIN 通常表示临时 DNS 解析失败（可重试）；其他错误也视为不可达
        return False
    except Exception:
        return False


def create_redis_client(host=None, port=None, db=None, max_retries=6, initial_delay=1):
    """创建 Redis 客户端，包含更稳健的 DNS 错误处理和可控的重试策略。"""
    # 支持通过环境变量快速禁用 Redis（例如在一次性脚本/测试中）
    if os.environ.get('REDIS_DISABLED', '0') == '1':
        logger.debug('REDIS_DISABLED=1, skip creating Redis client')
        return None
    host = host or os.environ.get('REDIS_HOST', 'redis')
    port = int(port or os.environ.get('REDIS_PORT', '6379'))
    db = int(db or os.environ.get('REDIS_DB', '0'))

    # 如果 redis 库不可用，快速返回 None
    if not REDIS_AVAILABLE:
        logger.debug('redis 库不可用，跳过 Redis 客户端创建。')
        return None

    for attempt in range(1, max_retries + 1):
        try:
            # 直接尝试建立 Redis 连接；若 DNS 临时失败或网络不稳定，下面的异常处理会按策略重试
            client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            client.ping()
            logger.info(f"✓ Redis连接成功: {host}:{port}/{db}")
            return client
        except Exception as e:
            # 如果是 redis exceptions.ConnectionError，仍然会落到这里统一处理
            msg = str(e)
            # 对于连接/解析类问题，降低日志级别为 DEBUG 以减少噪音，同时继续重试
            msg = str(e)
            is_dns_issue = 'Lookup timed out' in msg or 'Name or service not known' in msg or isinstance(e.__cause__, OSError) and getattr(e.__cause__, 'errno', None) in (errno.EAI_AGAIN, errno.EHOSTUNREACH)
            delay = min(initial_delay * (2 ** (attempt - 1)), 30)
            if is_dns_issue:
                logger.debug(f"Redis 连接临时失败(尝试 {attempt}/{max_retries}): {e}. {delay}s 后重试...")
            else:
                logger.warning(f"⚠ Redis连接失败(尝试 {attempt}/{max_retries}): {e}. {delay}s 后重试...")
            time.sleep(delay)
            continue
        except Exception as e:
            if attempt < max_retries:
                delay = min(initial_delay * (2 ** (attempt - 1)), 30)
                logger.warning(f"⚠ Redis连接失败(尝试 {attempt}/{max_retries}): {e}. {delay}s 后重试...")
                time.sleep(delay)
            else:
                logger.error(f"✗ Redis最终失败: {e}")
                return None
