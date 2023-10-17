from dotenv import load_dotenv
from datetime import timedelta
from celery import Celery
import requests
import json

from red_alerts.shared import redis_client
from red_alerts.logger import logger
import os

load_dotenv()

API_URL = os.environ.get("API_URL")
UPDATE_INTERVAL = int(os.environ.get("UPDATE_INTERVAL", 10))


CELERYBEAT_SCHEDULE = {
    'update_data_task': {
        'task': 'update.update_data',
        'schedule': timedelta(seconds=UPDATE_INTERVAL),
    },
}

celery = Celery('update', broker='redis://redis:6379/0')
celery.conf.beat_schedule = CELERYBEAT_SCHEDULE
celery.conf.worker_hijack_root_logger = False
celery.conf.timezone = 'UTC'


@celery.task(bind=True)
def update_data(self):
    global jsonData
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # raises exception when not a 2xx response
        content = response.content.decode('utf-8')
        jsonData = json.loads(content)
        redis_client.set('alerts_data', json.dumps(jsonData))
        logger.info("Data successfully fetched and updated.")

    except Exception as e:
        logger.error(f'Error fetching data: {e}')
