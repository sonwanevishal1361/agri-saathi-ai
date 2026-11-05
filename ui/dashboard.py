"""Farmer-friendly, high-contrast, accessible home dashboard for AgriSaathi AI."""

import base64
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, List
import streamlit as st
from core.database import get_db
from core.auth import AuthenticatedFarmer
from services.crop_service import CropService
from services.expense_service import ExpenseService
from services.harvest_service import HarvestService
from services.activity_service import ActivityService
from services.weather_service import WeatherService
from services.mandi_service import MandiService
from utils.formatting import format_inr, format_date
from utils.language import t, localize_unit, localize_weather_condition
from utils.logging_config import logger
from ui.state import get_language, set_page
from ui.theme import clean_html
from ui.components.crop_card import render_crop_tracker_card
from ui.components.weather_card import render_weather_widget
from ui.components.hero_3d import render_hero_3d_field
from ui.components.empty_state import render_empty_state
from ui.components.voice_button import render_voice_mic_button


COMMODITY_CHOICES = [
    {"en": "Cotton", "mr": "कापूस", "hi": "कपास"},
    {"en": "Soyabean", "mr": "सोयाबीन", "hi": "सोयाबीन"},
    {"en": "Wheat", "mr": "गहू", "hi": "गेहूं"},
    {"en": "Onion", "mr": "कांदा", "hi": "प्याज"},
    {"en": "Tomato", "mr": "टोमॅटो", "hi": "टमाटर"},
    {"en": "Gram", "mr": "हरभरा (चना)", "hi": "चना"},
    {"en": "Maize", "mr": "मका", "hi": "मक्का"},
]


@lru_cache(maxsize=1)
def get_hero_bg_data_uri() -> str:
    """Return base64 data URI for the cinematic Maharashtra crop field hero image."""
    bg_path = Path(__file__).resolve().parent.parent / "assets" / "hero_field_bg.jpg"
    if bg_path.exists():
        try:
            with open(bg_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
                return f"data:image/jpeg;base64,{b64}"
        except Exception as e:
            logger.warning("Failed to read hero background image: %s", e)
    return ""


def get_crop_icon(crop_name: str) -> str:
    """Return an agricultural emoji based on crop name."""
    name_low = (crop_name or "").lower()
    if any(k in name_low for k in ["cotton", "kapas", "कापूस", "कपास"]):
        return "⚪"
    if any(k in name_low for k in ["soybean", "soya", "सोयाबीन", "सोया"]):
        return "🌱"
    if any(k in name_low for k in ["wheat", "gehu", "गहू", "गेहूं"]):
        return "🌾"
    if any(k in name_low for k in ["rice", "paddy", "भात", "धान"]):
        return "🌾"
    if any(k in name_low for k in ["onion", "kanda", "कांदा", "प्याज"]):
        return "🧅"
    if any(k in name_low for k in ["tomato", "tamatar", "टोमॅटो", "टमाटर"]):
        return "🍅"
    if any(k in name_low for k in ["turmeric", "haldi", "हळद", "हल्दी"]):
        return "🌿"
    if any(k in name_low for k in ["maize", "corn", "मका", "मक्का"]):
        return "🌽"
    if any(k in name_low for k in ["sugarcane", "oos", "ऊस", "गन्ना"]):
        return "🎋"
    if any(k in name_low for k in ["gram", "chana", "हरभरा", "चना"]):
        return "🧆"
    return "🌾"


def get_stage_care_advice(growth_stage: str, lang: str = "mr") -> str:
    """Return grounded, actionable growth-stage care advice."""
    st_low = (growth_stage or "").lower()
    if any(w in st_low for w in ["flower", "फुलोरा", "फूल"]):
        return t("crop_care_flowering", lang)
    if any(w in st_low for w in ["pod", "fruit", "शेंग", "दाणे", "फल"]):
        return t("crop_care_pod", lang)
    if any(w in st_low for w in ["veg", "शाकीय", "वाढ"]):
        return t("crop_care_vegetative", lang)
    if any(w in st_low for w in ["matur", "harvest", "पक्व", "काढणी", "कटाई"]):
        return t("crop_care_maturity", lang)
    return t("crop_care_default", lang)


def render_dashboard(farmer: AuthenticatedFarmer):
    """Render the premium, farmer-first home dashboard."""
    lang = get_language()

    # ---------------- 0. DATA FETCHING (PRE-RENDER) ----------------
    recent_activities: List[Any] = []
    activities_load_error = False
    with get_db() as db:
        active_crops = CropService.list_crops(db, farmer.id, status="active")
        expense_summary = ExpenseService.get_expense_summary(db, farmer.id)
        harvest_summary = HarvestService.get_harvest_summary(db, farmer.id)
        try:
            recent_activities = ActivityService.list_activities(db, farmer.id, limit=3)
        except Exception as e:
            logger.exception("Failed to load recent activities for farmer ID %s: %s", farmer.id, e)
            activities_load_error = True

    total_area = sum(float(c.area or 0.0) for c in active_crops)
    tot_exp = expense_summary.get("total_expense", 0.0)
    tot_rev = harvest_summary.get("total_revenue", 0.0)
    net_prof = harvest_summary.get("net_profit", 0.0)

    state_query = farmer.state or "Maharashtra"
    dist_query = farmer.district or "Pune"
    weather_res = WeatherService.get_weather_forecast(state_query, dist_query)
    weather_curr = weather_res.get("current", {})
    weather_temp = weather_curr.get("temperature", "--")
    raw_cond = weather_curr.get("condition", "हवामान अनुकूल")
    weather_cond = localize_weather_condition(raw_cond, lang)

    hero_crop_name = active_crops[0].name if active_crops else "Cotton"
    hero_stage = active_crops[0].growth_stage if active_crops else "Flowering"

    # ---------------- 1. IMMERSIVE AGRICULTURAL HERO SECTION ----------------
    loc_parts = [p for p in [farmer.village, farmer.district, farmer.state] if p]
    loc_str = " • ".join(loc_parts) if loc_parts else f"{dist_query}, {state_query}"
    help_prompt = t("welcome_help_prompt", lang)

    crops_count_txt = f"{len(active_crops)} पिके सक्रिय" if lang == "mr" else (f"{len(active_crops)} फसलें सक्रिय" if lang == "hi" else f"{len(active_crops)} Active Crops")
    area_txt = f"{total_area:.1f} एकर क्षेत्र" if lang == "mr" else (f"{total_area:.1f} एकड़ क्षेत्र" if lang == "hi" else f"{total_area:.1f} Acres Sown")
    season_txt = "🌾 खरीप २०२६" if lang == "mr" else ("🌾 खरीफ २०२६" if lang == "hi" else "🌾 Kharif 2026")
    net_prof_str = f"नफा: ₹{net_prof:,.0f}" if net_prof >= 0 else f"तोटा: ₹{abs(net_prof):,.0f}"

    # Procedural 3D Farm Hero Banner with Three.js r128 and ambient lighting
    render_hero_3d_field(
        farmer_name=farmer.full_name,
        location_str=loc_str,
        season_str=season_txt,
        helper_text=help_prompt,
        crop_name=hero_crop_name,
        weather_condition=weather_cond,
        is_day=True,
        precipitation=weather_curr.get("precipitation", 0.0),
        height=275,
        lang=lang,
        summary_chips=[
            f"🌱 {crops_count_txt}",
            f"📐 {area_txt}",
            f"🌦️ {weather_temp}°C • {weather_cond}",
            f"⚖️ {net_prof_str}",
        ],
    )
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # ---------------- 2. WEATHER & SMART FARMING DUAL SECTION ----------------
    w_col1, w_col2 = st.columns([1, 1])
    with w_col1:
        # Animated Weather Card with live Spray Advisory Banner
        render_weather_widget(weather_res, district=dist_query, lang=lang)

    with w_col2:
        # ---------------- 2.1 TODAY'S SMART FARMING ADVICE CARD ----------------
        crop_tip = get_stage_care_advice(hero_stage, lang)
        advisory_title = "🌾 आजचा कृषी सल्ला" if lang == "mr" else ("🌾 आज की कृषि सलाह" if lang == "hi" else "🌾 Today's Smart Crop Advice")
        crop_name_loc = {
            "cotton": "कापूस", "wheat": "गहू", "soybean": "सोयाबीन", "onion": "कांदा", "tomato": "टोमॅटो", "gram": "हरभरा", "maize": "मका"
        }.get(hero_crop_name.lower(), hero_crop_name) if lang in ("mr", "hi") else hero_crop_name

        stage_loc = {
            "flowering": "फुलोरा अवस्था", "vegetative": "शाकीय वाढ", "sowing": "पेरणी", "pod": "शेंगा भरणे", "harvest": "काढणीस तयार"
        }.get(hero_stage.lower(), hero_stage) if lang == "mr" else ({
            "flowering": "फूल अवस्था", "vegetative": "बढ़वार", "sowing": "बुवाई", "pod": "फली लगना", "harvest": "कटाई योग्य"
        }.get(hero_stage.lower(), hero_stage) if lang == "hi" else hero_stage)

        advisory_html = clean_html(f"""
            <div class="tilt-card" style="
                background: linear-gradient(135deg, #ffffff 0%, #fffdf5 60%, #f4fbf5 100%);
                border: 1.5px solid #fcd34d;
                border-left: 6px solid #f59e0b;
                border-radius: 20px;
                padding: 22px 24px;
                margin-bottom: 18px;
                box-shadow: 0 4px 18px -2px rgba(245, 158, 11, 0.12);
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            ">
                <div>
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                        <span style="font-size: 2rem;">💡</span>
                        <h4 style="margin: 0; color: #92400e; font-size: 1.25rem; font-weight: 800;">
                            {advisory_title}
                        </h4>
                    </div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #166534; margin-bottom: 10px;">
                        🌱 {crop_name_loc} • {stage_loc}
                    </div>
                    <p style="margin: 0; color: #0b2316; font-size: 1.05rem; font-weight: 600; line-height: 1.55;">
                        {crop_tip}
                    </p>
                </div>
                <div style="margin-top: 14px; padding-top: 10px; border-top: 1px dashed #fcd34d; font-size: 0.85rem; color: #6d4c41; font-weight: 600;">
                    🌾 ICAR व वसंतराव नाईक मराठवाडा कृषी विद्यापीठ शिफारस
                </div>
            </div>
        """)
        st.markdown(advisory_html, unsafe_allow_html=True)

    # ---------------- 3. AI AGRICULTURAL ADVISOR SHOWCASE ----------------
    ai_header_html = clean_html(f"""
        <div style="
            background: linear-gradient(135deg, #ffffff 0%, #f4fbf5 100%);
            border: 1.5px solid #a5d6a7;
            border-radius: 22px;
            padding: 20px 24px;
            margin-bottom: 16px;
            box-shadow: 0 6px 20px rgba(15, 56, 34, 0.06);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        ">
            <div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.6rem;">🤖</span>
                    <h3 style="margin: 0; color: #0f3822; font-size: 1.35rem; font-weight: 800;">
                        {t('ai_search_title', lang)}
                    </h3>
                </div>
                <p style="margin: 4px 0 0 0; color: #374151; font-size: 0.98rem; font-weight: 500;">
                    {t('ai_search_subtitle', lang)}
                </p>
            </div>
            <span style="background: #e8f5e9; border: 1.5px solid #81c784; color: #166534; font-size: 0.82rem; font-weight: 800; padding: 5px 14px; border-radius: 16px; display: inline-flex; align-items: center; gap: 6px;">
                🟢 २४/७ ऑनलाईन कृषी सल्लागार
            </span>
        </div>
    """)
    st.markdown(ai_header_html, unsafe_allow_html=True)

    # Voice Mic Row for one-tap speech
    render_voice_mic_button(lang)

    # Typed Query Input & Search Button
    ai_in_col, ai_btn_col = st.columns([4, 1])
    with ai_in_col:
        typed_query = st.text_input(
            "AI Search",
            placeholder=t("ask_question_placeholder", lang),
            key="dash_typed_ai_query",
            label_visibility="collapsed",
        )
    with ai_btn_col:
        if st.button(t("btn_ask_ai_now", lang), key="dash_btn_submit_query", use_container_width=True, type="primary"):
            if typed_query and typed_query.strip():
                st.session_state["pending_ai_query"] = typed_query.strip()
                set_page("chat")
                st.rerun()

    # 4 Contextual Devanagari suggestion chips (56px touch target buttons)
    c_chip1, c_chip2, c_chip3, c_chip4 = st.columns(4)
    chips_data = [
        ("ai_chip_bollworm", c_chip1),
        ("ai_chip_soybean_fert", c_chip2),
        ("ai_chip_onion_blight", c_chip3),
        ("ai_chip_spray_today", c_chip4),
    ]
    for key_id, col in chips_data:
        chip_label = t(key_id, lang)
        with col:
            if st.button(chip_label, key=f"chip_btn_{key_id}", use_container_width=True):
                st.session_state["pending_ai_query"] = chip_label
                set_page("chat")
                st.rerun()

    st.markdown("<div style='margin-bottom: 28px;'></div>", unsafe_allow_html=True)

    # ---------------- 4. QUICK ACTION AGRITECH TILES (6 DISTINCT CARDS) ----------------
    st.markdown(f"<h3 style='color: #0f3822; font-size: 1.45rem; font-weight: 800; margin-bottom: 14px;'>⚡ {t('quick_actions', lang)}</h3>", unsafe_allow_html=True)

    qa_col1, qa_col2, qa_col3 = st.columns(3)

    # Card 1: Leaf Doctor & Disease Scanner
    with qa_col1:
        card1_html = clean_html(f"""
            <div class="agri-action-card" style="border-left: 5px solid #16a34a;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <span style="font-size: 2.2rem;">🔬</span>
                    <span class="agri-action-badge" style="background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0;">
                        AI रोग निदान
                    </span>
                </div>
                <h4 style="margin: 10px 0 4px 0; color: #0f3822; font-size: 1.18rem; font-weight: 800;">
                    {t('action_leaf_doctor_title', lang)}
                </h4>
                <p style="margin: 0 0 14px 0; color: #4b5563; font-size: 0.92rem; min-height: 40px; line-height: 1.35;">
                    {t('action_leaf_doctor_desc', lang)}
                </p>
            </div>
        """)
        st.markdown(card1_html, unsafe_allow_html=True)
        btn1_lbl = "📸 फोटो काढून रोग ओळखा" if lang == "mr" else ("📸 फोटो से रोग पहचानें" if lang == "hi" else "📸 Scan Plant Photo")
        if st.button(btn1_lbl, key="dash_action_btn_image", use_container_width=True):
            set_page("image")
            st.rerun()

    # Card 2: My Crops & Growth Tracker
    with qa_col2:
        crops_badge_txt = f"{len(active_crops)} पिके • {total_area:.1f} एकर" if lang == "mr" else f"{len(active_crops)} Crops • {total_area:.1f} Ac"
        card2_html = clean_html(f"""
            <div class="agri-action-card" style="border-left: 5px solid #2e7d32;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <span style="font-size: 2.2rem;">🌾</span>
                    <span class="agri-action-badge" style="background: #e8f5e9; color: #1b5e20; border: 1px solid #a5d6a7;">
                        {crops_badge_txt}
                    </span>
                </div>
                <h4 style="margin: 10px 0 4px 0; color: #0f3822; font-size: 1.18rem; font-weight: 800;">
                    {t('action_my_crops_title', lang)}
                </h4>
                <p style="margin: 0 0 14px 0; color: #4b5563; font-size: 0.92rem; min-height: 40px; line-height: 1.35;">
                    {t('action_my_crops_desc', lang)}
                </p>
            </div>
        """)
        st.markdown(card2_html, unsafe_allow_html=True)
        btn2_lbl = "🌾 माझी पिके व्यवस्थापित करा" if lang == "mr" else ("🌾 फसलें देखें व प्रबंधित करें" if lang == "hi" else "🌾 View & Manage Crops")
        if st.button(btn2_lbl, key="dash_action_btn_crops", use_container_width=True):
            set_page("crops")
            st.rerun()

    # Card 3: Mandi Rates & Net Returns
    with qa_col3:
        card3_html = clean_html(f"""
            <div class="agri-action-card" style="border-left: 5px solid #f59e0b;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <span style="font-size: 2.2rem;">💰</span>
                    <span class="agri-action-badge" style="background: #fffbeb; color: #92400e; border: 1px solid #fde68a;">
                        APMC थेट भाव
                    </span>
                </div>
                <h4 style="margin: 10px 0 4px 0; color: #0f3822; font-size: 1.18rem; font-weight: 800;">
                    {t('action_mandi_rates_title', lang)}
                </h4>
                <p style="margin: 0 0 14px 0; color: #4b5563; font-size: 0.92rem; min-height: 40px; line-height: 1.35;">
                    {t('action_mandi_rates_desc', lang)}
                </p>
            </div>
        """)
        st.markdown(card3_html, unsafe_allow_html=True)
        btn3_lbl = "📈 थेट APMC भाव व नफा पहा" if lang == "mr" else ("📈 लाइव मंडी भाव व मुनाफा देखें" if lang == "hi" else "📈 Check Live Mandi Rates")
        if st.button(btn3_lbl, key="dash_action_btn_market", use_container_width=True):
            set_page("market")
            st.rerun()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    qa_col4, qa_col5, qa_col6 = st.columns(3)

    # Card 4: Weather Forecast & Spray Guidance
    with qa_col4:
        weather_badge_txt = f"{weather_temp}°C • फवारणी सल्ला"
        card4_html = clean_html(f"""
            <div class="agri-action-card" style="border-left: 5px solid #0284c7;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <span style="font-size: 2.2rem;">🌦️</span>
                    <span class="agri-action-badge" style="background: #f0f9ff; color: #0369a1; border: 1px solid #bae6fd;">
                        {weather_badge_txt}
                    </span>
                </div>
                <h4 style="margin: 10px 0 4px 0; color: #0f3822; font-size: 1.18rem; font-weight: 800;">
                    {t('action_weather_info_title', lang)}
                </h4>
                <p style="margin: 0 0 14px 0; color: #4b5563; font-size: 0.92rem; min-height: 40px; line-height: 1.35;">
                    {t('action_weather_info_desc', lang)}
                </p>
            </div>
        """)
        st.markdown(card4_html, unsafe_allow_html=True)
        btn4_lbl = "🌦️ हवामान व फवारणी अंदाज" if lang == "mr" else ("🌦️ मौसम व छिड़काव पूर्वानुमान" if lang == "hi" else "🌦️ Weather & Spray Forecast")
        if st.button(btn4_lbl, key="dash_action_btn_weather", use_container_width=True):
            set_page("weather")
            st.rerun()

    # Card 5: Farm Diary & Expenses
    with qa_col5:
        exp_badge_txt = f"खर्च: ₹{tot_exp:,.0f}" if lang == "mr" else f"Exp: ₹{tot_exp:,.0f}"
        card5_html = clean_html(f"""
            <div class="agri-action-card" style="border-left: 5px solid #b45309;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <span style="font-size: 2.2rem;">📒</span>
                    <span class="agri-action-badge" style="background: #fffbeb; color: #92400e; border: 1px solid #fed7aa;">
                        {exp_badge_txt}
                    </span>
                </div>
                <h4 style="margin: 10px 0 4px 0; color: #0f3822; font-size: 1.18rem; font-weight: 800;">
                    {t('action_farm_expenses_title', lang)}
                </h4>
                <p style="margin: 0 0 14px 0; color: #4b5563; font-size: 0.92rem; min-height: 40px; line-height: 1.35;">
                    {t('action_farm_expenses_desc', lang)}
                </p>
            </div>
        """)
        st.markdown(card5_html, unsafe_allow_html=True)
        btn5_lbl = "💸 खर्च व उत्पन्न नोंदवा" if lang == "mr" else ("💸 खर्च व आय दर्ज करें" if lang == "hi" else "💸 Record Farm Expenses")
        if st.button(btn5_lbl, key="dash_action_btn_expenses", use_container_width=True):
            set_page("expenses")
            st.rerun()

    # Card 6: Government Schemes & Subsidies
    with qa_col6:
        card6_html = clean_html(f"""
            <div class="agri-action-card" style="border-left: 5px solid #4338ca;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <span style="font-size: 2.2rem;">🏛️</span>
                    <span class="agri-action-badge" style="background: #eef2ff; color: #3730a3; border: 1px solid #c7d2fe;">
                        PM-किसान व अनुदाने
                    </span>
                </div>
                <h4 style="margin: 10px 0 4px 0; color: #0f3822; font-size: 1.18rem; font-weight: 800;">
                    {t('action_govt_schemes_title', lang)}
                </h4>
                <p style="margin: 0 0 14px 0; color: #4b5563; font-size: 0.92rem; min-height: 40px; line-height: 1.35;">
                    {t('action_govt_schemes_desc', lang)}
                </p>
            </div>
        """)
        st.markdown(card6_html, unsafe_allow_html=True)
        btn6_lbl = "🏛️ शासकीय योजना व अनुदाने" if lang == "mr" else ("🏛️ सरकारी योजनाएं व सब्सिडी" if lang == "hi" else "🏛️ Govt Schemes & Subsidies")
        if st.button(btn6_lbl, key="dash_action_btn_schemes", use_container_width=True):
            set_page("schemes")
            st.rerun()

    st.markdown("<hr style='margin: 32px 0 26px 0; border: none; border-top: 1.5px solid #d4ebd9;' />", unsafe_allow_html=True)

    # ---------------- 5. MY CROPS SECTION (WITH 6-STAGE 3D TRACKER) ----------------
    crop_header_col1, crop_header_col2 = st.columns([3, 1])
    with crop_header_col1:
        st.markdown(f"<h3 style='color: #0f3822; font-size: 1.45rem; font-weight: 800; margin: 0;'>🌾 {t('action_my_crops_title', lang)} ({len(active_crops)})</h3>", unsafe_allow_html=True)
    with crop_header_col2:
        if st.button(f"➕ {t('add_crop', lang)}", key="dash_add_crop_top", use_container_width=True):
            set_page("crops")
            st.rerun()

    if not active_crops:
        if render_empty_state(
            icon="🌱",
            title=t("empty_crops_title", lang),
            description=t("empty_crops_desc", lang),
            button_text=t("empty_crops_btn", lang),
            button_key="dash_add_first_crop",
        ):
            set_page("crops")
            st.rerun()
    else:
        crop_cols = st.columns(min(len(active_crops), 2))
        for idx, c in enumerate(active_crops):
            col_target = crop_cols[idx % len(crop_cols)]
            with col_target:
                c_icon = get_crop_icon(c.name)
                care_tip = get_stage_care_advice(c.growth_stage, lang)
                if render_crop_tracker_card(c, c_icon, care_tip, lang=lang, on_click_key=f"dash_crop_btn_{c.id}"):
                    set_page("crop_detail", crop_id=c.id)
                    st.rerun()

    st.markdown("<hr style='margin: 32px 0 26px 0; border: none; border-top: 1.5px solid #d4ebd9;' />", unsafe_allow_html=True)

    # ---------------- 6. MANDI MARKET RATES PREVIEW ----------------
    st.markdown(f"<h3 style='color: #0f3822; font-size: 1.45rem; font-weight: 800; margin: 0;'>📊 {t('mandi_home_preview_title', lang)}</h3>", unsafe_allow_html=True)
    st.caption(t("mandi_home_preview_desc", lang))

    # Commodity selector
    comm_sel_title = "🌾 निवडा शेतमाल" if lang == "mr" else ("🌾 चुनें कृषि उपज" if lang == "hi" else "🌾 Select Commodity")
    sel_comm_idx = st.selectbox(
        comm_sel_title,
        options=list(range(len(COMMODITY_CHOICES))),
        format_func=lambda i: COMMODITY_CHOICES[i].get(lang, COMMODITY_CHOICES[i]["en"]),
        key="dash_mandi_preview_comm_select",
        label_visibility="collapsed",
    )
    chosen_comm = COMMODITY_CHOICES[sel_comm_idx]["en"]

    best_markets: List[Dict[str, Any]] = MandiService.get_best_markets(
        commodity=chosen_comm,
        farmer_district=farmer.district or "Pune",
        state=farmer.state or "Maharashtra",
        top_n=3,
    )

    if best_markets:
        m_cols = st.columns(min(len(best_markets), 3))
        for m_idx, m_rec in enumerate(best_markets[:3]):
            with m_cols[m_idx]:
                m_market = m_rec.get("market", "APMC Market")
                m_district = m_rec.get("district", farmer.district or "")
                m_modal = m_rec.get("modal_price", 0.0)
                m_dist_km = m_rec.get("distance_km", 0.0)
                m_net = m_rec.get("estimated_net_price", m_modal)

                is_top_market = (m_idx == 0)
                card_border = "#f59e0b" if is_top_market else "#d4ebd9"
                card_bg = "#fffdf5" if is_top_market else "#ffffff"
                medal = "🥇 " if is_top_market else ("🥈 " if m_idx == 1 else "🥉 ")

                mandi_card_html = clean_html(f"""
                    <div style="
                        background: {card_bg};
                        border: 1.5px solid {card_border};
                        border-radius: 18px;
                        padding: 18px;
                        margin-bottom: 12px;
                        box-shadow: 0 4px 14px rgba(15, 56, 34, 0.06);
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 0.82rem; font-weight: 800; color: #166534; background: #f0fdf4; padding: 3px 10px; border-radius: 12px; border: 1px solid #bbf7d0;">
                                {medal} Agmarknet
                            </span>
                            <span style="font-size: 0.85rem; color: #4b5563; font-weight: 600;">📍 {m_dist_km} {localize_unit('km', lang)}</span>
                        </div>
                        <h4 style="margin: 10px 0 2px 0; color: #0b2316; font-size: 1.25rem; font-weight: 800;">{m_market}</h4>
                        <div style="font-size: 0.9rem; color: #4b5563; margin-bottom: 8px;">{m_district}</div>
                        <div style="font-size: 1.45rem; font-weight: 800; color: #166534;">
                            ₹{m_modal:,.0f} <span style="font-size: 0.88rem; font-weight: 600;">/ {t('mandi_per_quintal', lang)}</span>
                        </div>
                        <div style="
                            background: {'#fef3c7' if is_top_market else '#f0fdf4'};
                            color: {'#92400e' if is_top_market else '#166534'};
                            font-size: 0.92rem;
                            font-weight: 800;
                            margin-top: 10px;
                            padding: 8px 10px;
                            border-radius: 10px;
                            text-align: center;
                            border: 1px solid {'#fde047' if is_top_market else '#bbf7d0'};
                        ">
                            💰 {t('mandi_net_price', lang)}: ₹{m_net:,.0f}
                        </div>
                    </div>
                """)
                st.markdown(mandi_card_html, unsafe_allow_html=True)

    if st.button(t("view_all_markets_btn", lang), key="dash_btn_view_all_mandi", use_container_width=True):
        set_page("market")
        st.rerun()

    st.markdown("<hr style='margin: 32px 0 26px 0; border: none; border-top: 1.5px solid #d4ebd9;' />", unsafe_allow_html=True)

    # ---------------- 7. FARM FINANCIAL OVERVIEW ----------------
    st.markdown(f"<h3 style='color: #0f3822; font-size: 1.45rem; font-weight: 800; margin: 0;'>💰 {t('finances_title', lang)}</h3>", unsafe_allow_html=True)

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        st.metric(
            label=f"💸 {t('farm_total_expense', lang)}",
            value=format_inr(tot_exp),
        )
    with f_col2:
        st.metric(
            label=f"💰 {t('crop_sales_income', lang)}",
            value=format_inr(tot_rev),
        )
    with f_col3:
        st.metric(
            label=f"⚖️ {t('total_profit_loss', lang)}",
            value=format_inr(net_prof),
            delta=t("profit_label", lang) if net_prof >= 0 else f"-{t('loss_label', lang)}",
        )

    if tot_exp == 0.0 and tot_rev == 0.0:
        st.markdown(
            clean_html(f"""
            <div style="background: #fff8e1; border: 2px dashed #ffe082; border-radius: 14px; padding: 14px 18px; margin: 12px 0; font-size: 0.98rem; color: #5d4037; font-weight: 600;">
                ℹ️ {t('empty_finances_friendly', lang)}
            </div>
            """),
            unsafe_allow_html=True,
        )

    fin_btn_col1, fin_btn_col2 = st.columns(2)
    with fin_btn_col1:
        if st.button(f"➕ {t('quick_add_expense', lang)}", key="dash_fin_add_exp", use_container_width=True):
            set_page("expenses")
            st.rerun()
    with fin_btn_col2:
        if st.button(t("action_harvest_sales_title", lang), key="dash_fin_view_harvest", use_container_width=True):
            set_page("harvest")
            st.rerun()

    # ---------------- 8. RECENT FARM DIARY ACTIVITIES ----------------
    st.markdown("<hr style='margin: 32px 0 26px 0; border: none; border-top: 1.5px solid #d4ebd9;' />", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #0f3822; font-size: 1.45rem; font-weight: 800; margin: 0;'>📅 {t('tab_diary', lang)} ({t('recent_entries', lang)})</h3>", unsafe_allow_html=True)

    if activities_load_error:
        err_msg = {
            "mr": "⚠️ शेती कृती लोड करताना अडचण आली. कृपया थोड्या वेळाने पुन्हा तपासा.",
            "hi": "⚠️ कृषि गतिविधियां लोड करते समय समस्या आई। कृपया थोड़ी देर बाद पुनः देखें।",
            "en": "⚠️ Recent farm activities could not be loaded at this time. Please try refreshing.",
        }.get(lang, "⚠️ Recent farm activities could not be loaded at this time.")
        st.warning(err_msg)
    elif recent_activities:
        for act in recent_activities:
            with st.container(border=True):
                act_d = format_date(act.activity_date)
                crop_label = f"[{act.crop.name}] " if act.crop else ""
                cost_lbl = f" • {t('tab_expenses', lang)}: {format_inr(act.cost)}" if act.cost else ""
                st.markdown(f"**{crop_label}{act.activity_type}** ({act_d}){cost_lbl}")
                if act.description:
                    st.caption(act.description[:120])
    else:
        empty_msg = {
            "mr": "अजून कोणतीही शेती कृती नोंदवलेली नाही. दैनंदिन कामांची नोंद ठेवण्यासाठी 'शेत रोजनिशी' वापरा.",
            "hi": "अभी तक कोई कृषि गतिविधि दर्ज नहीं की गई है। दैनिक कार्यों का रिकॉर्ड रखने के लिए 'फार्म डायरी' का उपयोग करें।",
            "en": "No farm activities recorded yet. Use the Farm Diary to track your daily field operations.",
        }.get(lang, "No farm activities recorded yet.")
        st.info(f"📝 {empty_msg}")
        if st.button(f"➕ {t('quick_log_activity', lang)}", key="dash_empty_act_btn", use_container_width=True):
            set_page("diary")
            st.rerun()
