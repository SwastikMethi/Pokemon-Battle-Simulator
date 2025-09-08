import logging
from logging.handlers import RotatingFileHandler
import os

# Ensure logs directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "pokemon.log")

# Always use the same logger name
logger = logging.getLogger("pokemon_app")
logger.setLevel(logging.DEBUG)

# Avoid duplicate handlers if re-imported
if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s"
    )

    rotating_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=100 * 1024 * 1024,  # 100 MB
        backupCount=5
    )
    rotating_handler.setFormatter(formatter)
    rotating_handler.setLevel(logging.DEBUG)

    logger.addHandler(rotating_handler)

    # Optional console logs too
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
