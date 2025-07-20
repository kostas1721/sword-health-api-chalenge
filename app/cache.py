import aioredis
import json
from datetime import datetime

redis = None

def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

async def init_redis():
    global redis
    redis = await aioredis.from_url("redis://redis:6379", decode_responses=True)

async def get_cache(key: str):
    data = await redis.get(key)
    return json.loads(data) if data else None

async def set_cache(key: str, value, expire=300):
    await redis.set(key, json.dumps(value, default=json_serial), ex=expire)
