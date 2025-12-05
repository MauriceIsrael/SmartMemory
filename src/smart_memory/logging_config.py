"""
Logging configuration for Semantic Memory MCP Server.

Configures structured logging with appropriate levels for different components.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from smart_memory.config import config


def setup_logging(level: Optional[str] = None, log_file: Optional[str] = None) -> logging.Logger:
    """
    Configure logging for the Semantic Memory server.

    Args:
        level: Optional log level override (defaults to config.log_level)
        log_file: Optional file path for logging (in addition to stderr)

    Returns:
        Configured logger instance
    """
    log_level = level or config.log_level

    # Create logger
    logger = logging.getLogger("smart_memory")
    logger.setLevel(getattr(logging, log_level))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (stderr)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional file handler
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, mode='a')
            file_handler.setLevel(getattr(logging, log_level))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.info(f"File logging enabled: {log_file}")
        except Exception as e:
            logger.warning(f"Failed to setup file logging to {log_file}: {e}")

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module name (e.g., "smart_memory.inference")

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Check for log file from environment
import os
log_file_path = os.environ.get("SEMMEM_LOG_FILE")

# Initialize default logger
default_logger = setup_logging(log_file=log_file_path)

__all__ = ["setup_logging", "get_logger", "default_logger"]
