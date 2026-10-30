"""Tests for AI Chatbot Service, history bounding, provider routing, and failure handling."""

import pytest
from unittest.mock import patch
from services.chat_service import ChatService
from models.conversation import Message
from core.exceptions import ValidationError, AIInferenceError


def test_empty_message_rejected(db_session, farmer_a):
    conv = ChatService.create_conversation(db_session, farmer_a.id, "Test Chat")
    with pytest.raises(ValidationError, match="Message cannot be empty"):
        ChatService.send_message(db_session, farmer_a.id, conv.id, "   ")


def test_chat_success_with_mocked_gemini(db_session, farmer_a):
    conv = ChatService.create_conversation(db_session, farmer_a.id, "Crop Advice")

    with patch("services.chat_service.settings.AI_PROVIDER", "gemini"), \
         patch("services.chat_service.gemini_service.chat_completion") as mock_gemini:
        mock_gemini.return_value = "Use 5 pheromone traps per acre for pink bollworm."

        res = ChatService.send_message(
            db=db_session,
            farmer_id=farmer_a.id,
            conversation_id=conv.id,
            user_text="How to monitor bollworm in cotton?",
            language="en",
        )

        assert "5 pheromone traps" in res["response"]
        assert res["message_id"] is not None
        mock_gemini.assert_called_once()

        # Verify messages persisted in DB
        msgs = db_session.query(Message).filter(Message.conversation_id == conv.id).all()
        assert len(msgs) == 2
        assert msgs[0].role == "user"
        assert msgs[1].role == "assistant"


def test_chat_success_with_mocked_ollama(db_session, farmer_a):
    conv = ChatService.create_conversation(db_session, farmer_a.id, "Ollama Mode Chat")

    with patch("services.chat_service.settings.AI_PROVIDER", "ollama"), \
         patch("services.chat_service.ollama_service.chat_completion") as mock_ollama:
        mock_ollama.return_value = "Organic neem oil spray is effective."

        res = ChatService.send_message(
            db=db_session,
            farmer_id=farmer_a.id,
            conversation_id=conv.id,
            user_text="What organic spray should I use?",
            language="en",
        )

        assert "Organic neem oil" in res["response"]
        mock_ollama.assert_called_once()


def test_gemini_failure_without_fallback(db_session, farmer_a):
    conv = ChatService.create_conversation(db_session, farmer_a.id, "Offline Gemini Chat")

    with patch("services.chat_service.settings.AI_PROVIDER", "gemini"), \
         patch("services.chat_service.settings.ENABLE_OLLAMA_FALLBACK", False), \
         patch("services.chat_service.gemini_service.chat_completion") as mock_gemini, \
         patch("services.chat_service.ollama_service.chat_completion") as mock_ollama:
        mock_gemini.side_effect = AIInferenceError("Quota exceeded or network timeout.")

        res = ChatService.send_message(
            db=db_session,
            farmer_id=farmer_a.id,
            conversation_id=conv.id,
            user_text="What is the weather today?",
        )

        # Assistant response informs user gracefully without silently switching to Ollama
        assert "AI Service Notification" in res["response"]
        assert "Google Gemini" in res["response"]
        mock_ollama.assert_not_called()

        # User question is still safely preserved in DB
        msgs = db_session.query(Message).filter(Message.conversation_id == conv.id).all()
        assert len(msgs) == 2
        assert msgs[0].content == "What is the weather today?"


def test_gemini_failure_with_fallback_enabled(db_session, farmer_a):
    conv = ChatService.create_conversation(db_session, farmer_a.id, "Fallback Chat")

    with patch("services.chat_service.settings.AI_PROVIDER", "gemini"), \
         patch("services.chat_service.settings.ENABLE_OLLAMA_FALLBACK", True), \
         patch("services.chat_service.gemini_service.chat_completion") as mock_gemini, \
         patch("services.chat_service.ollama_service.chat_completion") as mock_ollama:
        mock_gemini.side_effect = AIInferenceError("Gemini unavailable.")
        mock_ollama.return_value = "Response from Ollama fallback."

        res = ChatService.send_message(
            db=db_session,
            farmer_id=farmer_a.id,
            conversation_id=conv.id,
            user_text="Tell me about crop rotation.",
        )

        assert "Response from Ollama fallback" in res["response"]
        mock_ollama.assert_called_once()


def test_conversation_history_bounded(db_session, farmer_a):
    conv = ChatService.create_conversation(db_session, farmer_a.id, "Long History Chat")

    with patch("services.chat_service.settings.AI_PROVIDER", "gemini"), \
         patch("services.chat_service.gemini_service.chat_completion") as mock_gemini:
        mock_gemini.return_value = "Understood."

        # Send 8 messages
        for i in range(8):
            ChatService.send_message(
                db=db_session,
                farmer_id=farmer_a.id,
                conversation_id=conv.id,
                user_text=f"Question number {i+1}",
            )

        # Verify calls passed bounded history
        last_call_messages = mock_gemini.call_args[0][0]
        # System prompt + bounded recent user/assistant turns
        assert len(last_call_messages) <= 8


def test_stream_reply_gemini():
    def dummy_generator(payload):
        yield "Step 1: "
        yield "Prepare soil."

    with patch("services.chat_service.settings.AI_PROVIDER", "gemini"), \
         patch("services.chat_service.gemini_service.stream_chat_completion", side_effect=dummy_generator):
        chunks = list(ChatService.stream_reply([{"role": "user", "content": "How to prepare soil?"}]))
        assert "".join(chunks) == "Step 1: Prepare soil."
