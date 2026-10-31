"""AgriSaathi AI - Complete AI-Powered Farming Support Platform for Indian Farmers.

Streamlit main application entrypoint with mobile-first 5-section navigation and accessible theme.
"""

import streamlit as st
from config import settings
from core.database import bootstrap_database
from ui.theme import inject_custom_theme
from ui.state import (
    init_session_state,
    get_current_farmer,
    logout,
    get_language,
    set_language,
    set_page,
)
from ui.auth_pages import render_auth_page
from ui.dashboard import render_dashboard
from ui.crops_page import render_crops_page
from ui.crop_detail import render_crop_detail
from ui.knowledge_page import render_knowledge_page
from ui.chat_page import render_chat_page
from ui.diary_page import render_diary_page
from ui.expenses_page import render_expenses_page
from ui.harvest_page import render_harvest_page
from ui.weather_page import render_weather_page
from ui.market_page import render_market_page
from ui.schemes_page import render_schemes_page
from ui.image_page import render_image_page
from ui.profile_page import render_profile_page
from utils.language import t


# 1. Page Configuration
st.set_page_config(
    page_title=f"{settings.APP_NAME} - Your Smart Farming Companion",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Automatic Database Bootstrap (Streamlit Community Cloud & Production Ready)
@st.cache_resource(show_spinner=False)
def _st_bootstrap() -> bool:
    return bootstrap_database()

_st_bootstrap()

# 3. Inject Shared Theme & Mobile Styles
inject_custom_theme()

# 4. Session State Initialization
init_session_state()
current_farmer = get_current_farmer()
lang = get_language()

# 5. Authentication Gate
if not current_farmer:
    render_auth_page()
    st.stop()

# 6. Top Persistent Header with Language Switcher, Profile & Logout on Every Page
farmer_loc_parts = [p for p in [current_farmer.village, current_farmer.district, current_farmer.state] if p]
farmer_loc_display = " • 📍 " + ", ".join(farmer_loc_parts) if farmer_loc_parts else ""

top_col1, top_col2, top_col3 = st.columns([5, 3, 3])
with top_col1:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
            <span style="font-size: 1.8rem;">🌱</span>
            <div>
                <h3 style="margin: 0; color: #1b5e20; line-height: 1.2;">AgriSaathi AI (कृषी साथी AI)</h3>
                <span style="font-size: 0.84rem; color: #2e7d32; font-weight: 600;">
                    👤 {current_farmer.full_name}{farmer_loc_display}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with top_col2:
    lang_opts = ["mr", "hi", "en"]
    lang_choice = st.selectbox(
        "🌐 भाषा (Language)",
        options=lang_opts,
        format_func=lambda x: "मराठी (Marathi)" if x == "mr" else ("हिंदी (Hindi)" if x == "hi" else "English"),
        index=lang_opts.index(lang) if lang in lang_opts else 0,
        key="top_persistent_lang_select",
        label_visibility="collapsed",
    )
    if lang_choice != lang:
        set_language(lang_choice)
        st.rerun()

with top_col3:
    hdr_p_col, hdr_l_col = st.columns(2)
    with hdr_p_col:
        if st.button("👤 " + t("profile", lang), key="hdr_btn_profile", use_container_width=True):
            set_page("profile")
            st.rerun()
    with hdr_l_col:
        if st.button("🚪 " + t("logout", lang), key="hdr_btn_logout", use_container_width=True):
            logout()
            st.rerun()

# 6. Primary 5-Section Mobile Navigation Bar
sections = {
    "home": f"🏠 {t('nav_home', lang)}",
    "chat": f"🤖 {t('nav_ask_ai', lang)}",
    "my_farm": f"🌾 {t('nav_my_farm', lang)}",
    "market_schemes": f"📈 {t('nav_market_schemes', lang)}",
    "profile": f"👤 {t('nav_profile', lang)}",
}

active_sec = st.session_state.get("active_section", "home")
if active_sec not in sections:
    active_sec = "home"

sec_keys = list(sections.keys())
sec_cols = st.columns(len(sec_keys))
for idx, sk in enumerate(sec_keys):
    with sec_cols[idx]:
        is_active = (active_sec == sk)
        btn_type = "primary" if is_active else "secondary"
        if st.button(sections[sk], key=f"nav_btn_{sk}", use_container_width=True, type=btn_type):
            if sk == "home":
                set_page("dashboard")
            elif sk == "chat":
                set_page("chat")
            elif sk == "my_farm":
                set_page("crops")
            elif sk == "market_schemes":
                set_page("market")
            elif sk == "profile":
                set_page("profile")
            st.rerun()

st.markdown("<hr style='margin: 12px 0 16px 0; border: none; border-top: 1.5px solid #c8e6c9;' />", unsafe_allow_html=True)

# 7. Secondary Sub-Tabs for "My Farm" and "Market & Schemes"
active_page = st.session_state.get("current_page", "dashboard")

if active_sec == "my_farm":
    farm_tabs = {
        "crops": f"🌾 {t('tab_crops', lang)}",
        "diary": f"📅 {t('tab_diary', lang)}",
        "expenses": f"💸 {t('tab_expenses', lang)}",
        "harvest": f"💰 {t('tab_harvest', lang)}",
    }
    # If on crop_detail, highlight crops tab
    effective_sub = "crops" if active_page in ["crops", "crop_detail"] else active_page
    if effective_sub not in farm_tabs:
        effective_sub = "crops"

    ft_cols = st.columns(len(farm_tabs))
    for idx, (fk, flabel) in enumerate(farm_tabs.items()):
        with ft_cols[idx]:
            is_sub_active = (effective_sub == fk)
            sub_type = "primary" if is_sub_active else "secondary"
            if st.button(flabel, key=f"farm_sub_{fk}", use_container_width=True, type=sub_type):
                set_page(fk)
                st.rerun()

    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

elif active_sec == "market_schemes":
    market_tabs = {
        "market": f"📈 {t('tab_mandi', lang)}",
        "weather": f"🌦️ {t('tab_weather', lang)}",
        "schemes": f"🏛️ {t('tab_schemes', lang)}",
        "image": f"🔬 {t('tab_crop_health', lang)}",
        "knowledge": f"📚 {t('tab_knowledge', lang)}",
    }
    effective_m = active_page if active_page in market_tabs else "market"
    mt_cols = st.columns(len(market_tabs))
    for idx, (mk, mlabel) in enumerate(market_tabs.items()):
        with mt_cols[idx]:
            is_m_active = (effective_m == mk)
            m_type = "primary" if is_m_active else "secondary"
            if st.button(mlabel, key=f"market_sub_{mk}", use_container_width=True, type=m_type):
                set_page(mk)
                st.rerun()

    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# 8. Sidebar Companion with Profile & Quick Controls
with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align: center; padding: 10px 0 12px 0;">
            <h2 style="color: #1b5e20; margin: 0;">🌱 AgriSaathi AI</h2>
            <p style="color: #2e7d32; font-size: 0.85rem; margin: 0; font-weight: 600;">
                {t('app_tagline', lang)}
            </p>
            <div style="margin-top: 8px; padding: 6px 8px; background: #e8f5e9; border: 1px solid #a5d6a7; border-radius: 8px; font-size: 0.8rem; color: #1b5e20; font-weight: 600;">
                👨‍💻 Architect: <strong>Vishal Sonwane</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"**👤 {current_farmer.full_name}**")
    if current_farmer.district:
        st.caption(f"📍 {current_farmer.village or ''}, {current_farmer.district}")

    st.markdown("---")
    st.markdown(f"##### ⚡ {t('quick_links', lang)}")
    if st.button(f"🏠 {t('nav_home', lang)}", key="sb_nav_home", use_container_width=True):
        set_page("dashboard")
        st.rerun()
    if st.button(f"🤖 {t('nav_ask_ai', lang)}", key="sb_nav_chat", use_container_width=True):
        set_page("chat")
        st.rerun()
    if st.button(f"🌾 {t('my_crops', lang)}", key="sb_nav_crops", use_container_width=True):
        set_page("crops")
        st.rerun()
    if st.button(f"💸 {t('expenses', lang)}", key="sb_nav_exp", use_container_width=True):
        set_page("expenses")
        st.rerun()
    if st.button(f"📈 {t('mandi_prices', lang)}", key="sb_nav_mandi", use_container_width=True):
        set_page("market")
        st.rerun()
    if st.button(f"🌦️ {t('weather', lang)}", key="sb_nav_weather", use_container_width=True):
        set_page("weather")
        st.rerun()
    if st.button(f"👤 {t('profile', lang)}", key="sb_nav_profile", use_container_width=True):
        set_page("profile")
        st.rerun()

    st.markdown("---")
    if st.button(f"🚪 {t('logout', lang)}", key="sb_logout_btn", use_container_width=True):
        logout()
        st.rerun()

# 9. Render Selected Page
if active_page == "dashboard":
    render_dashboard(current_farmer)
elif active_page == "crops":
    render_crops_page(current_farmer)
elif active_page == "crop_detail":
    render_crop_detail(current_farmer, st.session_state.get("selected_crop_id"))
elif active_page == "chat":
    render_chat_page(current_farmer)
elif active_page == "diary":
    render_diary_page(current_farmer)
elif active_page == "expenses":
    render_expenses_page(current_farmer)
elif active_page == "harvest":
    render_harvest_page(current_farmer)
elif active_page == "image":
    render_image_page(current_farmer)
elif active_page == "knowledge":
    render_knowledge_page(current_farmer)
elif active_page == "weather":
    render_weather_page(current_farmer)
elif active_page == "market":
    render_market_page(current_farmer)
elif active_page == "schemes":
    render_schemes_page(current_farmer)
elif active_page == "profile":
    render_profile_page(current_farmer)
else:
    render_dashboard(current_farmer)

# 10. Global Footer
st.markdown(
    """
    <div style="text-align: center; margin-top: 50px; padding: 20px 10px 10px 10px; border-top: 1.5px solid #dceedd; color: #444; font-size: 0.88rem;">
        🌱 <strong>AgriSaathi AI</strong> — Smart Farming Companion for Indian Agriculture<br>
        Crafted & Architected with ❤️ for Indian Farmers by <strong>Vishal Sonwane</strong>
    </div>
    """,
    unsafe_allow_html=True,
)
