"""Google Gemini AI integration service using the official google-genai SDK."""

import os
from typing import List, Dict, Any, Optional, Iterator
from config import settings
from core.exceptions import AIInferenceError, ConfigurationError
from utils.logging_config import logger

try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    HAS_GENAI_SDK = True
except ImportError:
    HAS_GENAI_SDK = False
    genai = None
    types = None
    APIError = Exception


class GeminiService:
    """Handles communication with the Google Gemini API using google-genai SDK."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_output_tokens: Optional[int] = None,
    ):
        self._api_key = api_key
        self.model = model or settings.GEMINI_MODEL
        self.timeout = timeout or settings.GEMINI_TIMEOUT_SECONDS
        self.max_output_tokens = max_output_tokens or settings.GEMINI_MAX_OUTPUT_TOKENS

    @property
    def api_key(self) -> str:
        """Resolve API key dynamically from instance, settings, or environment."""
        key = self._api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        return key.strip()

    def get_client(self):
        """Instantiate and return google-genai Client."""
        if not HAS_GENAI_SDK:
            raise AIInferenceError(
                "The 'google-genai' SDK is not installed. Please install it using: pip install google-genai"
            )

        key = self.api_key
        if not key or key == "your_gemini_api_key_here":
            raise ConfigurationError(
                "Google Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file or environment."
            )

        return genai.Client(api_key=key)

    def check_health(self) -> Dict[str, Any]:
        """Check Gemini provider status and configuration."""
        key = self.api_key
        configured = bool(key and key != "your_gemini_api_key_here")

        if not HAS_GENAI_SDK:
            return {
                "online": False,
                "configured": False,
                "provider": "gemini",
                "model": self.model,
                "message": "google-genai SDK not installed.",
                "error": "google-genai SDK not installed.",
            }

        if not configured:
            return {
                "online": False,
                "configured": False,
                "provider": "gemini",
                "model": self.model,
                "message": "GEMINI_API_KEY is not configured.",
                "error": "GEMINI_API_KEY is not configured.",
            }

        return {
            "online": True,
            "configured": True,
            "provider": "gemini",
            "model": self.model,
            "message": f"Gemini API configured (model: {self.model}).",
        }

    def _build_contents(self, messages_payload: List[Dict[str, str]]) -> List[Any]:
        """Convert standard chat messages to google-genai Content objects."""
        contents = []
        for m in messages_payload:
            role = m.get("role", "user")
            # Skip system messages in conversation turns; system goes into GenerateContentConfig
            if role == "system":
                continue

            content_role = "model" if role == "assistant" else "user"
            text_part = types.Part.from_text(text=m.get("content", ""))
            contents.append(types.Content(role=content_role, parts=[text_part]))

        return contents

    def chat_completion(
        self,
        messages_payload: List[Dict[str, str]],
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Generate a complete text response via Google Gemini API."""
        client = self.get_client()
        temp = temperature if temperature is not None else settings.GEMINI_TEMPERATURE
        contents = self._build_contents(messages_payload)

        # Extract system prompt from messages if not passed separately
        sys_prompt = system_instruction
        if not sys_prompt:
            for m in messages_payload:
                if m.get("role") == "system":
                    sys_prompt = m.get("content")
                    break

        config = types.GenerateContentConfig(
            system_instruction=sys_prompt,
            temperature=temp,
            max_output_tokens=self.max_output_tokens,
        )

        try:
            logger.info(f"Calling Google Gemini API ({self.model}) with {len(contents)} content turns.")
            response = client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )

            text = response.text or ""
            text = text.strip()
            if not text:
                raise AIInferenceError("Google Gemini returned an empty response.")

            return text

        except APIError as e:
            logger.error(f"Gemini APIError [code {e.code}]: {e.message}")
            if e.code in (400, 401, 403):
                raise AIInferenceError(
                    "Google Gemini API authentication failed. Please verify your GEMINI_API_KEY."
                ) from e
            elif e.code == 404:
                raise AIInferenceError(
                    f"Google Gemini model '{self.model}' is not available or unrecognized. "
                    "Please check GEMINI_MODEL in configuration."
                ) from e
            elif e.code == 429:
                raise AIInferenceError(
                    "Google Gemini API rate limit or quota exceeded. Please wait a moment and try again."
                ) from e
            elif e.code in (500, 503):
                raise AIInferenceError(
                    "Google Gemini API service is temporarily experiencing high demand. Please try again shortly."
                ) from e
            else:
                raise AIInferenceError(f"Google Gemini API error ({e.code}): {e.message}") from e

        except Exception as e:
            if isinstance(e, AIInferenceError):
                raise
            err_str = str(e)
            logger.error(f"Gemini communication failure: {err_str}")
            if "timeout" in err_str.lower() or "timed out" in err_str.lower():
                raise AIInferenceError(
                    f"Google Gemini request timed out after {self.timeout}s. Please check your network connection."
                ) from e
            raise AIInferenceError(f"Failed to communicate with Google Gemini API: {err_str}") from e

    def stream_chat_completion(
        self,
        messages_payload: List[Dict[str, str]],
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> Iterator[str]:
        """Stream response chunks via Google Gemini API."""
        client = self.get_client()
        temp = temperature if temperature is not None else settings.GEMINI_TEMPERATURE
        contents = self._build_contents(messages_payload)

        sys_prompt = system_instruction
        if not sys_prompt:
            for m in messages_payload:
                if m.get("role") == "system":
                    sys_prompt = m.get("content")
                    break

        config = types.GenerateContentConfig(
            system_instruction=sys_prompt,
            temperature=temp,
            max_output_tokens=self.max_output_tokens,
        )

        try:
            logger.info(f"Initiating Google Gemini stream ({self.model})...")
            stream_response = client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=config,
            )

            for chunk in stream_response:
                if chunk.text:
                    yield chunk.text

        except APIError as e:
            logger.error(f"Gemini Stream APIError [code {e.code}]: {e.message}")
            if e.code in (400, 401, 403):
                raise AIInferenceError(
                    "Google Gemini API authentication failed. Please verify your GEMINI_API_KEY."
                ) from e
            elif e.code == 429:
                raise AIInferenceError(
                    "Google Gemini API rate limit or quota exceeded. Please wait a moment and try again."
                ) from e
            else:
                raise AIInferenceError(f"Google Gemini stream error ({e.code}): {e.message}") from e

        except Exception as e:
            if isinstance(e, AIInferenceError):
                raise
            logger.error(f"Gemini streaming failure: {str(e)}")
            raise AIInferenceError(f"Google Gemini streaming error: {str(e)}") from e


# Singleton service instance
gemini_service = GeminiService()

