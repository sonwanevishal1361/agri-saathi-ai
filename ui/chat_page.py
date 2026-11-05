"""Interactive, Accessible AI Farming Chatbot interface for Indian Farmers.

Styled with refined message bubbles, vector agricultural avatars,
Web Speech API voice mic and speaker output, and instant quick-question chips.
"""

import textwrap
import streamlit as st
from config import settings
from core.database import get_db
from core.auth import AuthenticatedFarmer
from services.chat_service import ChatService
from services.crop_service import CropService
from services.ollama_service import ollama_service
from services.gemini_service import gemini_service
from models.conversation import Message
from ui.state import get_language
from utils.language import t
from ui.components.voice_button import render_voice_mic_button
from ui.components.chat_bubble import render_chat_bubble
from ui.components.icons import get_icon


SAMPLE_QUESTIONS_MAP = {
    "mr": [
        "🐛 कपाशीतील बोंडअळी नियंत्रणासाठी काय करावे?",
        "🧅 आजचे कांद्याचे बाजारभाव काय आहेत?",
        "🌦️ या आठवड्यात पाऊस कसा राहील?",
        "🌿 सोयाबीन पिवळा मोझॅक रोगावर काय उपाय आहेत?",
    ],
    "hi": [
        "🐛 कपास में गुलाबी सुंडी का नियंत्रण कैसे करें?",
        "🧅 आज प्याज का ताजा मंडी भाव क्या है?",
        "🌦️ इस सप्ताह मौसम और बारिश कैसी रहेगी?",
        "🌿 सोयाबीन में पीला मोज़ेक से बचाव के उपाय बताएं।",
    ],
    "en": [
        "🐛 How to manage pink bollworm in cotton?",
        "🧅 What is today's onion mandi price?",
        "🌦️ What is the weather forecast for this week?",
        "🌿 How to prevent soybean yellow mosaic virus?",
    ],
}


def render_chat_page(farmer: AuthenticatedFarmer):
    """Render interactive AI chatbot page with refined bubbles and voice interaction."""
    lang = get_language()
    active_provider = (settings.AI_PROVIDER or "gemini").strip().lower()

    sparkle_svg = get_icon("sparkles", size=16, color="#fde047")
    bot_svg = get_icon("bot", size=24, color="#86efac")

    # Header Card with AI Avatar
    chat_hdr_html = textwrap.dedent(f"""
        <div class="tilt-card" style="
            background: linear-gradient(145deg, #071e13 0%, #0b2f1e 40%, #15462c 80%, #1e5a39 100%);
            border: 1px solid rgba(134, 239, 172, 0.2);
            border-radius: 22px;
            padding: 20px 24px;
            margin-bottom: 20px;
            box-shadow: 0 14px 34px -6px rgba(7, 30, 19, 0.3);
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 14px;
            color: #ffffff;
        ">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="width: 52px; height: 52px; border-radius: 16px; background: rgba(255,255,255,0.1); border: 1.5px solid rgba(255,255,255,0.25); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    {bot_svg}
                </div>
                <div>
                    <h2 style="margin: 0; color: #ffffff; font-size: 1.5rem; font-weight: 800; letter-spacing: -0.01em;">
                        AgriSaathi AI कृषी सल्लागार
                    </h2>
                    <p style="margin: 2px 0 0 0; color: #d1fae5; font-size: 0.98rem; font-weight: 500;">
                        {t('app_tagline', lang)}
                    </p>
                </div>
            </div>
            <div>
                <span style="background: rgba(255,255,255,0.16); border: 1px solid rgba(255,255,255,0.3); padding: 6px 14px; border-radius: 20px; font-size: 0.84rem; font-weight: 700; color: #ffffff; display: inline-flex; align-items: center; gap: 6px;">
                    {sparkle_svg} {'Google Gemini AI' if active_provider == 'gemini' else 'Local Ollama'}
                </span>
            </div>
        </div>
    """).strip()
    st.markdown(chat_hdr_html, unsafe_allow_html=True)

    # Provider Health Check
    if active_provider == "gemini":
        gemini_status = gemini_service.check_health()
        if not gemini_status.get("configured"):
            st.error(
                "⚠️ **Google Gemini API Key Configured नाही (Missing GEMINI_API_KEY)**: "
                "कृपया `.env` फाईलमध्ये किंवा Environment मध्ये `GEMINI_API_KEY` सेट करा."
            )
        elif not gemini_status.get("online"):
            st.warning(
                f"⚠️ **Google Gemini AI सेवा ऑफलाइन किंवा त्रुटीयुक्त आहे**: {gemini_status.get('error')}."
            )
    else:
        ollama_status = ollama_service.check_health()
        if not ollama_status.get("online"):
            st.warning("⚠️ **स्थानिक AI सेवा ऑफलाइन आहे (Ollama Offline)**.")

    with get_db() as db:
        farmer_crops = CropService.list_crops(db, farmer.id, status="active")
        conversations = ChatService.list_conversations(db, farmer.id, limit=30)

    # Active conversation management
    active_cid = st.session_state.get("active_conversation_id")
    if not active_cid and conversations:
        active_cid = conversations[0].id
        st.session_state["active_conversation_id"] = active_cid
    elif not active_cid and not conversations:
        with get_db() as db:
            init_c = ChatService.create_conversation(db, farmer.id, title="शेतकरी संवाद", preferred_language=lang)
        active_cid = init_c.id
        st.session_state["active_conversation_id"] = active_cid

    # Top Controls Bar: New Chat & Crop Context
    c_top1, c_top2 = st.columns([1, 1])
    with c_top1:
        if st.button("➕ नवीन चर्चा (New Chat)", use_container_width=True):
            with get_db() as db:
                new_c = ChatService.create_conversation(db, farmer.id, title="नवीन शेती प्रश्न", preferred_language=lang)
            st.session_state["active_conversation_id"] = new_c.id
            st.rerun()

    with c_top2:
        crop_options = {"None": "सर्व पिके / सामान्य (General)"}
        for cr in farmer_crops:
            crop_options[cr.id] = f"{cr.name} ({cr.growth_stage})"

        preselect_key = st.session_state.get("chat_crop_filter")
        default_index = 0
        crop_keys = list(crop_options.keys())
        if preselect_key in crop_keys:
            default_index = crop_keys.index(preselect_key)

        selected_crop_key = st.selectbox(
            "🌾 संदर्भ (Crop Context)",
            options=crop_keys,
            format_func=lambda k: crop_options[k],
            index=default_index,
        )

    # Voice Input Dictation Mic
    render_voice_mic_button(lang, prompt_placeholder="🎙️ आवाजाने विचारा (Speak question)")

    # 4 Quick Question Chips (WhatsApp style action tags)
    st.markdown("##### 💡 एका टॅपमध्ये विचारा (Quick Chips):")
    sample_qs = SAMPLE_QUESTIONS_MAP.get(lang, SAMPLE_QUESTIONS_MAP["en"])
    q_col1, q_col2 = st.columns(2)
    clicked_prompt = None

    if st.session_state.get("pending_ai_query"):
        clicked_prompt = st.session_state.pop("pending_ai_query")

    for idx, sq in enumerate(sample_qs):
        col_t = q_col1 if idx % 2 == 0 else q_col2
        with col_t:
            if st.button(sq, key=f"chat_chip_{idx}", use_container_width=True):
                clicked_prompt = sq

    st.markdown("<hr style='margin: 18px 0; border: none; border-top: 1.5px solid #d4ebd9;' />", unsafe_allow_html=True)

    # Render Messages in WhatsApp Bubbles
    with get_db() as db:
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == active_cid)
            .order_by(Message.created_at.asc())
            .all()
        )

    if not messages:
        empty_chat_html = textwrap.dedent("""
            <div class="empty-state-box">
                <div class="empty-state-icon">🌾👨‍🌾</div>
                <h3 style="margin: 0; color: #166534; font-weight: 800;">AgriSaathi AI कडे प्रश्न विचारा</h3>
                <p style="color: #4b5563; font-size: 1.05rem; margin: 8px 0 0 0;">
                    खते, फवारणी, रोग किंवा बाजारभावाबाबत वरील बटण दाबा किंवा खाली लिहा.
                </p>
            </div>
        """).strip()
        st.markdown(empty_chat_html, unsafe_allow_html=True)
    else:
        for idx, m in enumerate(messages):
            render_chat_bubble(m.role, m.content, lang=lang, show_audio=(m.role != "user"))

    # Chat Input Box
    placeholder_text = t("ask_question_placeholder", lang)
    user_input = st.chat_input(placeholder_text)
    effective_prompt = clicked_prompt or user_input

    if effective_prompt:
        render_chat_bubble("user", effective_prompt, lang=lang, show_audio=False)

        crop_arg = selected_crop_key if selected_crop_key != "None" else None

        with get_db() as db:
            context = ChatService.prepare_chat_context(
                db=db,
                farmer_id=farmer.id,
                conversation_id=active_cid,
                user_text=effective_prompt,
                crop_id=crop_arg,
                language=lang,
            )

        if context.get("limit_reached"):
            full_reply = ChatService.get_daily_limit_message(lang)
            st.warning(full_reply)
        else:
            spinner_msg = (
                "🌱 AgriSaathi AI उत्तर तयार करत आहे... (Google Gemini)..."
                if active_provider == "gemini"
                else "🌱 स्थानिक CPU वर उत्तर तयार होत आहे..."
            )
            with st.spinner(spinner_msg):
                full_reply = st.write_stream(ChatService.stream_reply(context["messages_payload"], language=lang))

        # Save assistant message
        with get_db() as db:
            ChatService.save_assistant_message(
                db=db,
                farmer_id=farmer.id,
                conversation_id=active_cid,
                content=full_reply,
                language=lang,
            )

        # Show RAG sources if any
        sources = context.get("retrieved_docs", [])
        if sources:
            with st.expander(f"📚 संदर्भ व अधिकृत स्रोत [{len(sources)}]", expanded=False):
                for s in sources:
                    st.markdown(f"**{s.get('title')}**")
                    st.caption(f"स्रोत: {s.get('source_name')} | [अधिकृत पोर्टल लिंक]({s.get('source_url')})")
                    st.text(s.get("content", "")[:250] + "...")

        st.rerun()
