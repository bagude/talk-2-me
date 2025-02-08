"""
Core LLM service providing text processing capabilities.
Can be used for both PDF extraction and text transformation.
"""

from abc import ABC, abstractmethod
from typing import Any, BinaryIO, Dict, List, Optional
from pathlib import Path
import io

from loguru import logger
from .prompts import prompts, PromptType


class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass


class LLMAPIError(LLMError):
    """Exception raised when LLM API calls fail."""
    pass


class LLMService(ABC):
    """Abstract base class for LLM services."""

    @abstractmethod
    def process_text(
        self,
        text: str,
        prompt_template: str,
        **kwargs: Any
    ) -> str:
        """Process text using the LLM."""
        pass

    @abstractmethod
    def process_pdf(
        self,
        file: BinaryIO,
        prompt_template: str,
        **kwargs: Any
    ) -> str:
        """Process PDF directly using the LLM."""
        pass


class GeminiService(LLMService):
    """Google's Gemini implementation of LLM service."""

    GENAI_IMPORT = 'google.generativeai'

    def __init__(self, api_key: str):
        """Initialize Gemini service with API key."""
        from google import generativeai as genai

        logger.debug("Initializing Gemini service")
        # Configure API key first
        genai.configure(api_key=api_key)

        # Then create the model
        self._client = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config={
                "temperature": 0.4,
                "top_p": 1,
                "top_k": 32,
                "max_output_tokens": 2048,
            }
        )

    def process_text(
        self,
        text: str,
        prompt_template: str,
        **kwargs: Any
    ) -> str:
        """Process text using Gemini."""
        try:
            prompt = prompt_template.format(text=text, **kwargs)
            logger.debug(f"Sending prompt to Gemini: {prompt[:100]}...")

            response = self._client.generate_content(prompt)

            if not response.text:
                raise LLMError("Empty response from Gemini")

            return response.text

        except Exception as e:
            logger.error(f"Gemini processing failed: {str(e)}")
            raise LLMAPIError(f"Failed to process text: {str(e)}")

    def process_pdf(
        self,
        file: BinaryIO,
        prompt_template: str = None,
        **kwargs: Any
    ) -> str:
        """Process PDF directly using Gemini's native PDF support."""
        try:
            # Get PDF data
            pdf_data = file.read()

            # Get template (use TEXT_EXTRACTION if none specified)
            if not prompt_template:
                template = prompts.get_template(PromptType.TEXT_EXTRACTION)
                # PDF will be added as separate part
                prompt = template.format(content="")
            else:
                prompt = prompt_template

            logger.debug(f"Processing PDF with prompt: {prompt[:100]}...")

            # Create content parts
            response = self._client.generate_content([
                {"mime_type": "application/pdf", "data": pdf_data},
                prompt
            ])

            if not response.text:
                raise LLMError("Empty response from Gemini")

            return response.text

        except Exception as e:
            logger.error(f"Gemini PDF processing failed: {str(e)}")
            raise LLMAPIError(f"Failed to process PDF: {str(e)}")


def create_llm_service(provider: str = "gemini", **kwargs: Any) -> LLMService:
    """Factory function to create LLM services."""
    providers = {
        "gemini": GeminiService,
    }

    try:
        service_class = providers[provider.lower()]
        logger.info(f"Creating LLM service with provider: {provider}")
        return service_class(**kwargs)
    except KeyError:
        raise ValueError(f"Unsupported LLM provider: {provider}")
