"""
PDF Processor module responsible for loading and extracting text from PDF files.
Can use either LLM-based extraction or PyPDF2 as fallback.
"""

from pathlib import Path
from typing import BinaryIO, Union

from loguru import logger

from .error_handler import handle_exceptions, validate_pdf
from .exceptions import TextExtractionError, ValidationError
from .extractors import create_extractor


class PDFProcessor:
    """Handles PDF file processing and text extraction."""

    def __init__(self, extraction_strategy: str = "pypdf2", **config):
        """
        Initialize PDFProcessor.

        Args:
            extraction_strategy: Strategy to use for text extraction
            **config: Additional configuration (e.g., llm_api_key for LLM strategy)
        """
        logger.debug(f"Initializing PDFProcessor with {extraction_strategy}")
        self.extractor = create_extractor(
            extraction_strategy,
            api_key=config.get('llm_api_key')
        )

    @handle_exceptions("Failed to load PDF file")
    @validate_pdf
    def load_pdf(self, file: Union[BinaryIO, Path, str]) -> str:
        """
        Load and validate a PDF file.

        Args:
            file: PDF file object, path, or string path

        Returns:
            Extracted text from the PDF

        Raises:
            ValidationError: If the file is not a valid PDF
            TextExtractionError: If text extraction fails
        """
        logger.info("Loading PDF file")

        # First validate the input
        if file is None:
            raise ValidationError("No file provided")

        try:
            # Convert file to binary if it's a path
            if isinstance(file, (str, Path)):
                logger.debug(f"Opening file from path: {file}")
                file = open(file, 'rb')

            # Ensure we have a binary file
            if not hasattr(file, 'read'):
                raise ValidationError("Invalid file object provided")

            return self.extractor.extract_text(file)

        except ValidationError:
            # Re-raise validation errors without wrapping
            raise
        except Exception as e:
            raise TextExtractionError(f"Failed to load PDF: {str(e)}")

    def _validate_pdf_content(self, file: BinaryIO) -> bool:
        """
        Validate PDF file content.

        Args:
            file: Binary file object to validate

        Returns:
            bool: True if file is valid, False otherwise

        Note:
            This is a placeholder for future implementation
        """
        logger.debug("Validating PDF content")
        # TODO: Implement PDF validation logic
        return True
