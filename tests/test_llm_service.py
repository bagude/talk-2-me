"""
Test suite for LLM service functionality.
"""

import io
from unittest.mock import Mock, patch
import pytest

from src.core.llm.service import (
    GeminiService,
    create_llm_service,
    LLMError,
    LLMAPIError
)


@pytest.fixture
def mock_genai():
    """Mock the google.generativeai module."""
    with patch(GeminiService.GENAI_IMPORT, create=True) as mock:
        # Mock the response
        mock_response = Mock()
        mock_response.text = "Processed content"

        # Mock the model
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response

        # Mock GenerativeModel
        mock.GenerativeModel.return_value = mock_model

        yield mock


@pytest.fixture
def llm_service(mock_genai):
    """Create a GeminiService instance with mocked dependencies."""
    service = GeminiService(api_key="test_key")
    return service


def test_process_text(llm_service):
    """Test text processing."""
    result = llm_service.process_text(
        text="test text",
        prompt_template="Process this: {text}"
    )
    assert result == "Processed content"
    llm_service._client.generate_content.assert_called_once()


def test_process_pdf(llm_service):
    """Test PDF processing."""
    pdf_file = io.BytesIO(b"fake pdf content")

    result = llm_service.process_pdf(
        file=pdf_file,
        prompt_template="Analyze this PDF"
    )

    assert result == "Processed content"
    llm_service._client.generate_content.assert_called_once()


def test_empty_response(llm_service):
    """Test handling of empty responses."""
    # Mock empty response
    llm_service._client.generate_content.return_value.text = ""

    with pytest.raises(LLMError, match="Empty response from Gemini"):
        llm_service.process_text("test", "test prompt")


def test_api_error(llm_service):
    """Test handling of API errors."""
    # Mock API error
    llm_service._client.generate_content.side_effect = Exception("API Error")

    with pytest.raises(LLMAPIError, match="Failed to process text"):
        llm_service.process_text("test", "test prompt")


def test_create_llm_service():
    """Test LLM service factory."""
    with patch('src.core.llm.service.GeminiService') as mock_gemini:
        service = create_llm_service("gemini", api_key="test_key")
        mock_gemini.assert_called_once_with(api_key="test_key")

    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        create_llm_service("unsupported_provider")


def test_pdf_processing_error(llm_service):
    """Test handling of PDF processing errors."""
    pdf_file = io.BytesIO(b"fake pdf content")

    # Mock processing error
    llm_service._client.generate_content.side_effect = Exception("PDF Error")

    with pytest.raises(LLMAPIError, match="Failed to process PDF"):
        llm_service.process_pdf(pdf_file, "test prompt")
