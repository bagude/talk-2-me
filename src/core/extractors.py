"""
Text extraction strategies for PDF processing.
Provides a common interface for different text extraction methods.
"""

from abc import ABC, abstractmethod
from typing import BinaryIO

from loguru import logger

from .exceptions import TextExtractionError
from .llm.service import create_llm_service, LLMAPIError


class TextExtractor(ABC):
    """Abstract base class for text extraction strategies."""

    @abstractmethod
    def extract_text(self, file: BinaryIO) -> str:
        """
        Extract text from a PDF file.

        Args:
            file: Binary file object of the PDF

        Returns:
            Extracted text from the PDF

        Raises:
            TextExtractionError: If text extraction fails
        """
        pass


class PyPDF2Extractor(TextExtractor):
    """Text extraction using PyPDF2 library."""

    def extract_text(self, file: BinaryIO) -> str:
        """Extract text using PyPDF2."""
        logger.debug("Starting PyPDF2 text extraction")

        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(file)

            # Check if PDF is encrypted
            if reader.is_encrypted:
                logger.warning("Encrypted PDF detected")
                raise TextExtractionError("Encrypted PDFs are not supported")

            # Extract text from all pages
            text_content = []
            total_pages = len(reader.pages)

            logger.info(f"Processing {total_pages} pages")

            for page_num in range(total_pages):
                logger.debug(
                    f"Extracting text from page {page_num + 1}/{total_pages}")
                page = reader.pages[page_num]
                text_content.append(page.extract_text())

            extracted_text = "\n".join(text_content)

            if not extracted_text.strip():
                logger.warning("No text content extracted from PDF")
                raise TextExtractionError("No text content found in PDF")

            logger.success(
                f"Successfully extracted {len(extracted_text)} characters")
            return extracted_text

        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {str(e)}")
            raise TextExtractionError(f"Failed to extract text: {str(e)}")


class LLMExtractor(TextExtractor):
    """Text extraction using LLM-based approach."""

    def __init__(self, api_key: str, provider: str = "gemini"):
        """Initialize LLM extractor."""
        self.llm = create_llm_service(provider, api_key=api_key)
        self._extraction_prompt = """
        Extract and structure all content from this PDF.
        Maintain the original formatting and organization.
        Include descriptions of any tables, figures, or diagrams.
        Preserve headers, sections, and hierarchical structure.
        """

    def extract_text(self, file: BinaryIO) -> str:
        """Extract text using LLM's native PDF processing."""
        try:
            return self.llm.process_pdf(file, self._extraction_prompt)
        except LLMAPIError as e:
            logger.error(f"LLM extraction failed: {str(e)}")
            raise TextExtractionError(f"Failed to extract text: {str(e)}")


def create_extractor(strategy: str = "pypdf2", **kwargs) -> TextExtractor:
    """
    Factory function to create text extractors.

    Args:
        strategy: The extraction strategy to use ("pypdf2" or "llm")
        **kwargs: Additional arguments for the extractor (e.g., api_key for LLM)

    Returns:
        TextExtractor: An instance of the requested extractor

    Raises:
        ValueError: If the strategy is not recognized
    """
    extractors = {
        "pypdf2": PyPDF2Extractor,
        "llm": LLMExtractor,
    }

    try:
        extractor_class = extractors[strategy.lower()]
        logger.info(f"Creating text extractor with strategy: {strategy}")

        if strategy.lower() == "llm":
            if "api_key" not in kwargs:
                raise ValueError("api_key is required for LLM extractor")
            return extractor_class(api_key=kwargs["api_key"])

        return extractor_class()
    except KeyError:
        logger.error(f"Unknown extraction strategy: {strategy}")
        raise ValueError(f"Unknown extraction strategy: {strategy}")
