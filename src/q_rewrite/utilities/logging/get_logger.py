from q_rewrite.enums import LogLevelEnum
from q_rewrite.tools import Logger

def get_logger() -> Logger:
    return Logger(level=LogLevelEnum.DEBUG)
