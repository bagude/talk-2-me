"""
Logging configuration module using Loguru.
Provides a centralized logging setup for the entire application.
"""

import sys
from pathlib import Path
from loguru import logger


def setup_logger():
    """
    Configure Loguru logger with both file and console outputs.

    File logs will include:
    - Detailed timestamps
    - Log levels
    - Module names
    - Function names
    - Line numbers
    - Full exception tracebacks
    """
    # Remove default logger
    logger.remove()

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Add console logger with color
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level="INFO",
        colorize=True
    )

    # Add file logger with more detailed output
    logger.add(
        "logs/app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
               "{name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="500 MB",  # Create new file when size exceeds 500MB
        retention="10 days",  # Keep logs for 10 days
        backtrace=True,  # Detailed exception information
        diagnose=True    # Even more detailed exception information
    )

    # Add error-specific logger
    logger.add(
        "logs/errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
               "{name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="100 MB",
        retention="30 days",
        backtrace=True,
        diagnose=True,
        filter=lambda record: record["level"].name == "ERROR"
    )

    logger.info("Logger initialized successfully")


# Initialize logger when module is imported
setup_logger()

# Export logger for use in other modules
__all__ = ["logger"]
