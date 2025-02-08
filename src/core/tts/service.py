"""
Core TTS service providing text-to-speech capabilities.
Supports multiple providers with factory pattern.
"""

from abc import ABC, abstractmethod
from typing import Any, BinaryIO, Dict, Optional
from pathlib import Path
import uuid
import json
import base64

from loguru import logger


class TTSError(Exception):
    """Base exception for TTS-related errors."""
    pass


class TTSAPIError(TTSError):
    """Exception raised when TTS API calls fail."""
    pass


class TTSService(ABC):
    """Abstract base class for TTS services."""

    @abstractmethod
    def text_to_speech(
        self,
        text: str,
        voice_id: str,
        output_format: str = "mp3_44100_128"
    ) -> BinaryIO:
        """Convert text to speech."""
        pass

    @abstractmethod
    def text_to_speech_with_timestamps(
        self,
        text: str,
        voice_id: str,
        output_format: str = "mp3_44100_128"
    ) -> tuple[BinaryIO, Dict[str, Any]]:
        """Convert text to speech and return timestamps."""
        pass


class ElevenLabsService(TTSService):
    """ElevenLabs implementation of TTS service."""

    ELEVENLABS_API = "https://api.elevenlabs.io/v1"

    def __init__(self, api_key: str):
        """Initialize ElevenLabs service with API key."""
        import requests  # Import here to keep it optional

        logger.debug("Initializing ElevenLabs service")
        self.api_key = api_key
        self._session = requests.Session()
        self._session.headers.update({
            "xi-api-key": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

    def text_to_speech(
        self,
        text: str,
        voice_id: str,
        output_format: str = "mp3_44100_128"
    ) -> BinaryIO:
        """Convert text to speech using ElevenLabs API."""
        try:
            logger.info(f"Converting text to speech with voice {voice_id}")
            logger.debug(f"Text length: {len(text)} characters")

            url = f"{self.ELEVENLABS_API}/text-to-speech/{voice_id}/stream"
            payload = {
                "text": text,
                "model_id": "eleven_turbo_v2_5",
                "output_format": output_format
            }

            logger.debug(f"Making API request to {url}")
            response = self._session.post(url, json=payload, stream=True)
            response.raise_for_status()
            logger.debug(f"API response status: {response.status_code}")

            # Create a temporary file to store the audio
            temp_file = Path(f"temp_{uuid.uuid4()}.mp3")
            logger.debug(f"Creating temporary file: {temp_file}")

            bytes_written = 0
            with open(temp_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        bytes_written += len(chunk)
                        f.write(chunk)

            logger.info(
                f"Successfully wrote {bytes_written} bytes to {temp_file}")
            return open(temp_file, "rb")

        except Exception as e:
            logger.error(f"ElevenLabs API call failed: {str(e)}")
            logger.exception("Full traceback:")
            raise TTSAPIError(f"Failed to convert text to speech: {str(e)}")

    def text_to_speech_with_timestamps(
        self,
        text: str,
        voice_id: str,
        output_format: str = "mp3_44100_128"
    ) -> tuple[BinaryIO, Dict[str, Any]]:
        """Convert text to speech and return timestamps."""
        try:
            url = f"{self.ELEVENLABS_API}/text-to-speech/{voice_id}/stream/with-timestamps"
            payload = {
                "text": text,
                "model_id": "eleven_turbo_v2_5",
                "output_format": output_format
            }

            response = self._session.post(url, json=payload, stream=True)
            response.raise_for_status()

            # Create temporary files for audio and timestamps
            temp_audio = Path(f"temp_{uuid.uuid4()}.mp3")
            timestamps = []

            with open(temp_audio, "wb") as f:
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        if "audio_base64" in chunk:
                            audio_bytes = base64.b64decode(
                                chunk["audio_base64"])
                            f.write(audio_bytes)
                        if "alignment" in chunk and chunk["alignment"]:
                            timestamps.extend(chunk["alignment"])

            return open(temp_audio, "rb"), {"timestamps": timestamps}

        except Exception as e:
            logger.error(f"ElevenLabs API call failed: {str(e)}")
            raise TTSAPIError(f"Failed to convert text to speech: {str(e)}")


def create_tts_service(provider: str = "elevenlabs", **kwargs: Any) -> TTSService:
    """Factory function to create TTS services."""
    providers = {
        "elevenlabs": ElevenLabsService,
    }

    try:
        service_class = providers[provider.lower()]
        logger.info(f"Creating TTS service with provider: {provider}")
        return service_class(**kwargs)
    except KeyError:
        raise ValueError(f"Unsupported TTS provider: {provider}")
