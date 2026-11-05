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
from ui.auth_pages import render_auth_page, render_force_password_change
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
from ui.privacy_page import render_privacy_page
from ui.admin_page import render_admin_page
from ui.components.bottom_nav import render_bottom_nav
from utils.language import t


# 1. Page Configuration
st.set_page_config(
    page_title=f"{settings.APP_NAME} - Your Smart Farming Companion",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 1.1 Health Check Route (?health=true or ?page=health)
if hasattr(st, "query_params") and (
    st.query_params.get("health") in ("true", "1") or st.query_params.get("page") == "health"
):
    from core.health import check_system_health
    health_status = check_system_health()
    st.title("🏥 AgriSaathi AI Health Diagnostics")
    st.json(health_status)
    st.stop()

# 2. Automatic Database Bootstrap (Streamlit Community Cloud & Production Ready)
if not bootstrap_database():
    st.stop()

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

# 5.1 Enforce Password Change on First Login
if getattr(current_farmer, "must_change_password", False):
    render_force_password_change(current_farmer)
    st.stop()

# 5.2 Enterprise Admin Portal Route
active_page = st.session_state.get("current_page", "dashboard")
if active_page == "admin":
    if not current_farmer or not current_farmer.is_admin:
        st.error("⛔ प्रवेश नाकारला / Access Denied: Administrator privileges required.")
        set_page("dashboard")
        st.rerun()
    render_admin_page(current_farmer)
    st.stop()

# 6. Top Persistent Floating Header with Language Switcher, Profile & Logout on Every Page
farmer_loc_parts = [p for p in [current_farmer.village, current_farmer.district, current_farmer.state] if p]
farmer_loc_display = " • 📍 " + ", ".join(farmer_loc_parts) if farmer_loc_parts else ""

with st.container(key="top_header_container"):
    top_col1, top_col2, top_col3 = st.columns([5, 3, 3])
    with top_col1:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
                <div style="width: 44px; height: 44px; border-radius: 14px; background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); display: flex; align-items: center; justify-content: center; font-size: 1.6rem; box-shadow: 0 2px 8px rgba(30,107,62,0.15); border: 1.5px solid #a5d6a7;">
                    🌱
                </div>
                <div>
                    <h3 style="margin: 0; color: #0f3822; font-size: 1.35rem; font-weight: 800; line-height: 1.2;">
                        AgriSaathi AI <span style="font-size: 0.88rem; color: #1e6b3e; font-weight: 700;">(कृषी साथी)</span>
                    </h3>
                    <span style="font-size: 0.85rem; color: #2e7d32; font-weight: 700;">
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
            format_func=lambda x: "🚩 मराठी (Marathi)" if x == "mr" else ("🇮🇳 हिंदी (Hindi)" if x == "hi" else "🌐 English"),
            index=lang_opts.index(lang) if lang in lang_opts else 0,
            key="top_persistent_lang_select",
            label_visibility="collapsed",
        )
        if lang_choice != lang:
            set_language(lang_choice)
            st.rerun()

    with top_col3:
        profile_lbl = "👤 " + ("प्रोफाइल" if lang == "mr" else ("प्रोफ़ाइल" if lang == "hi" else "Profile"))
        logout_lbl = "🚪 " + ("लॉग आउट" if lang in ("mr", "hi") else "Logout")
        if current_farmer.is_admin:
            hdr_a_col, hdr_p_col, hdr_l_col = st.columns([4, 3, 3])
            with hdr_a_col:
                if st.button("🛠️ Admin", key="hdr_btn_admin", use_container_width=True, type="primary"):
                    set_page("admin")
                    st.rerun()
            with hdr_p_col:
                if st.button(profile_lbl, key="hdr_btn_profile", use_container_width=True):
                    set_page("profile")
                    st.rerun()
            with hdr_l_col:
                if st.button(logout_lbl, key="hdr_btn_logout", use_container_width=True):
                    logout()
                    st.rerun()
        else:
            hdr_p_col, hdr_l_col = st.columns(2)
            with hdr_p_col:
                if st.button(profile_lbl, key="hdr_btn_profile", use_container_width=True):
                    set_page("profile")
                    st.rerun()
            with hdr_l_col:
                if st.button(logout_lbl, key="hdr_btn_logout", use_container_width=True):
                    logout()
                    st.rerun()

# 6. Primary Desktop Navigation Bar (Hidden on Mobile)
with st.container(key="desktop_nav_container"):
    sections = {
        "home": f"🏠 {t('nav_home', lang)}",
        "chat": f"🤖 {t('nav_ask_ai', lang)}",
        "my_farm": f"🌾 {t('nav_my_farm', lang)}",
        "market_schemes": f"📈 {t('nav_market_schemes', lang)}",
        "profile": f"👤 {t('nav_profile', lang)}",
    }
    if current_farmer.is_admin:
        sections["admin"] = "🛠️ Admin"

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
                elif sk == "admin":
                    set_page("admin")
                st.rerun()

    st.markdown("<hr style='margin: 10px 0 16px 0; border: none; border-top: 1.5px solid #d4ebd9;' />", unsafe_allow_html=True)

    # 7. Secondary Sub-Tabs for "My Farm" and "Market & Schemes" (Desktop Only)
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

# 8. Sidebar Companion - Farmer Digital Card & Emergency Support Drawer
with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align: center; padding: 12px 0 14px 0; border-bottom: 1.5px solid #d4ebd9; margin-bottom: 14px;">
            <div style="font-size: 2.2rem; margin-bottom: 4px;">🌱</div>
            <h2 style="color: #0f3822; margin: 0; font-size: 1.35rem; font-weight: 800;">AgriSaathi AI</h2>
            <p style="color: #2e7d32; font-size: 0.88rem; margin: 2px 0 0 0; font-weight: 700;">
                {t('app_tagline', lang)}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Farmer Identity Card
    f_loc = ", ".join(farmer_loc_parts) if farmer_loc_parts else "महाराष्ट्र"
    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1.5px solid #d4ebd9; border-radius: 16px; padding: 14px 16px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(15, 56, 34, 0.05);">
            <div style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; color: #166534; font-weight: 800; margin-bottom: 4px;">
                🌾 शेतकरी डिजिटल खाते
            </div>
            <div style="font-size: 1.15rem; font-weight: 800; color: #0f3822;">
                👤 {current_farmer.full_name}
            </div>
            <div style="font-size: 0.88rem; color: #4b5563; margin-top: 4px;">
                📞 {current_farmer.phone or 'मोबाईल नोंदणीकृत'}
            </div>
            <div style="font-size: 0.86rem; color: #2e7d32; font-weight: 600; margin-top: 2px;">
                📍 {f_loc} • ✅ सक्रिय खाते
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Kisan Call Centre 24/7 Helpline Card
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #e8f5e9 100%); border: 1.5px solid #a5d6a7; border-radius: 16px; padding: 14px 16px; margin-bottom: 16px;">
            <div style="font-size: 0.78rem; font-weight: 800; color: #1e6b3e; text-transform: uppercase; letter-spacing: 0.04em;">
                📞 मोफत शेतकरी हेल्पलाइन
            </div>
            <div style="font-size: 1.05rem; font-weight: 800; color: #0f3822; margin-top: 4px;">
                किसान कॉल सेंटर: <span style="color: #1b5e20;">1800-180-1551</span>
            </div>
            <div style="font-size: 0.8rem; color: #374151; margin-top: 4px; line-height: 1.35;">
                २४ तास मोफत कृषी तज्ज्ञ सल्ला (मराठी/हिंदी)
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # DPDP 2023 Digital Farmer Privacy & Trust
    st.markdown(
        """
        <div style="background: #ffffff; border: 1px solid #e2ece4; border-radius: 14px; padding: 12px 14px; margin-bottom: 16px; font-size: 0.8rem; color: #4b5563;">
            <div style="font-weight: 700; color: #166534; display: flex; align-items: center; gap: 6px; margin-bottom: 3px;">
                🛡️ DPDP कायदा २०२३ सुसंगत
            </div>
            आपला शेती व वैयक्तिक डेटा १००% सुरक्षित आणि गोपनीय आहे.
        </div>
        """,
        unsafe_allow_html=True,
    )

# 9. Render Selected Page
if active_page == "dashboard":
    render_dashboard(current_farmer)
elif active_page == "admin":
    if not current_farmer or not current_farmer.is_admin:
        st.error("⛔ प्रवेश नाकारला / Access Denied: Administrator privileges required.")
        set_page("dashboard")
        st.rerun()
    render_admin_page(current_farmer)
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
elif active_page == "privacy":
    render_privacy_page()
else:
    render_dashboard(current_farmer)

# 10. Fixed Bottom Navigation Bar for Mobile One-Hand Thumb Reach
render_bottom_nav(current_page=active_page, is_admin=current_farmer.is_admin)

# 11. Global Footer
st.markdown(
    """
    <div style="text-align: center; margin-top: 40px; padding: 20px 10px 14px 10px; border-top: 1.5px solid #dceedd; color: #475569; font-size: 0.88rem;">
        🌱 <strong>AgriSaathi AI (कृषी साथी AI)</strong> — भारतीय शेतकऱ्यांसाठी प्रगत डिजिटल शेती सहाय्यक प्लॅटफॉर्म<br>
        <span style="font-size: 0.82rem; color: #166534; font-weight: 600;">🌾 ICAR व कृषी विद्यापीठ शिफारशींवर आधारित • DPDP कायदा २०२३ सुसंगत डेटा सुरक्षा</span><br>
        <span style="font-size: 0.78rem; color: #64748b; margin-top: 6px; display: inline-block;">वास्तूकार: विशाल सोनवणे | Architect: Vishal Sonwane</span>
    </div>
    """,
    unsafe_allow_html=True,
)
