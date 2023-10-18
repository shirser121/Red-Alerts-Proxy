from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from dotenv import load_dotenv

import json

from red_alerts.logger import logger
from red_alerts.shared import redis_client
from red_alerts.routes import init_routes

load_dotenv()
API_URL = os.environ.get("API_URL")
if not API_URL:
    raise Exception("API_URL is not set")

app = Flask(__name__)
limiter = Limiter(
    app,
    storage_uri="redis://redis:6379/1"
)
limiter.init_app(app)

init_routes(app)
