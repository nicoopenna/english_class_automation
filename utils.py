# Configure logging
import logging
import os


def create_logging(logs_path):
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_path),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    return logger