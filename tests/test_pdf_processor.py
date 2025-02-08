"""
Test suite for PDF processing functionality
"""

import io
from unittest.mock import Mock, patch
import pytest
from pathlib import Path

from src.core.pdf_processor import PDFProcessor
from src.core.exceptions import ValidationError, TextExtractionError
from src.core.extractors import create_extractor, TextExtractor


@pytest.fixture
def pdf_processor():
    return PDFProcessor()


@pytest.fixture
def sample_pdf():
    # Create a simple PDF in memory for testing
    try:
        from reportlab.pdfgen import canvas
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)
        c.drawString(100, 100, "Test PDF content")
        c.save()
        buffer.seek(0)
        return buffer
    except Exception as e:
        pytest.skip(f"Failed to create sample PDF: {str(e)}")


class MockExtractor(TextExtractor):
    """Mock extractor for testing"""

    def extract_text(self, file: io.BytesIO) -> str:
        return "Mocked extracted text"


def test_pdf_loading(pdf_processor, sample_pdf):
    """Test basic PDF loading functionality"""
    text = pdf_processor.load_pdf(sample_pdf)
    assert "Test PDF content" in text


def test_invalid_file(pdf_processor):
    """Test handling of invalid file input"""
    with pytest.raises(ValidationError):
        pdf_processor.load_pdf(None)


def test_empty_pdf(pdf_processor):
    """Test handling of PDF with no text content"""
    empty_pdf = io.BytesIO(b"%PDF-1.4\n%EOF")
    with pytest.raises(TextExtractionError):
        pdf_processor.load_pdf(empty_pdf)


def test_extractor_factory():
    """Test text extractor factory"""
    pypdf2_extractor = create_extractor("pypdf2")
    assert pypdf2_extractor.__class__.__name__ == "PyPDF2Extractor"

    with pytest.raises(ValueError):
        create_extractor("invalid_strategy")

    # Test LLM extractor with api_key
    llm_extractor = create_extractor("llm", api_key="test_key")
    assert llm_extractor.__class__.__name__ == "LLMExtractor"


def test_processor_with_different_strategies():
    """Test PDFProcessor with different extraction strategies"""
    processor_pypdf2 = PDFProcessor(extraction_strategy="pypdf2")
    assert processor_pypdf2.extractor.__class__.__name__ == "PyPDF2Extractor"

    # Test with LLM strategy and api_key
    processor_llm = PDFProcessor(
        extraction_strategy="llm",
        llm_api_key="test_key"  # Add this parameter
    )
    assert processor_llm.extractor.__class__.__name__ == "LLMExtractor"


def test_processor_with_file_path(tmp_path):
    """Test PDFProcessor with file path input"""
    pdf_path = tmp_path / "test.pdf"

    # Create a test PDF file
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(pdf_path))
    c.drawString(100, 100, "File path test content")
    c.save()

    processor = PDFProcessor()
    text = processor.load_pdf(pdf_path)
    assert "File path test content" in text


def test_processor_with_mock_extractor():
    """Test PDFProcessor with a mock extractor"""
    mock_extractor = MockExtractor()

    # Patch before creating the processor
    with patch('src.core.pdf_processor.create_extractor', return_value=mock_extractor):
        processor = PDFProcessor(extraction_strategy="mock")
        result = processor.load_pdf(io.BytesIO(b"dummy content"))

        assert result == "Mocked extracted text"
