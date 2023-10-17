from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import json

from red_alerts.logger import logger
from red_alerts.shared import redis_client
from red_alerts.routes import init_routes

app = Flask(__name__)
limiter = Limiter(
    app,
    storage_uri="redis://redis:6379/1"
)
limiter.init_app(app)

init_routes(app)
