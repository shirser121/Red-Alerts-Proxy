from dotenv import load_dotenv
from datetime import timedelta
from celery import Celery
import requests

from red_alerts.shared import redis_client, REDIS_URL
from red_alerts.logger import logger
import os

load_dotenv()

API_URL = os.environ.get("API_URL")
UPDATE_INTERVAL = int(os.environ.get("UPDATE_INTERVAL", 10))
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", 10))


CELERYBEAT_SCHEDULE = {
    'update_data_task': {
        'task': 'update.update_data',
        'schedule': timedelta(seconds=UPDATE_INTERVAL),
    },
}

celery = Celery('update', broker=REDIS_URL)
celery.conf.beat_schedule = CELERYBEAT_SCHEDULE
celery.conf.worker_hijack_root_logger = False
celery.conf.timezone = 'UTC'


@celery.task(bind=True, autoretry_for=(Exception,), retry_backoff=2, retry_kwargs={'max_retries': 3})
def update_data(self):
    response = requests.get(API_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    new_data = response.content
    previous_data = redis_client.get('alerts_data')
    redis_client.set('alerts_data', new_data)
    if previous_data != new_data:
        logger.info("Data successfully fetched and updated.")
