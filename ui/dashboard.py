"""Farmer-Friendly Home Dashboard for AgriSaathi AI."""

import streamlit as st
from core.database import get_db
from core.auth import AuthenticatedFarmer
from services.crop_service import CropService
from services.activity_service import ActivityService
from services.expense_service import ExpenseService
from services.harvest_service import HarvestService
from services.weather_service import WeatherService
from utils.formatting import format_inr, format_date
from utils.language import t
from ui.state import get_language, set_page


def render_dashboard(farmer: AuthenticatedFarmer):
    """Render high-contrast, accessible home dashboard for Indian farmers."""
    lang = get_language()

    # 1. Welcome Header
    loc_tag = f"📍 {farmer.village or ''}, {farmer.district or farmer.state or ''}".strip(", ")
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1b5e20, #2e7d32); color: white; padding: 18px 20px; border-radius: 14px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(27,94,32,0.15);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h2 style="margin: 0; color: #ffffff; font-size: 1.5rem; font-weight: 700;">🌱 {t('welcome', lang)}, {farmer.full_name}!</h2>
                    <p style="margin: 4px 0 0 0; color: #e8f5e9; font-size: 0.95rem; font-weight: 500;">
                        {loc_tag} • <em>{t('app_tagline', lang)}</em>
                    </p>
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

    with get_db() as db:
        active_crops = CropService.list_crops(db, farmer.id, status="active")
        recent_activities = ActivityService.list_activities(db, farmer.id, limit=4)
        expense_summary = ExpenseService.get_expense_summary(db, farmer.id)
        harvest_summary = HarvestService.get_harvest_summary(db, farmer.id)

    # 2. Onboarding Banner for first-time login
    if len(active_crops) == 0:
        st.markdown(
            f"""
            <div style="background: #fff8e1; border: 2px solid #ffe082; border-radius: 12px; padding: 16px; margin-bottom: 20px;">
                <h4 style="margin: 0 0 6px 0; color: #b78103;">👋 {t('onboarding_welcome', lang)}</h4>
                <p style="margin: 0; color: #5d4037; font-size: 0.95rem;">{t('onboarding_steps', lang)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 3. Live Weather & Spray Advisory Card
    state_query = farmer.state or "Maharashtra"
    dist_query = farmer.district or "Pune"
    weather_res = WeatherService.get_weather_forecast(state_query, dist_query)

    curr_weather = weather_res.get("current", {})
    temp = curr_weather.get("temperature", "--")
    condition = curr_weather.get("condition", "Partly cloudy")
    wind_spd = curr_weather.get("wind_speed", 0.0)
    precip = curr_weather.get("precipitation", 0.0)
    humidity = curr_weather.get("humidity", "--")

    # Evaluate spray suitability
    is_spray_warn = (wind_spd > 15.0) or (precip > 1.0)
    badge_label = t("spray_warn_badge", lang) if is_spray_warn else t("spray_ok_badge", lang)
    badge_cls = "spray-warn" if is_spray_warn else "spray-ok"
    badge_advice = t("spray_warn_advice", lang) if is_spray_warn else t("spray_ok_advice", lang)

    st.markdown(
        f"""
        <div style="background: #ffffff; border: 2px solid #c8e6c9; border-radius: 14px; padding: 18px; margin-bottom: 22px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px;">
                <div>
                    <span style="font-size: 0.9rem; font-weight: 700; color: #2e7d32; text-transform: uppercase;">
                        🌦️ {t('tab_weather', lang)} ({dist_query})
                    </span>
                    <h3 style="margin: 2px 0 0 0; color: #1b5e20;">{temp}°C • {condition}</h3>
                    <span style="color: #4b634b; font-size: 0.88rem;">💨 {t('weather_wind', lang)}: {wind_spd} km/h | 💧 {t('weather_humidity', lang)}: {humidity}% | 🌧️ {t('weather_rain', lang)}: {precip} mm</span>
                </div>
                <div>
                    <div class="weather-spray-badge {badge_cls}">
                        {badge_label}
                    </div>
                </div>
            </div>
            <div style="background: #f7faf7; border-left: 4px solid {'#e53935' if is_spray_warn else '#2e7d32'}; padding: 8px 12px; border-radius: 4px; font-size: 0.92rem; color: #1b3b1b;">
                💡 <strong>{t('agri_advisory', lang)}:</strong> {badge_advice}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4. Three Large Action Tiles (Ask AI, Scan Leaf, Mandi Prices)
    st.markdown(f"##### 🚀 {t('quick_actions', lang)}")
    t1, t2, t3 = st.columns(3)
    with t1:
        with st.container(border=True):
            st.markdown("### 🤖")
            st.markdown(f"**{t('tile_ask_ai_title', lang)}**")
            st.caption(t("tile_ask_ai_desc", lang))
            if st.button(t("btn_ask_ai_tile", lang), key="tile_btn_ai", use_container_width=True):
                set_page("chat")
                st.rerun()

    with t2:
        with st.container(border=True):
            st.markdown("### 🔬")
            st.markdown(f"**{t('tile_scan_leaf_title', lang)}**")
            st.caption(t("tile_scan_leaf_desc", lang))
            if st.button(t("btn_scan_tile", lang), key="tile_btn_scan", use_container_width=True):
                set_page("image")
                st.rerun()

    with t3:
        with st.container(border=True):
            st.markdown("### 📈")
            st.markdown(f"**{t('tile_mandi_title', lang)}**")
            st.caption(t("tile_mandi_desc", lang))
            if st.button(t("btn_mandi_tile", lang), key="tile_btn_mandi", use_container_width=True):
                set_page("market")
                st.rerun()

    # 5. Quick Add Buttons Row
    st.markdown("---")
    qa1, qa2, qa3 = st.columns(3)
    with qa1:
        if st.button(f"➕ {t('quick_add_expense', lang)}", key="btn_quick_expense", use_container_width=True):
            set_page("expenses")
            st.rerun()
    with qa2:
        if st.button(f"➕ {t('quick_add_diary', lang)}", key="btn_quick_diary", use_container_width=True):
            set_page("diary")
            st.rerun()
    with qa3:
        if st.button(f"➕ {t('add_crop', lang)}", key="btn_quick_crop", use_container_width=True):
            set_page("crops")
            st.rerun()

    # 6. Active Crops & Farm Status
    st.markdown("---")
    crop_col, fin_col = st.columns([3, 2])

    with crop_col:
        st.subheader(f"🌾 {t('tab_crops', lang)} ({len(active_crops)})")
        if not active_crops:
            st.markdown(
                f"""
                <div class="empty-state-box">
                    <div class="empty-state-icon">🌱</div>
                    <h4 style="margin: 0; color: #1b5e20;">{t('empty_crops_title', lang)}</h4>
                    <p style="color: #4b634b; font-size: 0.92rem; margin: 6px 0 16px 0;">{t('empty_crops_desc', lang)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(t("empty_crops_btn", lang), key="dash_add_first_crop", use_container_width=True):
                set_page("crops")
                st.rerun()
        else:
            for c in active_crops:
                with st.container(border=True):
                    c_info, c_action = st.columns([3, 1])
                    with c_info:
                        st.markdown(f"**{c.name}** ({c.variety or 'General'})")
                        st.caption(f"{t('crop_area_lbl', lang)}: **{c.area} {c.area_unit}** | {t('growth_stage_lbl', lang)}: **{c.growth_stage}** | {t('sowing_date_lbl', lang)}: {format_date(c.sowing_date)}")
                    with c_action:
                        if st.button(t("view_details", lang), key=f"dash_crop_{c.id}", use_container_width=True):
                            set_page("crop_detail", crop_id=c.id)
                            st.rerun()

    with fin_col:
        st.subheader(f"💰 {t('finances_title', lang)}")
        tot_exp = expense_summary.get("total_expense", 0.0)
        tot_rev = harvest_summary.get("total_revenue", 0.0)
        net_prof = harvest_summary.get("net_profit", 0.0)

        with st.container(border=True):
            st.metric(label=f"💸 {t('tab_expenses', lang)}", value=format_inr(tot_exp))
            st.metric(label=f"💰 {t('sales_revenue', lang)}", value=format_inr(tot_rev))
            st.metric(
                label=f"⚖️ {t('net_balance', lang)}",
                value=format_inr(net_prof),
                delta=t("profit_label", lang) if net_prof >= 0 else f"-{t('loss_label', lang)}",
            )
            if st.button(t("view_finances_btn", lang), key="dash_fin_btn", use_container_width=True):
                set_page("expenses")
                st.rerun()

    # 7. Recent Diary Activities
    if recent_activities:
        st.markdown("---")
        st.subheader(f"📅 {t('tab_diary', lang)} ({t('recent_entries', lang)})")
        for act in recent_activities:
            with st.container(border=True):
                act_d = format_date(act.activity_date)
                crop_label = f"[{act.crop.name}] " if act.crop else ""
                cost_lbl = f" • {t('tab_expenses', lang)}: {format_inr(act.cost)}" if act.cost else ""
                st.markdown(f"**{crop_label}{act.activity_type}** ({act_d}){cost_lbl}")
                if act.description:
                    st.caption(act.description[:100])
