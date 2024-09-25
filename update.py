from dotenv import load_dotenv
from datetime import timedelta
from celery import Celery
import requests
import json

from red_alerts.shared import redis_client
from red_alerts.logger import logger
import os

# Load environment variables
load_dotenv()

API_URL = os.environ.get("API_URL")
UPDATE_INTERVAL = int(os.environ.get("UPDATE_INTERVAL", 10))

# Celery beat schedule for periodic task execution
CELERYBEAT_SCHEDULE = {
    'update_data_task': {
        'task': 'update.update_data',
        'schedule': timedelta(seconds=UPDATE_INTERVAL),
    },
}

# Celery app configuration
celery = Celery('update', broker='redis://redis:6379/0')
celery.conf.beat_schedule = CELERYBEAT_SCHEDULE
celery.conf.worker_hijack_root_logger = False
celery.conf.timezone = 'UTC'
celery.conf.task_time_limit = 300  # Max time a task can run (5 minutes)
celery.conf.task_soft_time_limit = 270  # Grace period of 30 seconds before hard limit


@celery.task(bind=True, max_retries=5)
def update_data(self):
    lock_id = "celery-update-data-lock"
    try:
        # Try to acquire a Redis lock to avoid task overlap
        if redis_client.set(lock_id, "1", nx=True, ex=UPDATE_INTERVAL):
            logger.info(f"Starting data update task: {self.request.id}")

            # Fetch data with a timeout
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()

            # Decode the JSON response
            jsonData = json.loads(response.content.decode('utf-8'))

            # Ensure the data is valid before storing it in Redis
            if not jsonData:
                raise ValueError("JSON data is empty")

            # Use a Redis pipeline to atomically set data and expiry
            with redis_client.pipeline() as pipe:
                pipe.set('alerts_data', json.dumps(jsonData))
                pipe.expire('alerts_data', UPDATE_INTERVAL + 10)
                pipe.execute()

            logger.info(f"Data successfully updated for task: {self.request.id}")

        else:
            logger.info("Skipping task execution due to an active lock.")

    except requests.exceptions.Timeout:
        logger.error(f"Timeout occurred while fetching data from {API_URL}. Retrying...")
        self.retry(exc=Exception("API Timeout"), countdown=60)

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from {API_URL}: {e}. Retrying...")
        self.retry(exc=e, countdown=60)  # Retry in 60 seconds on failure

    except Exception as e:
        logger.error(f"Unexpected error in task {self.request.id}: {e}")
        raise e

    finally:
        # Clean up the Redis lock if the task completed successfully
        redis_client.delete(lock_id)
