import redis

redis_client = redis.Redis(host='redis', socket_connect_timeout=5, socket_timeout=10)
