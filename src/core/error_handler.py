"""
Error handling utilities for graceful error management and logging.
"""

import functools
from typing import Callable, TypeVar, ParamSpec

from loguru import logger

from .exceptions import PDFAudioError

# Type variables for generic function decorators
P = ParamSpec('P')
T = TypeVar('T')


def handle_exceptions(error_message: str = "An error occurred") -> Callable:
    """
    Decorator for handling exceptions in a consistent way across the application.

    Args:
        error_message: Custom error message to use when an error occurs

    Returns:
        Decorated function with error handling
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except PDFAudioError as e:
                logger.error(f"{error_message}: {str(e)}")
                raise
            except Exception as e:
                logger.exception(
                    f"Unexpected error - {error_message}: {str(e)}")
                raise PDFAudioError(
                    f"{error_message}: {str(e)}", original_error=e)
        return wrapper
    return decorator


def validate_pdf(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator for validating PDF files before processing.

    Args:
        func: Function to decorate

    Returns:
        Decorated function with PDF validation
    """
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        logger.debug("Validating PDF file")
        # Add PDF validation logic here
        return func(*args, **kwargs)
    return wrapper
