import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_DIR: Path = Path(__file__).resolve().parents[2] / "logs"
LOG_FILE: Path = LOG_DIR / "backend.log"
LOG_FORMAT: str = "[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s"
MAX_LOG_SIZE_BYTES: int = 10 * 1024 * 1024
BACKUP_LOG_COUNT: int = 5

logger: logging.Logger = logging.getLogger("polarus")


def setup_logging() -> logging.Logger:
    """Configure application logging for console and rotating file output."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_LOG_SIZE_BYTES,
        backupCount=BACKUP_LOG_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
