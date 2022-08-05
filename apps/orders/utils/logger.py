import logging
from typing import Optional


def get_default_logger(name: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt='[%(asctime)s:%(levelname)s:%(name)s] %(message)s'
        )
    )
    logger.addHandler(handler)
    logger.propagate = False
    return logger
