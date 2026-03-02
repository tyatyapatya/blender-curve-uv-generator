import logging

from ..constants import ADDON_ID


def get_logger() -> logging.Logger:
    logger = logging.getLogger(ADDON_ID)
    if not logger.handlers:
        logger.addHandler(logging.NullHandler())
    return logger
