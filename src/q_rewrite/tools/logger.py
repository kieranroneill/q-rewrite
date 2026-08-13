from q_rewrite.constants import LEVEL_COLORS, RESET, WHITE
from q_rewrite.enums import LogLevelEnum


class Logger:
    def __init__(self, level: LogLevelEnum = LogLevelEnum.INFO) -> None:
        self.level = level

    def _log(self, level: LogLevelEnum, msg: str) -> None:
        if level < self.level:
            return
        color = LEVEL_COLORS.get(level, WHITE)
        level_name = level.name
        print(f"{color}[{level_name}]{RESET}: {msg}")

    def debug(self, msg: str) -> None:
        self._log(LogLevelEnum.DEBUG, msg)

    def info(self, msg: str) -> None:
        self._log(LogLevelEnum.INFO, msg)

    def warning(self, msg: str) -> None:
        self._log(LogLevelEnum.WARNING, msg)

    def error(self, msg: str) -> None:
        self._log(LogLevelEnum.ERROR, msg)

    def critical(self, msg: str) -> None:
        self._log(LogLevelEnum.CRITICAL, msg)
