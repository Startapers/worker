

import json


class CacheDal:
    def __init__(self, redis) -> None:
        self.redis = redis

    async def set(self, key, value):
        self.redis.set(key, value)
        return

    async def get(self, key):
        res = self.redis.rpop(key)
        if not res:
            return None
        res = res.decode()
        return json.loads(res) if res else None


async def create(redis, logger):
    return CacheDal(redis)
