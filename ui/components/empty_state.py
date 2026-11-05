"""Polished Empty State Component for AgriSaathi AI."""

import textwrap
from typing import Optional
import streamlit as st


def render_empty_state(
    icon: str = "🌱",
    title: str = "कोणतीही माहिती उपलब्ध नाही",
    description: str = "नवीन माहिती जोडण्यासाठी खालील बटणावर टॅप करा.",
    button_text: Optional[str] = None,
    button_key: str = "empty_state_action_btn",
) -> bool:
    """Render an encouraging agricultural empty state box with 56px action button."""
    html = textwrap.dedent(f"""
    <div class="empty-state-box">
        <div class="empty-state-icon">{icon}</div>
        <h3 style="margin: 0; color: #166534; font-size: 1.35rem; font-weight: 800;">{title}</h3>
        <p style="color: #4b634b; font-size: 1.05rem; margin: 8px 0 20px 0; font-weight: 500; max-width: 500px; margin-left: auto; margin-right: auto;">
            {description}
        </p>
    </div>
    """).strip()
    st.markdown(html, unsafe_allow_html=True)

    if button_text:
        return st.button(button_text, key=button_key, use_container_width=True, type="primary")
    return False

