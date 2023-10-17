import os
import logging
from logging.handlers import RotatingFileHandler

if not os.path.exists('./logs'):
    os.makedirs('./logs')

# Set up logging
log_format = "[%(asctime)s] [%(levelname)s] - %(message)s"

# Add rotating file handler
file_handler = RotatingFileHandler("./logs/app.log", maxBytes=1000000, backupCount=5)
file_handler.setFormatter(logging.Formatter(log_format))
logging.getLogger().addHandler(file_handler)

# Add stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(log_format))
logging.getLogger().addHandler(stream_handler)
logging.getLogger().setLevel(logging.INFO)  # Set logging level here

celery_logger = logging.getLogger('celery')
celery_logger.setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)
