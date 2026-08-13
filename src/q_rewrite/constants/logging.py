from q_rewrite.enums import LogLevelEnum

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

LEVEL_COLORS = {
    LogLevelEnum.DEBUG: CYAN,
    LogLevelEnum.INFO: GREEN,
    LogLevelEnum.WARNING: YELLOW,
    LogLevelEnum.ERROR: RED,
    LogLevelEnum.CRITICAL: MAGENTA,
}
