"""
Service layer for coordinating PDF processing operations.
Provides a clean API for the UI layer to interact with core functionality.
"""

from pathlib import Path
from typing import BinaryIO, Optional, Union, Tuple
import io
import fitz  # PyMuPDF for PDF rendering
import base64
from loguru import logger

from src.core.exceptions import PDFAudioError, ValidationError
from src.core.pdf_processor import PDFProcessor
from src.core.llm.prompts import prompts
from src.core.llm.prompt_types import PromptType
from src.core.llm.service import create_llm_service


class PDFService:
    """Service for handling PDF processing operations."""

    def __init__(self):
        """Initialize PDF service."""
        logger.debug("Initializing PDF Service")

        # Load environment variables
        from dotenv import load_dotenv
        import os
        from pathlib import Path

        # Get project root directory
        root_dir = Path(__file__).parent.parent.parent
        env_path = root_dir / '.env'

        logger.debug(f"Looking for .env file at: {env_path}")
        load_dotenv(env_path)

        # Use GEMINI_API_KEY instead of GOOGLE_API_KEY
        self.llm_api_key = os.getenv('GEMINI_API_KEY')
        logger.debug(
            f"GEMINI_API_KEY found: {'Yes' if self.llm_api_key else 'No'}")

        if not self.llm_api_key:
            logger.warning("No GEMINI_API_KEY found in environment")
            logger.debug(f"Current working directory: {os.getcwd()}")
            logger.debug(f"Environment variables: {os.environ.keys()}")

        self.processor = PDFProcessor()
        self._current_file: Optional[BinaryIO] = None
        self._extracted_text: Optional[str] = None
        self._pdf_document: Optional[fitz.Document] = None
        self._total_pages: int = 0

        # Store templates with descriptions
        self.available_templates = prompts.list_templates()
        self.current_template = PromptType.QUICK_REVIEW

    def process_file(
        self,
        file: Union[BinaryIO, Path, str],
        extraction_strategy: str = "pypdf2",
        template_type: PromptType = None,
        research_area: str = None
    ) -> str:
        """
        Process a PDF file and extract its text.

        Args:
            file: The PDF file to process
            extraction_strategy: Strategy to use for text extraction
            template_type: The template type to use for processing
            research_area: The research area to use for processing

        Returns:
            Extracted text from the PDF

        Raises:
            ValidationError: If file validation fails
            PDFAudioError: If processing fails
        """
        try:
            # Load PDF with PyMuPDF for rendering
            if isinstance(file, (str, Path)):
                self._pdf_document = fitz.open(file)
            else:
                # Convert BinaryIO to bytes for PyMuPDF
                file_content = file.read()
                self._pdf_document = fitz.open(
                    stream=file_content, filetype="pdf")

            self._total_pages = len(self._pdf_document)

            logger.info(
                f"Processing PDF with {extraction_strategy} strategy and {template_type} template")

            if extraction_strategy == "llm":
                if not self.llm_api_key:
                    raise ValueError("GEMINI_API_KEY not found in environment")

                # Get template if specified
                if template_type:
                    template = prompts.get_template(template_type)
                    prompt = template.format(
                        content="",  # Content will be added by LLM service
                        research_area=research_area or "general research"
                    )
                else:
                    prompt = None

                self.processor = PDFProcessor(
                    extraction_strategy=extraction_strategy,
                    llm_api_key=self.llm_api_key,
                    prompt_template=prompt
                )
            else:
                self.processor = PDFProcessor(
                    extraction_strategy=extraction_strategy)

            # Process the file
            self._extracted_text = self.processor.load_pdf(file)

            logger.success("PDF processing completed successfully")
            return self._extracted_text

        except Exception as e:
            logger.error(f"PDF processing failed: {str(e)}")
            raise

    def get_extracted_text(self) -> Optional[str]:
        """
        Get the currently extracted text.

        Returns:
            The extracted text or None if no text has been extracted
        """
        return self._extracted_text

    def get_page_image(self, page_number: int, zoom: float = 1.0) -> Tuple[str, Tuple[int, int]]:
        """
        Get a specific page as an image with the specified zoom level.

        Args:
            page_number: The page number (1-indexed)
            zoom: Zoom level (default: 1.0)

        Returns:
            Tuple of (base64 encoded image, (width, height))
        """
        try:
            if not self._pdf_document:
                raise PDFAudioError("No PDF document loaded")

            if page_number < 1 or page_number > self._total_pages:
                raise ValueError(
                    f"Page number {page_number} out of range (1-{self._total_pages})")

            # Get the page (0-indexed internally)
            page = self._pdf_document[page_number - 1]

            # Calculate matrix for zoom
            matrix = fitz.Matrix(zoom, zoom)

            # Render page to image
            pix = page.get_pixmap(matrix=matrix)

            # Convert to PNG data
            img_data = pix.tobytes("png")

            # Convert to base64 for web display
            img_b64 = base64.b64encode(img_data).decode()

            return f"data:image/png;base64,{img_b64}", (pix.width, pix.height)

        except Exception as e:
            logger.error(f"Error rendering PDF page: {str(e)}")
            raise PDFAudioError(f"Failed to render PDF page: {str(e)}")

    def get_total_pages(self) -> int:
        """Get the total number of pages in the loaded PDF."""
        if not self._pdf_document:
            raise PDFAudioError("No PDF document loaded")
        return self._total_pages

    def clear(self) -> None:
        """Clear current processing state."""
        logger.debug("Clearing PDF service state")
        if self._pdf_document:
            self._pdf_document.close()
        self._pdf_document = None
        self._total_pages = 0
        self._current_file = None
        self._extracted_text = None

    def analyze_text(
        self,
        text: str,
        template_type: PromptType,
        research_area: str = None
    ) -> str:
        """Analyze extracted text using selected template."""
        try:
            template = prompts.get_template(template_type)
            # Format the prompt template with the text content
            formatted_prompt = template.format(
                content=text,
                research_area=research_area or "general research"
            )

            # Use LLM service for analysis
            llm_service = create_llm_service(
                "gemini", api_key=self.llm_api_key)
            result = llm_service.process_text(
                text=text,
                prompt_template=formatted_prompt
            )

            return result

        except Exception as e:
            logger.error(f"Text analysis failed: {str(e)}")
            raise
