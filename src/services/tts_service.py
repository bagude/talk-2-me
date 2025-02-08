"""
Service layer for coordinating text-to-speech operations.
Provides a clean API for the UI layer to interact with TTS functionality.
"""

from pathlib import Path
from typing import BinaryIO, Dict, Optional, Union
import os

from loguru import logger

from ..core.tts.service import create_tts_service, TTSError, TTSAPIError


class TTSService:
    """Service for handling text-to-speech operations."""

    def __init__(self):
        """Initialize TTS service."""
        logger.debug("Initializing TTS Service")

        # Load environment variables
        from dotenv import load_dotenv
        root_dir = Path(__file__).parent.parent.parent
        env_path = root_dir / '.env'

        logger.debug(f"Looking for .env file at: {env_path}")
        load_dotenv(env_path)

        self.tts_api_key = os.getenv('ELEVENLABS_API_KEY')
        logger.debug(
            f"ELEVENLABS_API_KEY found: {'Yes' if self.tts_api_key else 'No'}")

        if not self.tts_api_key:
            logger.warning("No ELEVENLABS_API_KEY found in environment")
            logger.debug(f"Current working directory: {os.getcwd()}")
            logger.debug(f"Environment variables: {os.environ.keys()}")

        # Initialize state
        self._current_audio: Optional[BinaryIO] = None
        self._current_timestamps: Optional[Dict] = None
        self._default_voice_id = "YFpUSo240svj7tcmDapZ"  # Default voice

    def text_to_audio(
        self,
        text: str,
        voice_id: Optional[str] = None,
        with_timestamps: bool = False
    ) -> Union[tuple[bytes, Dict], bytes]:
        """
        Convert text to audio using TTS service.

        Args:
            text: Text to convert to speech
            voice_id: Optional voice ID to use
            with_timestamps: Whether to return timestamps

        Returns:
            Audio bytes or tuple of audio bytes and timestamps

        Raises:
            TTSError: If TTS processing fails
        """
        try:
            logger.info("Starting text to audio conversion")
            logger.debug(
                f"Text length: {len(text)}, With timestamps: {with_timestamps}")

            # Create TTS service
            tts_service = create_tts_service(
                provider="elevenlabs",
                api_key=self.tts_api_key
            )

            # Use default voice if none specified
            voice_id = voice_id or self._default_voice_id
            logger.debug(f"Using voice ID: {voice_id}")

            if with_timestamps:
                logger.info("Converting text with timestamps")
                audio_file, timestamps = tts_service.text_to_speech_with_timestamps(
                    text=text,
                    voice_id=voice_id
                )

                # Read the audio data and close the file
                logger.debug("Reading audio data from file")
                audio_data = audio_file.read()
                audio_file.close()

                logger.info(
                    f"Successfully generated audio ({len(audio_data)} bytes) with timestamps")
                return audio_data, timestamps
            else:
                logger.info("Converting text without timestamps")
                audio_file = tts_service.text_to_speech(
                    text=text,
                    voice_id=voice_id
                )

                # Read the audio data and close the file
                logger.debug("Reading audio data from file")
                audio_data = audio_file.read()
                audio_file.close()

                logger.info(
                    f"Successfully generated audio ({len(audio_data)} bytes)")
                return audio_data

        except Exception as e:
            logger.error(f"TTS processing failed: {str(e)}")
            logger.exception("Full traceback:")
            raise TTSError(f"Failed to convert text to audio: {str(e)}")

    def get_current_audio(self) -> Optional[BinaryIO]:
        """Get the currently generated audio."""
        return self._current_audio

    def get_current_timestamps(self) -> Optional[Dict]:
        """Get the current timestamps if available."""
        return self._current_timestamps

    def clear(self) -> None:
        """Clear current processing state."""
        logger.debug("Clearing TTS service state")
        if self._current_audio:
            self._current_audio.close()
        self._current_audio = None
        self._current_timestamps = None
