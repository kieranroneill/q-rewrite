import logging


def get_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)

    logging.basicConfig(level=logging.INFO)

    for handler in logger.handlers:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s"))

    return logger
