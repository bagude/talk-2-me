"""
Service layer for coordinating PDF processing operations.
Provides a clean API for the UI layer to interact with core functionality.
"""

from pathlib import Path
from typing import BinaryIO, Optional, Union

from loguru import logger

from ..core.exceptions import PDFAudioError, ValidationError
from ..core.pdf_processor import PDFProcessor
from ..core.llm.prompts import prompts
from ..core.llm.prompt_types import PromptType
from ..core.llm.service import create_llm_service


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

    def clear(self) -> None:
        """Clear current processing state."""
        logger.debug("Clearing PDF service state")
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
            prompt = template.format(
                content=text,
                research_area=research_area or "general research"
            )

            # Use LLM service for analysis
            llm_service = create_llm_service(
                "gemini", api_key=self.llm_api_key)
            result = llm_service.process_text(
                text=text,
                prompt_template=prompt
            )

            return result

        except Exception as e:
            logger.error(f"Text analysis failed: {str(e)}")
            raise
