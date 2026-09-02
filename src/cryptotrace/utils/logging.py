"""
Logging configuration utilities for CryptoTrace AI.
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "cryptotrace", level: int = logging.INFO) -> logging.Logger:
    """Configure and return a standard formatted logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
