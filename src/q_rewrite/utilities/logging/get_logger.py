import os

from q_rewrite.enums import LogLevelEnum
from q_rewrite.tools import Logger

def get_logger() -> Logger:
    level = LogLevelEnum.DEBUG

    match os.environ.get("LOG_LEVEL", "DEBUG"):
        case "DEBUG":
            level = LogLevelEnum.DEBUG
        case "CRITICAL":
            level = LogLevelEnum.CRITICAL
        case "ERROR":
            level = LogLevelEnum.ERROR
        case "INFO":
            level = LogLevelEnum.INFO
        case "WARNING":
            level = LogLevelEnum.WARNING
        case _:
            pass

    return Logger(level=level)
