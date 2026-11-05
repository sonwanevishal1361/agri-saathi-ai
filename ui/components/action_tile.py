"""6 Large Glass Action Tiles for AgriSaathi AI with 3D tilt and telemetry tags."""

from typing import Dict, Any, List, Optional
import streamlit as st
from utils.language import t
from ui.theme import clean_html
from ui.state import set_page


def render_action_grid(
    farmer_data: Optional[Dict[str, Any]] = None,
    lang: str = "mr",
):
    """Render the 6 primary agritech action cards in a responsive 3x2 grid."""
    farmer_data = farmer_data or {}
    crops_count = farmer_data.get("crops_count", 0)
    total_area = farmer_data.get("total_area", 0.0)
    weather_temp = farmer_data.get("weather_temp", "--")
    tot_exp = farmer_data.get("total_expense", 0.0)

    # 6 Primary Agritech Action Destinations
    action_tiles: List[Dict[str, Any]] = [
        {
            "id": "chat",
            "icon": "🤖",
            "title": t("nav_ask_ai", lang),
            "desc": t("action_ask_ai_desc", lang),
            "badge": "२४/७ ऑनलाईन" if lang == "mr" else ("२४/७ ऑनलाइन" if lang == "hi" else "24/7 Online"),
            "badge_color": "#166534",
            "badge_bg": "#f0fdf4",
            "border_accent": "#16a34a",
            "target": "chat",
            "btn_label": f"👉 {t('nav_ask_ai', lang)}",
        },
        {
            "id": "crops",
            "icon": "🌾",
            "title": t("nav_my_farm", lang),
            "desc": t("action_my_crops_desc", lang),
            "badge": f"{crops_count} पिके • {total_area:.1f} Ac" if lang == "mr" else f"{crops_count} Crops",
            "badge_color": "#1b5e20",
            "badge_bg": "#e8f5e9",
            "border_accent": "#2e7d32",
            "target": "crops",
            "btn_label": f"👉 {t('nav_my_farm', lang)}",
        },
        {
            "id": "market",
            "icon": "📈",
            "title": t("action_mandi_rates_title", lang),
            "desc": t("action_mandi_rates_desc", lang),
            "badge": "APMC थेट भाव" if lang == "mr" else "Live APMC",
            "badge_color": "#92400e",
            "badge_bg": "#fffbeb",
            "border_accent": "#f59e0b",
            "target": "market",
            "btn_label": f"👉 {t('action_mandi_rates_title', lang)}",
        },
        {
            "id": "expenses",
            "icon": "📒",
            "title": t("action_farm_expenses_title", lang),
            "desc": t("action_farm_expenses_desc", lang),
            "badge": f"₹{tot_exp:,.0f} खर्च" if lang == "mr" else f"₹{tot_exp:,.0f} Exp",
            "badge_color": "#b45309",
            "badge_bg": "#fff7ed",
            "border_accent": "#ea580c",
            "target": "expenses",
            "btn_label": f"👉 {t('action_farm_expenses_title', lang)}",
        },
        {
            "id": "schemes",
            "icon": "🏛️",
            "title": t("action_govt_schemes_title", lang),
            "desc": t("action_govt_schemes_desc", lang),
            "badge": "PM-किसान व अनुदाने" if lang == "mr" else "Subsidies",
            "badge_color": "#3730a3",
            "badge_bg": "#eef2ff",
            "border_accent": "#4338ca",
            "target": "schemes",
            "btn_label": f"👉 {t('action_govt_schemes_title', lang)}",
        },
        {
            "id": "weather",
            "icon": "🌦️",
            "title": t("action_weather_info_title", lang),
            "desc": t("action_weather_info_desc", lang),
            "badge": f"{weather_temp}°C • फवारणी सल्ला" if lang == "mr" else f"{weather_temp}°C Spray",
            "badge_color": "#0369a1",
            "badge_bg": "#f0f9ff",
            "border_accent": "#0284c7",
            "target": "weather",
            "btn_label": f"👉 {t('action_weather_info_title', lang)}",
        },
    ]

    st.markdown(
        clean_html(f"""
        <div style="margin: 24px 0 14px 0;">
            <h3 style="color: #0f3822; font-size: 1.4rem; font-weight: 800; margin: 0;">
                ⚡ {t('quick_actions', lang)}
            </h3>
        </div>
        """),
        unsafe_allow_html=True,
    )

    # 3x2 Grid
    row1_cols = st.columns(3)
    for idx, card in enumerate(action_tiles[:3]):
        with row1_cols[idx]:
            card_html = clean_html(f"""
                <div class="tilt-card" style="
                    background: #ffffff;
                    border: 1.5px solid #d4ebd9;
                    border-left: 5px solid {card['border_accent']};
                    border-radius: 20px;
                    padding: 18px 20px;
                    margin-bottom: 8px;
                    box-shadow: 0 4px 16px -2px rgba(15, 56, 34, 0.06);
                    transition: all 0.25s ease;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <span style="font-size: 2.2rem; line-height: 1;">{card['icon']}</span>
                        <span style="background: {card['badge_bg']}; color: {card['badge_color']}; font-size: 0.78rem; font-weight: 800; padding: 3px 10px; border-radius: 12px; border: 1px solid {card['border_accent']}40;">
                            {card['badge']}
                        </span>
                    </div>
                    <h4 style="margin: 10px 0 4px 0; color: #0f3822; font-size: 1.2rem; font-weight: 800;">
                        {card['title']}
                    </h4>
                    <p style="margin: 0; color: #4b5563; font-size: 0.92rem; line-height: 1.35; min-height: 38px;">
                        {card['desc']}
                    </p>
                </div>
            """)
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(card["btn_label"], key=f"action_grid_btn_{card['id']}", use_container_width=True):
                set_page(card["target"])
                st.rerun()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    row2_cols = st.columns(3)
    for idx, card in enumerate(action_tiles[3:]):
        with row2_cols[idx]:
            card_html = clean_html(f"""
                <div class="tilt-card" style="
                    background: #ffffff;
                    border: 1.5px solid #d4ebd9;
                    border-left: 5px solid {card['border_accent']};
                    border-radius: 20px;
                    padding: 18px 20px;
                    margin-bottom: 8px;
                    box-shadow: 0 4px 16px -2px rgba(15, 56, 34, 0.06);
                    transition: all 0.25s ease;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <span style="font-size: 2.2rem; line-height: 1;">{card['icon']}</span>
                        <span style="background: {card['badge_bg']}; color: {card['badge_color']}; font-size: 0.78rem; font-weight: 800; padding: 3px 10px; border-radius: 12px; border: 1px solid {card['border_accent']}40;">
                            {card['badge']}
                        </span>
                    </div>
                    <h4 style="margin: 10px 0 4px 0; color: #0f3822; font-size: 1.2rem; font-weight: 800;">
                        {card['title']}
                    </h4>
                    <p style="margin: 0; color: #4b5563; font-size: 0.92rem; line-height: 1.35; min-height: 38px;">
                        {card['desc']}
                    </p>
                </div>
            """)
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(card["btn_label"], key=f"action_grid_btn_{card['id']}", use_container_width=True):
                set_page(card["target"])
                st.rerun()

