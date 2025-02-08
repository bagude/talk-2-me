"""
Test suite for PDF service functionality
"""

import io
from pathlib import Path
import pytest
from unittest.mock import patch

from src.services.pdf_service import PDFService
from src.core.exceptions import ValidationError, TextExtractionError
from src.core.extractors import TextExtractor


class MockExtractor(TextExtractor):
    """Mock extractor for testing"""

    def extract_text(self, file: io.BytesIO) -> str:
        return "Mocked service text"


@pytest.fixture
def pdf_service():
    return PDFService()


@pytest.fixture
def sample_pdf():
    # Create a simple PDF in memory for testing
    try:
        from reportlab.pdfgen import canvas
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)
        c.drawString(100, 100, "Service test content")
        c.save()
        buffer.seek(0)
        return buffer
    except Exception as e:
        pytest.skip(f"Failed to create sample PDF: {str(e)}")


def test_pdf_service_initialization():
    """Test service initialization"""
    service = PDFService()
    assert service.get_extracted_text() is None


def test_pdf_processing(pdf_service, sample_pdf):
    """Test PDF processing through service"""
    text = pdf_service.process_file(sample_pdf)
    assert "Service test content" in text
    assert pdf_service.get_extracted_text() == text


def test_service_with_invalid_file(pdf_service):
    """Test service handling of invalid file"""
    with pytest.raises(ValidationError):
        pdf_service.process_file(None)


def test_service_with_mock_processor():
    """Test service with mocked processor"""
    mock_extractor = MockExtractor()

    with patch('src.core.pdf_processor.create_extractor', return_value=mock_extractor):
        service = PDFService()
        result = service.process_file(io.BytesIO(b"dummy content"))
        assert result == "Mocked service text"


def test_service_clear_state(pdf_service, sample_pdf):
    """Test clearing service state"""
    pdf_service.process_file(sample_pdf)
    assert pdf_service.get_extracted_text() is not None

    pdf_service.clear()
    assert pdf_service.get_extracted_text() is None


def test_service_with_different_strategies(pdf_service, sample_pdf):
    """Test service with different extraction strategies"""
    # Test with PyPDF2
    text_pypdf2 = pdf_service.process_file(
        sample_pdf, extraction_strategy="pypdf2")
    assert "Service test content" in text_pypdf2

    # Test with invalid strategy
    with pytest.raises(ValueError):
        pdf_service.process_file(sample_pdf, extraction_strategy="invalid")
