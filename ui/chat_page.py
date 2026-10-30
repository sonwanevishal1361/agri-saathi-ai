"""Interactive, Accessible AI Farming Chatbot interface for Indian Farmers."""

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


SAMPLE_QUESTIONS_MAP = {
    "mr": [
        "🐛 कपाशीतील बोंडअळी नियंत्रणासाठी काय करावे?",
        "🌿 सोयाबीन पिवळा मोझॅक रोगावर काय उपाय आहेत?",
        "🌾 गव्हाच्या मुकुटमूळ (CRI) अवस्थेत पाण्याचे नियोजन कसे करावे?",
        "🧪 माती परीक्षणाचे (Soil Health Card) फायदे काय?",
        "💧 ठिबक सिंचनाचे अनुदान मिळवण्यासाठी काय प्रक्रिया आहे?",
    ],
    "hi": [
        "🐛 कपास में गुलाबी सुंडी (Pink Bollworm) का नियंत्रण कैसे करें?",
        "🌿 सोयाबीन में पीला मोज़ेक वायरस से बचाव के उपाय बताएं।",
        "🌾 गेहूं की पहली सिंचाई (CRI स्टेज) कब करनी चाहिए?",
        "🧪 मृदा स्वास्थ्य कार्ड (Soil Health Card) के क्या लाभ हैं?",
        "💧 पीएम किसान सम्मान निधि की पात्रता क्या है?",
    ],
    "en": [
        "🐛 How to manage pink bollworm in Bt cotton?",
        "🌿 What are prevention steps for Soybean Yellow Mosaic Virus?",
        "🌾 What is the critical irrigation schedule for Wheat (CRI stage)?",
        "🧪 How does balanced fertilizer use based on Soil Health Card help?",
        "💧 What are the benefits and eligibility for PM-KISAN?",
    ],
}


def render_chat_page(farmer: AuthenticatedFarmer):
    """Render interactive AI chatbot page with responsive bubbles, bounded history, and citations."""
    lang = get_language()
    active_provider = (settings.AI_PROVIDER or "gemini").strip().lower()

    # Header Card
    st.markdown(
        f"""
        <div style="background: #ffffff; border: 2px solid #a5d6a7; border-radius: 12px; padding: 16px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <h2 style="margin: 0; color: #1b5e20;">🤖 AgriSaathi AI कृषी सल्लागार</h2>
                    <p style="margin: 4px 0 0 0; color: #3e523e; font-size: 0.95rem;">
                        शेतकऱ्यांना सोप्या भाषेत अचूक, विश्वासू आणि व्यावहारिक मार्गदर्शन
                    </p>
                </div>
                <div>
                    <span style="background: #e8f5e9; border: 1.5px solid #81c784; padding: 6px 12px; border-radius: 20px; font-size: 0.82rem; font-weight: 700; color: #1b5e20;">
                        🧠 Engine: {'Google Gemini 3.5' if active_provider == 'gemini' else 'Local Ollama'}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Provider Health Check
    if active_provider == "gemini":
        gemini_status = gemini_service.check_health()
        if not gemini_status.get("configured"):
            st.error(
                "⚠️ **Google Gemini API Key Configured नाही (Missing GEMINI_API_KEY)**: "
                "कृपया `.env` फाईलमध्ये किंवा Environment मध्ये `GEMINI_API_KEY` सेट करा. "
                "इतर सर्व शेती नोंदी, खर्च, हवामान व बाजारभाव सामान्यपणे कार्यरत आहेत."
            )
        elif not gemini_status.get("online"):
            st.warning(
                f"⚠️ **Google Gemini AI सेवा ऑफलाइन किंवा त्रुटीयुक्त आहे**: {gemini_status.get('error')}. "
                "कृपया इंटरनेट कनेक्शन किंवा API कोटा तपासा."
            )
    else:
        ollama_status = ollama_service.check_health()
        if not ollama_status.get("online"):
            st.warning(
                "⚠️ **स्थानिक AI सेवा ऑफलाइन आहे (Ollama Offline)**: स्थानिक संगणकावर Ollama चालू असल्याची खात्री करा (`ollama serve`). "
                "इतर सर्व शेती नोंदी, हवामान व बाजारभाव सामान्यपणे कार्यरत आहेत."
            )

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

    # Controls Bar: Conversation Actions, Language & Crop Filter
    c_top1, c_top2 = st.columns([1, 1])
    with c_top1:
        if st.button("➕ नवीन चर्चा सुरू करा (New Chat)", use_container_width=True):
            with get_db() as db:
                new_c = ChatService.create_conversation(db, farmer.id, title="नवीन शेती प्रश्न", preferred_language=lang)
            st.session_state["active_conversation_id"] = new_c.id
            st.rerun()

    with c_top2:
        crop_options = {"None": "सर्व पिके / सामान्य माहिती (General Agriculture)"}
        for cr in farmer_crops:
            crop_options[cr.id] = f"{cr.name} ({cr.variety or 'General'}) - {cr.growth_stage}"

        preselect_key = st.session_state.get("chat_crop_filter")
        default_index = 0
        crop_keys = list(crop_options.keys())
        if preselect_key in crop_keys:
            default_index = crop_keys.index(preselect_key)

        selected_crop_key = st.selectbox(
            "🌾 पिकाचा संदर्भ जोडा (Crop Context)",
            options=crop_keys,
            format_func=lambda k: crop_options[k],
            index=default_index,
        )

    # Past conversations switcher if multiple exist
    if len(conversations) > 1:
        with st.expander(f"💬 मागील संभाषणे निवडा (Saved Conversations) [{len(conversations)}]", expanded=False):
            conv_cols = st.columns(2)
            for i, c in enumerate(conversations):
                with conv_cols[i % 2]:
                    marker = "👉 " if c.id == active_cid else ""
                    if st.button(f"{marker}{c.title[:30]}", key=f"c_pick_{c.id}", use_container_width=True):
                        st.session_state["active_conversation_id"] = c.id
                        st.rerun()

    st.markdown("---")

    # Suggested Starter Questions (Responsive 2-column grid instead of squashed 5 columns)
    st.markdown("##### 💡 तयार प्रश्न (Tap to ask):")
    sample_qs = SAMPLE_QUESTIONS_MAP.get(lang, SAMPLE_QUESTIONS_MAP["en"])
    sq_col1, sq_col2 = st.columns(2)
    clicked_prompt = None
    for idx, sq in enumerate(sample_qs):
        target_col = sq_col1 if idx % 2 == 0 else sq_col2
        with target_col:
            if st.button(sq, key=f"quick_sq_{idx}", use_container_width=True):
                clicked_prompt = sq

    st.markdown("---")

    # Render Messages with High-Contrast Chat Bubbles
    with get_db() as db:
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == active_cid)
            .order_by(Message.created_at.asc())
            .all()
        )

    if not messages:
        st.markdown(
            """
            <div class="empty-state-box">
                <div class="empty-state-icon">💬</div>
                <h4 style="margin: 0; color: #1b5e20;">कोणताही प्रश्न विचारा (Ask your farming query)</h4>
                <p style="color: #4b634b; font-size: 0.95rem; margin: 8px 0 0 0;">
                    बियाणे, खत मात्रा, फवारणी, रोग किंवा हवामानाविषयी खालील बॉक्समध्ये लिहा किंवा वरील प्रश्नांवर टॅप करा.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for m in messages:
            if m.role == "user":
                with st.chat_message("user", avatar="🧑‍🌾"):
                    st.markdown(
                        f"""
                        <div style="background: #e8f5e9; border: 1.5px solid #a5d6a7; border-radius: 12px; padding: 12px 16px; font-size: 1.05rem; color: #1b3b1b; line-height: 1.5;">
                            {m.content}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                with st.chat_message("assistant", avatar="🌱"):
                    st.markdown(
                        f"""
                        <div style="background: #ffffff; border: 1.5px solid #c8e6c9; border-radius: 12px; padding: 14px 18px; font-size: 1.05rem; color: #142814; line-height: 1.6; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                            {m.content}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # Chat Input Box
    placeholder_text = t("ask_question_placeholder", lang)
    user_input = st.chat_input(placeholder_text)
    effective_prompt = clicked_prompt or user_input

    if effective_prompt:
        # Display user message immediately
        with st.chat_message("user", avatar="🧑‍🌾"):
            st.markdown(
                f"""
                <div style="background: #e8f5e9; border: 1.5px solid #a5d6a7; border-radius: 12px; padding: 12px 16px; font-size: 1.05rem; color: #1b3b1b;">
                    {effective_prompt}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Generate Assistant Response
        with st.chat_message("assistant", avatar="🌱"):
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

            spinner_msg = (
                "🌱 AgriSaathi AI उत्तर तयार करत आहे... (Google Gemini Streaming)..."
                if active_provider == "gemini"
                else "🌱 स्थानिक CPU वर उत्तर तयार होत आहे..."
            )

            with st.spinner(spinner_msg):
                full_reply = st.write_stream(ChatService.stream_reply(context["messages_payload"]))

            # Persist assistant reply
            with get_db() as db:
                ChatService.save_assistant_message(
                    db=db,
                    farmer_id=farmer.id,
                    conversation_id=active_cid,
                    content=full_reply,
                )

            # Display RAG Source Citations
            sources = context.get("retrieved_docs", [])
            if sources:
                with st.expander(f"📚 संदर्भ व अधिकृत स्रोत (Verified Agronomic Sources) [{len(sources)}]", expanded=False):
                    for s in sources:
                        st.markdown(f"**{s.get('title')}**")
                        st.caption(f"स्रोत: {s.get('source_name')} | [अधिकृत पोर्टल लिंक]({s.get('source_url')})")
                        st.text(s.get("content", "")[:250] + "...")

        st.rerun()
