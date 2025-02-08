"""
Core exceptions module defining custom exceptions for the PDF-to-Audio processor.
Provides a hierarchy of application-specific exceptions for better error handling.
"""

from typing import Optional


class PDFAudioError(Exception):
    """Base exception class for all application-specific errors."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error


class PDFProcessingError(PDFAudioError):
    """Raised when there are issues processing the PDF file."""
    pass


class TextExtractionError(PDFProcessingError):
    """Raised when text cannot be extracted from the PDF."""
    pass


class LLMError(PDFAudioError):
    """Base class for LLM-related errors."""
    pass


class LLMAPIError(LLMError):
    """Raised when there are issues with the LLM API."""
    pass


class LLMProcessingError(LLMError):
    """Raised when the LLM fails to process the text."""
    pass


class TTSError(PDFAudioError):
    """Base class for Text-to-Speech related errors."""
    pass


class TTSAPIError(TTSError):
    """Raised when there are issues with the TTS API."""
    pass


class AudioGenerationError(TTSError):
    """Raised when there are issues generating the audio file."""
    pass


class ValidationError(PDFAudioError):
    """Raised when input validation fails."""
    pass
