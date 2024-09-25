from flask import Flask
from flask_limiter import Limiter

from dotenv import load_dotenv

import os

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
