"""
Processing Service module that orchestrates the workflow between PDF processing,
LLM processing, and TTS conversion.
"""

from typing import BinaryIO, Optional

from ..core.error_handler import handle_exceptions
from ..core.exceptions import PDFAudioError
from ..core.pdf_processor import PDFProcessor
from ..core.llm_service import LLMService
from ..core.tts_service import TTSService


class ProcessingService:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.llm_service = LLMService()
        self.tts_service = TTSService()

    @handle_exceptions("Failed to process PDF to audio")
    def process_pdf_to_audio(
        self,
        pdf_file: BinaryIO,
        processing_mode: str,
        voice_id: Optional[str] = None
    ) -> BinaryIO:
        """
        Process a PDF file through the entire pipeline: PDF -> Text -> LLM -> TTS.

        Args:
            pdf_file: Input PDF file
            processing_mode: LLM processing mode
            voice_id: Optional voice ID for TTS

        Returns:
            Generated audio file

        Raises:
            PDFAudioError: If any step in the pipeline fails
        """
        # Extract text from PDF
        text = self.pdf_processor.load_pdf(pdf_file)

        # Process text with LLM
        processed_text = self.llm_service.process_text(text, processing_mode)

        # Convert to audio
        audio = self.tts_service.text_to_speech(processed_text, voice_id)

        return audio
