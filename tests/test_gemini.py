"""Tests for Google Gemini Service (mocked responses, error handling, streaming)."""

import pytest
from unittest.mock import MagicMock, patch
from google.genai import errors
from services.gemini_service import GeminiService
from core.exceptions import ConfigurationError, AIInferenceError


@pytest.fixture
def gemini_svc():
    return GeminiService()


def test_gemini_missing_api_key(gemini_svc):
    with patch("services.gemini_service.settings.GEMINI_API_KEY", None), \
         patch.dict("os.environ", {"GEMINI_API_KEY": ""}):
        with pytest.raises(ConfigurationError, match="Gemini API key is not configured"):
            gemini_svc.chat_completion([{"role": "user", "content": "Hello"}])


def test_gemini_health_check_unconfigured(gemini_svc):
    with patch("services.gemini_service.settings.GEMINI_API_KEY", None), \
         patch.dict("os.environ", {"GEMINI_API_KEY": ""}):
        health = gemini_svc.check_health()
        assert health["configured"] is False
        assert health["online"] is False
        assert "not configured" in health["error"]


def test_gemini_health_check_configured_and_healthy(gemini_svc):
    with patch("services.gemini_service.settings.GEMINI_API_KEY", "dummy_key"):
        health = gemini_svc.check_health()
        assert health["configured"] is True
        assert health["online"] is True
        assert health["model"] == gemini_svc.model


def test_gemini_chat_completion_success(gemini_svc):
    messages = [
        {"role": "system", "content": "You are AgriSaathi AI."},
        {"role": "user", "content": "कपाशीतील बोंडअळी कशी रोखावी?"},
    ]

    with patch("services.gemini_service.settings.GEMINI_API_KEY", "dummy_key"):
        with patch.object(gemini_svc, "get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_resp = MagicMock()
            mock_resp.text = "फेरोमोन ट्रॅप लावा आणि निंबोळी अर्काची फवारणी करा."
            mock_client.models.generate_content.return_value = mock_resp
            mock_get_client.return_value = mock_client

            reply = gemini_svc.chat_completion(messages)

            assert "फेरोमोन ट्रॅप" in reply
            mock_client.models.generate_content.assert_called_once()
            call_kwargs = mock_client.models.generate_content.call_args[1]
            assert call_kwargs["config"].system_instruction == "You are AgriSaathi AI."


def test_gemini_stream_chat_completion_success(gemini_svc):
    messages = [{"role": "user", "content": "How to treat wheat rust?"}]

    chunk1 = MagicMock()
    chunk1.text = "Apply "
    chunk2 = MagicMock()
    chunk2.text = "Propiconazole "
    chunk3 = MagicMock()
    chunk3.text = "recommended dose."

    with patch("services.gemini_service.settings.GEMINI_API_KEY", "dummy_key"):
        with patch.object(gemini_svc, "get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.models.generate_content_stream.return_value = [chunk1, chunk2, chunk3]
            mock_get_client.return_value = mock_client

            chunks = list(gemini_svc.stream_chat_completion(messages))
            assert "".join(chunks) == "Apply Propiconazole recommended dose."


def test_gemini_auth_error_handling(gemini_svc):
    with patch("services.gemini_service.settings.GEMINI_API_KEY", "bad_key"):
        with patch.object(gemini_svc, "get_client") as mock_get_client:
            mock_client = MagicMock()
            api_err = errors.APIError(401, {"error": {"message": "Invalid API key"}})
            mock_client.models.generate_content.side_effect = api_err
            mock_get_client.return_value = mock_client

            with pytest.raises(AIInferenceError, match="authentication failed"):
                gemini_svc.chat_completion([{"role": "user", "content": "test"}])


def test_gemini_quota_error_handling(gemini_svc):
    with patch("services.gemini_service.settings.GEMINI_API_KEY", "dummy_key"):
        with patch.object(gemini_svc, "get_client") as mock_get_client:
            mock_client = MagicMock()
            api_err = errors.APIError(429, {"error": {"message": "Quota exceeded"}})
            mock_client.models.generate_content.side_effect = api_err
            mock_get_client.return_value = mock_client

            with pytest.raises(AIInferenceError, match="rate limit or quota exceeded"):
                gemini_svc.chat_completion([{"role": "user", "content": "test"}])


def test_gemini_timeout_handling(gemini_svc):
    with patch("services.gemini_service.settings.GEMINI_API_KEY", "dummy_key"):
        with patch.object(gemini_svc, "get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.models.generate_content.side_effect = TimeoutError("Timed out")
            mock_get_client.return_value = mock_client

            with pytest.raises(AIInferenceError, match="timed out"):
                gemini_svc.chat_completion([{"role": "user", "content": "test"}])


def test_gemini_empty_response_handling(gemini_svc):
    with patch("services.gemini_service.settings.GEMINI_API_KEY", "dummy_key"):
        with patch.object(gemini_svc, "get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_resp = MagicMock()
            mock_resp.text = None
            mock_client.models.generate_content.return_value = mock_resp
            mock_get_client.return_value = mock_client

            with pytest.raises(AIInferenceError, match="empty response"):
                gemini_svc.chat_completion([{"role": "user", "content": "test"}])


def test_build_contents_mapping(gemini_svc):
    messages = [
        {"role": "system", "content": "System prompt text"},
        {"role": "user", "content": "First question"},
        {"role": "assistant", "content": "First answer"},
        {"role": "user", "content": "Second question"},
    ]
    contents = gemini_svc._build_contents(messages)
    assert len(contents) == 3
    assert contents[0].role == "user"
    assert contents[1].role == "model"
    assert contents[2].role == "user"
