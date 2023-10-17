import os
import logging
from logging.handlers import RotatingFileHandler

if not os.path.exists('logs'):
    os.makedirs('logs')

# Set up logging
log_format = "[%(asctime)s] [%(levelname)s] - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)

# Add rotating file handler
file_handler = RotatingFileHandler("logs/app.log", maxBytes=1000000, backupCount=5)
file_handler.setFormatter(logging.Formatter(log_format))
logging.getLogger().addHandler(file_handler)

# Add stream handler (optional if you want logs to also print to console)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(log_format))
logging.getLogger().addHandler(stream_handler)

celery_logger = logging.getLogger('celery')
celery_logger.setLevel(logging.CRITICAL)


logger = logging.getLogger(__name__)
