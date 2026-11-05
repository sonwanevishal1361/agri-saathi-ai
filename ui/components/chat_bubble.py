"""WhatsApp-style agricultural chat bubbles for AgriSaathi AI.

Includes farmer/advisor vector avatars, formatted markdown text, and
browser Web Speech API audio read-aloud buttons.
"""

import html
import textwrap
import streamlit as st
from ui.components.voice_button import render_speaker_button


def render_chat_bubble(
    role: str,
    content: str,
    lang: str = "mr",
    show_audio: bool = True,
):
    """Render a WhatsApp-style chat bubble for user or AI assistant."""
    escaped_content = html.escape(content).replace("\n", "<br>")

    if role == "user":
        user_html = textwrap.dedent(f"""
        <div class="chat-bubble-row chat-row-user">
            <div class="chat-bubble chat-bubble-user">
                <div style="font-size: 0.8rem; font-weight: 800; color: #1b5e20; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
                    🧑‍🌾 <span>शेतकरी</span>
                </div>
                <div style="font-size: 1.05rem; line-height: 1.5; color: #1f2a1f;">
                    {escaped_content}
                </div>
            </div>
        </div>
        """).strip()
        st.markdown(user_html, unsafe_allow_html=True)
    else:
        asst_html = textwrap.dedent(f"""
        <div class="chat-bubble-row chat-row-assistant">
            <div class="chat-avatar">🌱</div>
            <div class="chat-bubble chat-bubble-assistant">
                <div style="font-size: 0.8rem; font-weight: 800; color: #166534; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
                    🤖 <span>AgriSaathi AI सल्लागार</span>
                </div>
                <div style="font-size: 1.05rem; line-height: 1.55; color: #1f2a1f;">
                    {escaped_content}
                </div>
            </div>
        </div>
        """).strip()
        st.markdown(asst_html, unsafe_allow_html=True)

        if show_audio:
            listen_label = "🔊 उत्तर ऐका (Listen)" if lang == "mr" else ("🔊 उत्तर सुनें (Listen)" if lang == "hi" else "🔊 Listen Answer")
            render_speaker_button(content, lang=lang, button_label=listen_label)

