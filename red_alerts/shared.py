import redis

# Bound how long Redis calls may block. Without these, a hung or unreachable
# Redis would make request handlers wait forever, surfacing as a gunicorn
# WORKER TIMEOUT instead of a clean error.
redis_client = redis.StrictRedis(
    host='redis',
    port=6379,
    db=0,
    socket_timeout=5,
    socket_connect_timeout=5,
)
