import logging

from application.common.config import config


def init_logger() -> logging.Logger:
    logger = logging.getLogger(config.project_name)
    if logger.handlers:
        return logger
    logger.setLevel(getattr(logging, config.log.level.upper(), logging.INFO))
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    logger.addHandler(handler)
    return logger


logger = init_logger()
