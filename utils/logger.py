import logging
import os

# Set up logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.path.join("results", "etl_log.log")


def get_logger(name):
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent logger from adding multiple handlers if called multiple times
    if not logger.hasHandlers():
        # Create handlers
        file_handler = logging.FileHandler(LOG_FILE)
        console_handler = logging.StreamHandler()

        # Set logging levels
        file_handler.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)

        # Create formatters and add them to the handlers
        formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
