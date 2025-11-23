"""
Logging configuration for Semantic Memory MCP Server.

Configures structured logging with appropriate levels for different components.
"""

import logging
import sys
from typing import Optional

from semantic_memory.config import config


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """
    Configure logging for the Semantic Memory server.

    Args:
        level: Optional log level override (defaults to config.log_level)

    Returns:
        Configured logger instance
    """
    log_level = level or config.log_level

    # Create logger
    logger = logging.getLogger("semantic_memory")
    logger.setLevel(getattr(logging, log_level))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler with formatting
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(getattr(logging, log_level))

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module name (e.g., "semantic_memory.inference")

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Initialize default logger
default_logger = setup_logging()

__all__ = ["setup_logging", "get_logger", "default_logger"]
