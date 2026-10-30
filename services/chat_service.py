"""Chat service orchestrating conversation history, RAG, and AI inference (Gemini & Ollama)."""

from typing import List, Dict, Any, Optional, Generator
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.conversation import Conversation, Message
from models.crop import Crop
from services.ollama_service import ollama_service
from services.gemini_service import gemini_service
from services.knowledge_service import KnowledgeService
from utils.prompts import build_system_prompt
from core.exceptions import NotFoundError, AIInferenceError, ValidationError, ConfigurationError
from core.auth import verify_farmer_ownership
from config import settings
from utils.logging_config import logger


class ChatService:

    @staticmethod
    def create_conversation(
        db: Session,
        farmer_id: str,
        title: str = "New Farming Query",
        preferred_language: str = "en",
    ) -> Conversation:
        """Create a new chat conversation for the authenticated farmer."""
        conv = Conversation(
            farmer_id=farmer_id,
            title=title.strip()[:200],
            preferred_language=preferred_language,
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return conv

    @staticmethod
    def get_conversation(db: Session, farmer_id: str, conversation_id: str) -> Conversation:
        """Get a conversation with farmer ownership check."""
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conv:
            raise NotFoundError(f"Conversation {conversation_id} not found.")
        verify_farmer_ownership(farmer_id, conv.farmer_id, resource_name="Conversation")
        return conv

    @staticmethod
    def list_conversations(db: Session, farmer_id: str, limit: int = 20) -> List[Conversation]:
        """List all conversations owned by the authenticated farmer."""
        return (
            db.query(Conversation)
            .filter(Conversation.farmer_id == farmer_id)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
            .all()
        )

    @staticmethod
    def delete_conversation(db: Session, farmer_id: str, conversation_id: str) -> bool:
        """Delete a conversation with ownership check."""
        conv = ChatService.get_conversation(db, farmer_id, conversation_id)
        db.delete(conv)
        db.commit()
        return True

    @staticmethod
    def prepare_chat_context(
        db: Session,
        farmer_id: str,
        conversation_id: str,
        user_text: str,
        crop_id: Optional[str] = None,
        language: str = "en",
    ) -> Dict[str, Any]:
        """Prepare grounded conversation context, persist user message, and build LLM payload."""
        cleaned_text = (user_text or "").strip()
        if not cleaned_text:
            raise ValidationError("Message cannot be empty.")

        conv = ChatService.get_conversation(db, farmer_id, conversation_id)

        # 1. Fetch authorized crop context if specified
        crop_context = None
        crop_name = None
        if crop_id:
            crop = db.query(Crop).filter(Crop.id == crop_id).first()
            if crop:
                verify_farmer_ownership(farmer_id, crop.farmer_id, resource_name="Crop")
                crop_context = {
                    "name": crop.name,
                    "variety": crop.variety,
                    "area": crop.area,
                    "area_unit": crop.area_unit,
                    "sowing_date": str(crop.sowing_date),
                    "growth_stage": crop.growth_stage,
                    "soil_type": crop.soil_type,
                    "irrigation_method": crop.irrigation_method,
                }
                crop_name = crop.name

        # 2. Retrieve verified knowledge passages via lightweight TF-IDF RAG
        search_query = f"{crop_name or ''} {cleaned_text}"
        retrieved_docs = KnowledgeService.retrieve_relevant_documents(
            db=db,
            query=search_query,
            top_k=2,
        )
        compact_docs = []
        for d in retrieved_docs:
            d_copy = dict(d)
            if len(d_copy.get("content", "")) > 400:
                d_copy["content"] = d_copy["content"][:400] + "..."
            compact_docs.append(d_copy)

        # 3. Construct system prompt
        effective_lang = language or conv.preferred_language or "en"
        system_content = build_system_prompt(
            language=effective_lang,
            crop_context=crop_context,
            retrieved_documents=compact_docs,
        )

        # 4. Load recent message history (bounded context for current conversation only)
        max_history = settings.MAX_CHAT_HISTORY
        recent_messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(max_history)
            .all()
        )
        recent_messages.reverse()

        # Build prompt payload
        messages_payload: List[Dict[str, str]] = [{"role": "system", "content": system_content}]
        for m in recent_messages:
            messages_payload.append({"role": m.role, "content": m.content})
        messages_payload.append({"role": "user", "content": cleaned_text})

        # 5. Persist the user's message
        user_msg = Message(
            conversation_id=conversation_id,
            farmer_id=farmer_id,
            role="user",
            content=cleaned_text,
        )
        db.add(user_msg)

        # Update conversation title if this is the first message
        if len(recent_messages) == 0:
            title_candidate = cleaned_text[:40].replace("\n", " ").strip()
            if len(cleaned_text) > 40:
                title_candidate += "..."
            conv.title = title_candidate

        db.commit()

        return {
            "messages_payload": messages_payload,
            "retrieved_docs": retrieved_docs,
            "crop_name": crop_name,
            "effective_lang": effective_lang,
            "conversation": conv,
        }

    @staticmethod
    def generate_reply(messages_payload: List[Dict[str, str]]) -> str:
        """Call AI provider (Gemini primary, Ollama optional fallback)."""
        provider = (settings.AI_PROVIDER or "gemini").strip().lower()

        if provider == "gemini":
            try:
                return gemini_service.chat_completion(messages_payload)
            except (AIInferenceError, ConfigurationError) as e:
                logger.warning(f"Primary Gemini AI failed: {e}")
                if settings.ENABLE_OLLAMA_FALLBACK:
                    logger.info("Attempting optional Ollama fallback...")
                    try:
                        return ollama_service.chat_completion(messages_payload)
                    except Exception as ollama_err:
                        logger.error(f"Ollama fallback also failed: {ollama_err}")
                        return (
                            f"⚠️ **AI Service Notification**: Google Gemini AI failed ({str(e)}), "
                            f"and Ollama fallback also failed ({str(ollama_err)}).\n\n"
                            "Your question has been saved and your other farm records are fully accessible."
                        )
                # Fallback disabled - do not silently switch to slow Ollama
                return (
                    f"⚠️ **AI Service Notification**: Google Gemini AI assistant is currently unavailable ({str(e)}).\n\n"
                    "Please check your `GEMINI_API_KEY` configuration or network connection. "
                    "Your question has been saved and your other farm records are fully accessible."
                )

        # Provider is Ollama
        try:
            return ollama_service.chat_completion(messages_payload)
        except AIInferenceError as e:
            logger.warning(f"Ollama inference failure: {str(e)}")
            return (
                f"⚠️ **AI Service Notification**: Local AI assistant is currently unavailable ({str(e)}).\n\n"
                "Please ensure Ollama is running locally with the command `ollama serve`.\n"
                "Your question has been saved and your other farm records are fully accessible."
            )

    @staticmethod
    def stream_reply(messages_payload: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Stream AI reply chunks from Gemini, with graceful fallback or error handling."""
        provider = (settings.AI_PROVIDER or "gemini").strip().lower()

        if provider == "gemini":
            try:
                for chunk in gemini_service.stream_chat_completion(messages_payload):
                    yield chunk
                return
            except (AIInferenceError, ConfigurationError) as e:
                logger.warning(f"Primary Gemini stream failed: {e}")
                if settings.ENABLE_OLLAMA_FALLBACK:
                    logger.info("Attempting Ollama fallback for stream request...")
                    try:
                        reply = ollama_service.chat_completion(messages_payload)
                        yield reply
                        return
                    except Exception as ollama_err:
                        yield (
                            f"⚠️ **AI Service Notification**: Google Gemini stream failed ({str(e)}), "
                            f"and Ollama fallback also failed ({str(ollama_err)})."
                        )
                        return
                yield (
                    f"⚠️ **AI Service Notification**: Google Gemini AI assistant is currently unavailable ({str(e)}).\n\n"
                    "Please check your `GEMINI_API_KEY` configuration or network connection. "
                    "Your question has been saved and your other farm records are fully accessible."
                )
                return

        # Provider is Ollama
        try:
            reply = ollama_service.chat_completion(messages_payload)
            yield reply
        except AIInferenceError as e:
            yield (
                f"⚠️ **AI Service Notification**: Local AI assistant is currently unavailable ({str(e)}).\n\n"
                "Please ensure Ollama is running locally with the command `ollama serve`.\n"
                "Your question has been saved and your other farm records are fully accessible."
            )

    @staticmethod
    def save_assistant_message(
        db: Session,
        farmer_id: str,
        conversation_id: str,
        content: str,
    ) -> Message:
        """Persist assistant reply in the database."""
        assistant_msg = Message(
            conversation_id=conversation_id,
            farmer_id=farmer_id,
            role="assistant",
            content=content,
        )
        db.add(assistant_msg)
        db.commit()
        db.refresh(assistant_msg)
        return assistant_msg

    @staticmethod
    def send_message(
        db: Session,
        farmer_id: str,
        conversation_id: str,
        user_text: str,
        crop_id: Optional[str] = None,
        language: str = "en",
    ) -> Dict[str, Any]:
        """Process user message synchronously, ground with RAG and authorized crop context, and call LLM."""
        context = ChatService.prepare_chat_context(
            db=db,
            farmer_id=farmer_id,
            conversation_id=conversation_id,
            user_text=user_text,
            crop_id=crop_id,
            language=language,
        )

        assistant_reply = ChatService.generate_reply(context["messages_payload"])
        assistant_msg = ChatService.save_assistant_message(
            db=db,
            farmer_id=farmer_id,
            conversation_id=conversation_id,
            content=assistant_reply,
        )

        return {
            "response": assistant_reply,
            "sources": context["retrieved_docs"],
            "crop_context_used": context["crop_name"],
            "message_id": assistant_msg.id,
        }
