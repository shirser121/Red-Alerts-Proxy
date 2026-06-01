import os
from urllib.parse import urlsplit, urlunsplit

import redis

# Single source of truth for how to reach Redis. Override REDIS_URL to point at
# a different host/port, a password-protected or TLS (rediss://) instance, or a
# managed Redis service. Defaults to the bundled docker-compose service, so the
# standard setup keeps working unchanged.
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")


def redis_url_for_db(db):
    """Return ``REDIS_URL`` with its database number replaced by ``db``.

    Scheme, host, credentials and query string are preserved, so one REDIS_URL
    can drive both the cached data (db 0) and the rate limiter (db 1)."""
    return urlunsplit(urlsplit(REDIS_URL)._replace(path="/{}".format(db)))


# Storage backend for flask-limiter. Defaults to db 1 of REDIS_URL so rate-limit
# counters stay separate from the cached alert data; override RATELIMIT_REDIS_URL
# for managed Redis that exposes only a single database.
RATELIMIT_REDIS_URL = os.environ.get("RATELIMIT_REDIS_URL", redis_url_for_db(1))

# Bound how long Redis calls may block. Without these, a hung or unreachable
# Redis would make request handlers wait forever, surfacing as a gunicorn
# WORKER TIMEOUT instead of a clean error.
redis_client = redis.StrictRedis.from_url(
    REDIS_URL,
    socket_timeout=5,
    socket_connect_timeout=5,
)
