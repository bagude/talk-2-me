"""
Test suite for text extraction strategies.
"""

import io
from unittest.mock import Mock, patch
import pytest

from src.core.extractors import (
    create_extractor,
    PyPDF2Extractor,
    LLMExtractor,
    TextExtractionError
)
from src.core.llm.service import LLMAPIError


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service."""
    with patch('src.core.extractors.create_llm_service') as mock:
        service = Mock()
        service.process_pdf.return_value = "LLM extracted text"
        mock.return_value = service
        yield mock


def test_llm_extractor(mock_llm_service):
    """Test LLM-based extraction."""
    extractor = LLMExtractor(api_key="test_key")
    pdf_file = io.BytesIO(b"fake pdf content")

    result = extractor.extract_text(pdf_file)

    assert result == "LLM extracted text"
    mock_llm_service.assert_called_once_with("gemini", api_key="test_key")
    extractor.llm.process_pdf.assert_called_once()


def test_llm_extraction_error(mock_llm_service):
    """Test LLM extraction error handling."""
    extractor = LLMExtractor(api_key="test_key")
    pdf_file = io.BytesIO(b"fake pdf content")

    # Mock extraction error
    extractor.llm.process_pdf.side_effect = LLMAPIError("LLM Error")

    with pytest.raises(TextExtractionError):
        extractor.extract_text(pdf_file)


def test_create_extractor_with_llm():
    """Test creating LLM extractor through factory."""
    with patch('src.core.extractors.LLMExtractor') as mock_llm:
        create_extractor("llm", api_key="test_key")
        mock_llm.assert_called_once_with(api_key="test_key")


def test_invalid_strategy():
    """Test invalid extraction strategy."""
    with pytest.raises(ValueError, match="Unknown extraction strategy"):
        create_extractor("invalid")
