import logging
import sys

logger = logging.getLogger("mootdx")
logger.addHandler(logging.NullHandler())

_FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def setup_logging(level: int = logging.INFO, stream=None) -> None:
    """Configure mootdx console logging. Call once at application startup.

    Libraries should never configure handlers at import time — this function
    exists so CLI entry points and scripts can opt in to console output.
    """
    logger.handlers.clear()
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(_FORMATTER)
    logger.addHandler(handler)
    logger.setLevel(level)
