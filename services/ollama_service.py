"""Ollama AI integration service for local inference with Qwen 2.5 3B."""

import json
from typing import List, Dict, Any, Optional
import requests
from config import settings
from core.exceptions import AIInferenceError
from utils.logging_config import logger


class OllamaService:
    """Handles communication with the local Ollama instance."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout or settings.OLLAMA_TIMEOUT_SECONDS

    def check_health(self) -> Dict[str, Any]:
        """Check Ollama service status and verify if the required model is installed."""
        url = f"{self.base_url}/api/tags"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name") for m in data.get("models", [])]
                # Check exact or prefix match (e.g. qwen2.5:3b or qwen2.5:3b-latest)
                has_model = any(
                    self.model in m or m.startswith(self.model)
                    for m in models
                )
                return {
                    "online": True,
                    "available_models": models,
                    "has_target_model": has_model,
                    "target_model": self.model,
                    "message": "Ollama service is reachable." if has_model else f"Model '{self.model}' not found in installed models.",
                }
            return {
                "online": False,
                "available_models": [],
                "has_target_model": False,
                "target_model": self.model,
                "message": f"Ollama returned HTTP {resp.status_code}",
            }
        except requests.exceptions.RequestException as e:
            return {
                "online": False,
                "available_models": [],
                "has_target_model": False,
                "target_model": self.model,
                "message": f"Cannot connect to Ollama at {self.base_url}: {str(e)}",
            }

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
    ) -> str:
        """Send chat messages to Ollama /api/chat endpoint."""
        url = f"{self.base_url}/api/chat"
        temp = temperature if temperature is not None else settings.OLLAMA_TEMPERATURE

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temp,
                "num_ctx": settings.OLLAMA_NUM_CTX,
                "num_predict": settings.OLLAMA_NUM_PREDICT,
                "top_k": settings.OLLAMA_TOP_K,
                "top_p": settings.OLLAMA_TOP_P,
            },
        }

        try:
            logger.info(f"Calling Ollama chat with {len(messages)} messages (model={self.model})")
            resp = requests.post(url, json=payload, timeout=self.timeout)

            if resp.status_code != 200:
                error_msg = f"Ollama API returned HTTP {resp.status_code}: {resp.text}"
                logger.error(error_msg)
                raise AIInferenceError(error_msg)

            data = resp.json()
            message_obj = data.get("message", {})
            content = message_obj.get("content", "").strip()

            if not content:
                raise AIInferenceError("Ollama returned an empty response.")

            return content

        except requests.exceptions.Timeout:
            err = f"Ollama request timed out after {self.timeout} seconds. The local CPU may be heavily loaded."
            logger.error(err)
            raise AIInferenceError(err)
        except requests.exceptions.ConnectionError:
            err = f"Could not connect to Ollama at {self.base_url}. Please ensure 'ollama serve' is running."
            logger.error(err)
            raise AIInferenceError(err)
        except requests.exceptions.RequestException as e:
            err = f"Ollama HTTP communication failure: {str(e)}"
            logger.error(err)
            raise AIInferenceError(err)
        except json.JSONDecodeError:
            err = "Failed to parse Ollama response as valid JSON."
            logger.error(err)
            raise AIInferenceError(err)


# Singleton service instance
ollama_service = OllamaService()
