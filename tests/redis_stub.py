"""Simple in-memory redis stub used for tests when redis-py is not installed."""
class Redis:
    def __init__(self, *args, **kwargs):
        self._sets = {}
        self._hashes = {}
    def sadd(self, key, value):
        self._sets.setdefault(key, set()).add(value)
    def srem(self, key, value):
        if key in self._sets:
            self._sets[key].discard(value)
    def hset(self, key, field, value):
        self._hashes.setdefault(key, {})[field] = value
    def hget(self, key, field):
        return self._hashes.get(key, {}).get(field)
    def delete(self, key):
        self._sets.pop(key, None)
        self._hashes.pop(key, None)
    def ping(self):
        return True
# Provide a convenience constructor similar to redis.Redis
def RedisClient(*args, **kwargs):
    return Redis(*args, **kwargs)

# Compatibility: some code expects redis.from_url()
def from_url(url, **kwargs):
    # 解析 url 不是必需的：简单地返回一个 Redis 实例
    return Redis(**kwargs)

# 兼容 redis.Redis(...) 调用风格
def Redis(*args, **kwargs):
    return RedisClient(*args, **kwargs)
