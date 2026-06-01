"""Gunicorn configuration.

The proxy is exposed directly to the public internet, so it constantly gets
port scanners and bots that open a connection and then send a partial request
(or nothing at all). With the default *sync* worker, gunicorn reads each
request inside the worker and blocks on the socket, so a single slow/idle
client ties up an entire worker until the request timeout kills it
("WORKER TIMEOUT" / "Error handling request (no URI read)"). With only a few
workers that is a cheap way to starve the whole pool.

Threaded (gthread) workers decouple the worker heartbeat from request handling
and serve many connections per worker, so a stalled client occupies one thread
instead of a whole worker and no longer trips the timeout. gthread ships with
gunicorn, so this needs no extra dependency.
"""

import os

bind = "0.0.0.0:3007"

worker_class = "gthread"
workers = int(os.environ.get("GUNICORN_WORKERS", 3))
threads = int(os.environ.get("GUNICORN_THREADS", 4))

# Liveness timeout. For threaded workers this guards against a genuinely stuck
# worker rather than a slow client, so the default 30s is plenty.
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 30))
graceful_timeout = 30

# Drop idle keep-alive connections quickly so scanners can't park them.
keepalive = 5
