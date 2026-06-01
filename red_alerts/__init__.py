from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from dotenv import load_dotenv

import os
import json

from red_alerts.logger import logger
from red_alerts.shared import RATELIMIT_REDIS_URL
from red_alerts.routes import init_routes

load_dotenv()
API_URL = os.environ.get("API_URL")
if not API_URL:
    raise Exception("API_URL is not set")

app = Flask(__name__)
limiter = Limiter(
    app,
    storage_uri=RATELIMIT_REDIS_URL
)
limiter.init_app(app)

init_routes(app)
