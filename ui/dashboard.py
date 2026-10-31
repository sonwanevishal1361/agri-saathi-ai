"""Farmer-Friendly Home Dashboard for AgriSaathi AI (कृषी साथी AI).

Crafted with care to feel like an authentic, accessible agricultural companion
for Indian farmers (especially Maharashtra farmers).
"""

from typing import Dict, Any, List
import streamlit as st
from core.database import get_db
from core.auth import AuthenticatedFarmer
from services.crop_service import CropService
from services.activity_service import ActivityService
from services.expense_service import ExpenseService
from services.harvest_service import HarvestService
from services.weather_service import WeatherService
from services.mandi_service import MandiService
from utils.formatting import format_inr, format_date
from utils.language import t
from utils.logging_config import logger
from ui.state import get_language, set_page


COMMODITY_CHOICES = [
    {"id": "cotton", "en": "Cotton (Kapas)", "mr": "कापूस", "hi": "कपास"},
    {"id": "soybean", "en": "Soybean", "mr": "सोयाबीन", "hi": "सोयाबीन"},
    {"id": "onion", "en": "Onion", "mr": "कांदा", "hi": "प्याज"},
    {"id": "wheat", "en": "Wheat", "mr": "गहू", "hi": "गेहूं"},
    {"id": "gram", "en": "Gram (Chana)", "mr": "हरभरा (चना)", "hi": "चना"},
    {"id": "turmeric", "en": "Turmeric", "mr": "हळद", "hi": "हल्दी"},
]


def get_crop_icon(crop_name: str) -> str:
    """Return an agricultural emoji based on crop name."""
    name_low = (crop_name or "").lower()
    if any(k in name_low for k in ["cotton", "kapas", "कापूस", "कपास"]):
        return "⚪"
    if any(k in name_low for k in ["soybean", "soya", "सोयाबीन"]):
        return "🌱"
    if any(k in name_low for k in ["wheat", "gehu", "गहू", "गेहूं"]):
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


def get_stage_care_advice(growth_stage: str, lang: str) -> str:
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
    """Render the farmer-friendly home dashboard."""
    lang = get_language()

    # ---------------- 1. WELCOME HEADER SECTION ----------------
    greeting_word = t("greeting_farmer", lang)
    loc_parts = [p for p in [farmer.village, farmer.district, farmer.state] if p]
    loc_str = "📍 " + ", ".join(loc_parts) if loc_parts else f"📍 {farmer.district or farmer.state or 'महाराष्ट्र'}"
    help_prompt = t("welcome_help_prompt", lang)

    st.markdown(
        f"""
        <div class="farmer-welcome-banner">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h2 class="farmer-welcome-title">🌱 {greeting_word}, {farmer.full_name}! 🙏</h2>
                    <p class="farmer-welcome-sub">{help_prompt}</p>
                    <div style="margin-top: 10px; display: flex; flex-wrap: wrap; gap: 8px;">
                        <span class="farmer-badge-pill">{loc_str}</span>
                        <span class="farmer-badge-pill">🚜 {t('app_tagline', lang)}</span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span style="background: rgba(255,255,255,0.22); padding: 5px 12px; border-radius: 20px; font-size: 0.82rem; font-weight: 600; color: #ffffff; border: 1px solid rgba(255,255,255,0.35);">
                        👨‍💻 Architect: <strong>Vishal Sonwane</strong>
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Fetch farmer data
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

    # ---------------- 2. LIVE WEATHER & PRACTICAL FARMER GUIDANCE ----------------
    state_query = farmer.state or "Maharashtra"
    dist_query = farmer.district or "Pune"
    weather_res = WeatherService.get_weather_forecast(state_query, dist_query)

    curr_weather = weather_res.get("current", {})
    temp = curr_weather.get("temperature", "--")
    condition = curr_weather.get("condition", "Partly cloudy")
    wind_spd = float(curr_weather.get("wind_speed") or 0.0)
    precip = float(curr_weather.get("precipitation") or 0.0)
    humidity_val = curr_weather.get("humidity", 50)
    try:
        humidity_num = float(humidity_val)
    except (ValueError, TypeError):
        humidity_num = 50.0

    # Evaluate spray suitability & generate practical guidance
    is_spray_warn = (wind_spd > 15.0) or (precip > 1.0)
    is_humid = humidity_num >= 75.0

    if is_spray_warn:
        badge_label = t("spray_warn_badge", lang)
        badge_cls = "spray-warn"
        guidance_text = t("weather_rain_guidance", lang)
        guidance_cls = "warn"
    elif is_humid:
        badge_label = t("spray_ok_badge", lang)
        badge_cls = "spray-ok"
        guidance_text = t("weather_humid_guidance", lang)
        guidance_cls = "normal"
    else:
        badge_label = t("spray_ok_badge", lang)
        badge_cls = "spray-ok"
        guidance_text = t("weather_clear_guidance", lang)
        guidance_cls = "normal"

    st.markdown(
        f"""
        <div class="weather-farmer-card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px;">
                <div>
                    <span style="font-size: 0.92rem; font-weight: 700; color: #2e7d32; text-transform: uppercase;">
                        🌦️ {t('tab_weather', lang)} • {dist_query}
                    </span>
                    <h3 style="margin: 2px 0 0 0; color: #1b5e20; font-size: 1.55rem;">
                        {temp}°C • {condition}
                    </h3>
                    <div style="margin-top: 4px; color: #4b634b; font-size: 0.9rem; font-weight: 500;">
                        💨 {t('weather_wind', lang)}: <strong>{wind_spd} km/h</strong> &nbsp;|&nbsp;
                        💧 {t('weather_humidity', lang)}: <strong>{humidity_val}%</strong> &nbsp;|&nbsp;
                        🌧️ {t('weather_rain', lang)}: <strong>{precip} mm</strong>
                    </div>
                </div>
                <div>
                    <div class="weather-spray-badge {badge_cls}">
                        {badge_label}
                    </div>
                </div>
            </div>
            <div class="weather-guidance-box {guidance_cls}">
                {guidance_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------- 3. AI ASSISTANT SEARCH & ONE-TAP SUGGESTION CHIPS ----------------
    st.markdown(
        f"""
        <div class="ai-search-banner">
            <div style="margin-bottom: 10px;">
                <h4 style="margin: 0; color: #1b5e20; font-size: 1.25rem;">{t('ai_search_title', lang)}</h4>
                <p style="margin: 3px 0 0 0; color: #3e523e; font-size: 0.92rem;">{t('ai_search_subtitle', lang)}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

    # 4 One-tap suggestion chips
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

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # ---------------- 4. EIGHT QUICK ACTION TOUCH CARDS ----------------
    st.markdown(f"#### ⚡ {t('quick_actions', lang)}")

    action_cards = [
        {
            "icon": "🤖",
            "title": t("action_ask_ai_title", lang),
            "desc": t("action_ask_ai_desc", lang),
            "target": "chat",
            "key": "action_chat",
        },
        {
            "icon": "🌿",
            "title": t("action_leaf_doctor_title", lang),
            "desc": t("action_leaf_doctor_desc", lang),
            "target": "image",
            "key": "action_image",
        },
        {
            "icon": "💰",
            "title": t("action_mandi_rates_title", lang),
            "desc": t("action_mandi_rates_desc", lang),
            "target": "market",
            "key": "action_market",
        },
        {
            "icon": "🌦️",
            "title": t("action_weather_info_title", lang),
            "desc": t("action_weather_info_desc", lang),
            "target": "weather",
            "key": "action_weather",
        },
        {
            "icon": "🌾",
            "title": t("action_my_crops_title", lang),
            "desc": t("action_my_crops_desc", lang),
            "target": "crops",
            "key": "action_crops",
        },
        {
            "icon": "🏛️",
            "title": t("action_govt_schemes_title", lang),
            "desc": t("action_govt_schemes_desc", lang),
            "target": "schemes",
            "key": "action_schemes",
        },
        {
            "icon": "📒",
            "title": t("action_farm_expenses_title", lang),
            "desc": t("action_farm_expenses_desc", lang),
            "target": "expenses",
            "key": "action_expenses",
        },
        {
            "icon": "🚜",
            "title": t("action_harvest_sales_title", lang),
            "desc": t("action_harvest_sales_desc", lang),
            "target": "harvest",
            "key": "action_harvest",
        },
    ]

    # Render in 2 rows of 4 columns (responsive)
    row1 = action_cards[:4]
    row2 = action_cards[4:]

    cols_r1 = st.columns(4)
    for idx, card in enumerate(row1):
        with cols_r1[idx]:
            with st.container(border=True):
                st.markdown(f"<span class='action-card-icon'>{card['icon']}</span>", unsafe_allow_html=True)
                st.markdown(f"<p class='action-card-title'>{card['title']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='action-card-desc'>{card['desc']}</p>", unsafe_allow_html=True)
                if st.button(t("tap_to_open", lang), key=f"btn_act_{card['key']}", use_container_width=True):
                    set_page(card["target"])
                    st.rerun()

    cols_r2 = st.columns(4)
    for idx, card in enumerate(row2):
        with cols_r2[idx]:
            with st.container(border=True):
                st.markdown(f"<span class='action-card-icon'>{card['icon']}</span>", unsafe_allow_html=True)
                st.markdown(f"<p class='action-card-title'>{card['title']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='action-card-desc'>{card['desc']}</p>", unsafe_allow_html=True)
                if st.button(t("tap_to_open", lang), key=f"btn_act_{card['key']}", use_container_width=True):
                    set_page(card["target"])
                    st.rerun()

    st.markdown("<hr style='margin: 28px 0 24px 0; border: none; border-top: 1.5px solid #c8e6c9;' />", unsafe_allow_html=True)

    # ---------------- 5. MY CROPS SECTION ----------------
    crop_header_col1, crop_header_col2 = st.columns([3, 1])
    with crop_header_col1:
        st.subheader(f"🌾 {t('action_my_crops_title', lang)} ({len(active_crops)})")
    with crop_header_col2:
        if st.button(f"➕ {t('add_crop', lang)}", key="dash_add_crop_top", use_container_width=True):
            set_page("crops")
            st.rerun()

    if not active_crops:
        st.markdown(
            f"""
            <div class="empty-state-box">
                <div class="empty-state-icon">🌱</div>
                <h4 style="margin: 0; color: #1b5e20;">{t('empty_crops_title', lang)}</h4>
                <p style="color: #4b634b; font-size: 0.95rem; margin: 8px 0 16px 0;">{t('empty_crops_desc', lang)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(t("empty_crops_btn", lang), key="dash_add_first_crop", use_container_width=True, type="primary"):
            set_page("crops")
            st.rerun()
    else:
        crop_cols = st.columns(min(len(active_crops), 2))
        for idx, c in enumerate(active_crops):
            col_target = crop_cols[idx % len(crop_cols)]
            with col_target:
                c_icon = get_crop_icon(c.name)
                care_tip = get_stage_care_advice(c.growth_stage, lang)
                sow_date_str = format_date(c.sowing_date)
                harvest_date_str = format_date(c.expected_harvest_date) if c.expected_harvest_date else "--"

                st.markdown(
                    f"""
                    <div class="crop-farmer-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h4 style="margin: 0; color: #1b5e20;">{c_icon} {c.name}</h4>
                            <span style="background: #e8f5e9; color: #1b5e20; font-size: 0.8rem; font-weight: 700; padding: 3px 10px; border-radius: 12px; border: 1px solid #a5d6a7;">
                                {c.variety or 'Standard'}
                            </span>
                        </div>
                        <div style="font-size: 0.9rem; color: #3e523e; line-height: 1.5;">
                            📐 {t('crop_area_lbl', lang)}: <strong>{c.area} {c.area_unit}</strong><br>
                            🌱 {t('sowing_date_lbl', lang)}: <strong>{sow_date_str}</strong><br>
                            🌿 {t('growth_stage_lbl', lang)}: <strong>{c.growth_stage}</strong><br>
                            🌾 {t('crop_expected_harvest', lang)} <strong>{harvest_date_str}</strong>
                        </div>
                        <div class="crop-care-tip">
                            💡 <strong>{t('crop_stage_care_lbl', lang)}</strong> {care_tip}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(t("view_details", lang), key=f"dash_crop_btn_{c.id}", use_container_width=True):
                    set_page("crop_detail", crop_id=c.id)
                    st.rerun()

    st.markdown("<hr style='margin: 28px 0 24px 0; border: none; border-top: 1.5px solid #c8e6c9;' />", unsafe_allow_html=True)

    # ---------------- 6. MANDI MARKET RATES PREVIEW ----------------
    st.subheader(t("mandi_home_preview_title", lang))
    st.caption(t("mandi_home_preview_desc", lang))

    # Commodity selector
    sel_comm_idx = st.selectbox(
        "निवडा पीक (Select Commodity)",
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

                st.markdown(
                    f"""
                    <div class="crop-farmer-card" style="border-top: 4px solid #2e7d32;">
                        <span style="font-size: 0.78rem; font-weight: 700; color: #1b5e20; background: #e8f5e9; padding: 2px 8px; border-radius: 10px;">
                            🟢 Agmarknet
                        </span>
                        <h4 style="margin: 6px 0 4px 0; color: #1b5e20;">{m_market}</h4>
                        <div style="font-size: 0.85rem; color: #4b634b; margin-bottom: 8px;">📍 {m_district} ({m_dist_km} km)</div>
                        <div style="font-size: 1.35rem; font-weight: 700; color: #1b5e20;">
                            ₹{m_modal:,.0f} <span style="font-size: 0.85rem; font-weight: 500;">/ {t('mandi_per_quintal', lang)}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #2e7d32; font-weight: 600; margin-top: 4px;">
                            💰 {t('mandi_net_price', lang)}: ₹{m_net:,.0f}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if st.button(t("view_all_markets_btn", lang), key="dash_btn_view_all_mandi", use_container_width=True):
        set_page("market")
        st.rerun()

    st.markdown("<hr style='margin: 28px 0 24px 0; border: none; border-top: 1.5px solid #c8e6c9;' />", unsafe_allow_html=True)

    # ---------------- 7. FARM FINANCIAL SECTION ----------------
    st.subheader(f"💰 {t('finances_title', lang)}")

    tot_exp = expense_summary.get("total_expense", 0.0)
    tot_rev = harvest_summary.get("total_revenue", 0.0)
    net_prof = harvest_summary.get("net_profit", 0.0)

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
            f"""
            <div style="background: #fdfaf3; border: 1.5px dashed #ffe082; border-radius: 10px; padding: 12px 16px; margin: 12px 0; font-size: 0.92rem; color: #5d4037;">
                ℹ️ {t('empty_finances_friendly', lang)}
            </div>
            """,
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
    st.markdown("<hr style='margin: 28px 0 24px 0; border: none; border-top: 1.5px solid #c8e6c9;' />", unsafe_allow_html=True)
    st.subheader(f"📅 {t('tab_diary', lang)} ({t('recent_entries', lang)})")

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
                    st.caption(act.description[:100])
    else:
        empty_msg = {
            "mr": "अजून कोणतीही शेती कृती नोंदवलेली नाही. दैनंदिन कामांची नोंद ठेवण्यासाठी 'शेत रोजनिशी' वापरा.",
            "hi": "अभी तक कोई कृषि गतिविधि दर्ज नहीं की गई है। दैनिक कार्यों का रिकॉर्ड रखने के लिए 'फार्म डायरी' का उपयोग करें।",
            "en": "No farm activities recorded yet. Use the Farm Diary to track your daily field operations.",
        }.get(lang, "No farm activities recorded yet.")
        st.info(f"📝 {empty_msg}")
        if st.button(f"➕ {t('quick_log_activity', lang)}", key="dash_empty_act_btn"):
            set_page("diary")
            st.rerun()
