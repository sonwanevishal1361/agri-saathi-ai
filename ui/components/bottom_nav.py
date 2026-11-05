"""Fixed bottom navigation bar for one-hand thumb use on Indian smartphones."""

import textwrap
import streamlit as st
from ui.state import get_language, set_page
from utils.language import t


def render_bottom_nav(current_page: str, is_admin: bool = False):
    """Render a fixed bottom navigation bar with 5 thumb destinations and center elevated mic button."""
    lang = get_language()

    # Define localized labels
    labels = {
        "home": {"mr": "🏠 मुख्य", "hi": "🏠 मुख्य", "en": "🏠 Home"},
        "crops": {"mr": "🌾 पिके", "hi": "🌾 फसलें", "en": "🌾 Crops"},
        "voice": {"mr": "🎤 बोला", "hi": "🎤 बोलें", "en": "🎤 Voice"},
        "market": {"mr": "📈 बाजार", "hi": "📈 मंडी", "en": "📈 Mandi"},
        "more": {"mr": "➕ अधिक", "hi": "➕ अधिक", "en": "➕ More"},
    }

    # Determine which main tab is active
    active_key = "home"
    if current_page in ("dashboard",):
        active_key = "home"
    elif current_page in ("crops", "crop_detail"):
        active_key = "crops"
    elif current_page in ("chat",):
        active_key = "voice"
    elif current_page in ("market", "weather"):
        active_key = "market"
    elif current_page in ("diary", "expenses", "harvest", "schemes", "image", "knowledge", "profile", "admin", "privacy"):
        active_key = "more"

    st.markdown('<div class="agri-bottom-nav-spacer"></div>', unsafe_allow_html=True)

    # If "More" section is toggled open, show quick drawer above nav
    show_more = st.session_state.get("show_more_drawer", False)
    if show_more:
        with st.container():
            st.markdown(
                textwrap.dedent(f"""
                <div class="agri-more-drawer">
                    <div style="font-weight: 800; color: #1b5e20; margin-bottom: 10px; font-size: 1.05rem; display: flex; justify-content: space-between; align-items: center;">
                        <span>⚡ {t('more_tools_drawer_title', lang) if t('more_tools_drawer_title', lang) != 'more_tools_drawer_title' else 'अधिक शेती साधने (More Tools)'}</span>
                        <span style="font-size: 0.85rem; color: #6d4c41; font-weight: 600;">AgriSaathi Suite</span>
                    </div>
                </div>
                """).strip(),
                unsafe_allow_html=True,
            )
            d_cols1 = st.columns(3)
            with d_cols1[0]:
                if st.button("📅 " + t("tab_diary", lang), key="bnav_drawer_diary", use_container_width=True):
                    st.session_state["show_more_drawer"] = False
                    set_page("diary")
                    st.rerun()
            with d_cols1[1]:
                if st.button("💸 " + t("tab_expenses", lang), key="bnav_drawer_expenses", use_container_width=True):
                    st.session_state["show_more_drawer"] = False
                    set_page("expenses")
                    st.rerun()
            with d_cols1[2]:
                if st.button("🌦️ " + t("tab_weather", lang), key="bnav_drawer_weather", use_container_width=True):
                    st.session_state["show_more_drawer"] = False
                    set_page("weather")
                    st.rerun()

            d_cols2 = st.columns(3)
            with d_cols2[0]:
                if st.button("🏛️ " + t("tab_schemes", lang), key="bnav_drawer_schemes", use_container_width=True):
                    st.session_state["show_more_drawer"] = False
                    set_page("schemes")
                    st.rerun()
            with d_cols2[1]:
                if st.button("🔬 " + t("tab_crop_health", lang), key="bnav_drawer_image", use_container_width=True):
                    st.session_state["show_more_drawer"] = False
                    set_page("image")
                    st.rerun()
            with d_cols2[2]:
                if st.button("👤 " + t("profile", lang), key="bnav_drawer_profile", use_container_width=True):
                    st.session_state["show_more_drawer"] = False
                    set_page("profile")
                    st.rerun()

            if is_admin:
                if st.button("🛠️ Developer Admin Panel", key="bnav_drawer_admin", use_container_width=True, type="primary"):
                    st.session_state["show_more_drawer"] = False
                    set_page("admin")
                    st.rerun()

    # Fixed Bottom Navigation Container (5 destinations with center mic button)
    with st.container(key="bottom_nav_container"):
        c1, c2, c3, c4, c5 = st.columns([1, 1, 1.25, 1, 1])

        with c1:
            is_sel = active_key == "home" and not show_more
            btn_type = "primary" if is_sel else "secondary"
            if st.button(labels["home"].get(lang, "🏠 Home"), key="bnav_home", use_container_width=True, type=btn_type):
                st.session_state["show_more_drawer"] = False
                set_page("dashboard")
                st.rerun()

        with c2:
            is_sel = active_key == "crops" and not show_more
            btn_type = "primary" if is_sel else "secondary"
            if st.button(labels["crops"].get(lang, "🌾 Crops"), key="bnav_crops", use_container_width=True, type=btn_type):
                st.session_state["show_more_drawer"] = False
                set_page("crops")
                st.rerun()

        with c3:
            # Elevated center action button: Voice AI
            voice_lbl = labels["voice"].get(lang, "🎤 Voice")
            if st.button(voice_lbl, key="bnav_voice_center", use_container_width=True, type="primary"):
                st.session_state["show_more_drawer"] = False
                set_page("chat")
                st.rerun()

        with c4:
            is_sel = active_key == "market" and not show_more
            btn_type = "primary" if is_sel else "secondary"
            if st.button(labels["market"].get(lang, "📈 Mandi"), key="bnav_market", use_container_width=True, type=btn_type):
                st.session_state["show_more_drawer"] = False
                set_page("market")
                st.rerun()

        with c5:
            is_sel = active_key == "more" or show_more
            btn_type = "primary" if is_sel else "secondary"
            if st.button(labels["more"].get(lang, "➕ More"), key="bnav_more", use_container_width=True, type=btn_type):
                st.session_state["show_more_drawer"] = not show_more
                st.rerun()
