import redis
from groundible_admin.root.settings import Settings

settings = Settings()
redis_url = str(settings.redis_url)
gr_redis = redis.Redis(decode_responses=True)
gr_redis.from_url(url=redis_url)
