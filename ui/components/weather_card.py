"""Animated, farmer-friendly weather card with live CSS animations, prominent spray advice, TTS audio, and 5-day forecast."""

import html
from typing import Dict, Any, List
import streamlit as st
from utils.language import t, localize_weather_condition, localize_unit
from ui.theme import clean_html
from ui.components.icons import get_icon


def render_weather_widget(weather_data: Dict[str, Any], district: str, lang: str = "mr"):
    """Render animated weather visual, giant spray advisory pill with TTS, and 5-day mini forecast."""
    curr = weather_data.get("current", {})
    temp = curr.get("temperature", "--")
    raw_condition = curr.get("condition", "Partly cloudy")
    localized_condition = localize_weather_condition(raw_condition, lang)
    wind_spd = float(curr.get("wind_speed") or 0.0)
    precip = float(curr.get("precipitation") or 0.0)
    humidity = curr.get("humidity", 55)

    try:
        humidity_num = float(humidity)
    except (ValueError, TypeError):
        humidity_num = 55.0

    # Determine Spray Suitability
    is_spray_warn = (wind_spd > 15.0) or (precip > 1.0)
    is_humid = humidity_num >= 75.0

    if is_spray_warn:
        banner_bg = "linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)"
        banner_border = "#f87171"
        banner_color = "#991b1b"
        banner_icon = "⚠️"
        pill_status = t("spray_warn_pill", lang)
        guidance = t("weather_rain_guidance", lang)
    elif is_humid:
        banner_bg = "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)"
        banner_border = "#86efac"
        banner_color = "#166534"
        banner_icon = "✅"
        pill_status = t("spray_ok_pill", lang)
        guidance = t("weather_humid_guidance", lang)
    else:
        banner_bg = "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)"
        banner_border = "#86efac"
        banner_color = "#166534"
        banner_icon = "✅"
        pill_status = t("spray_ok_pill", lang)
        guidance = t("weather_clear_guidance", lang)

    # CSS weather animation archetype
    cond_low = str(raw_condition).lower()
    is_rain = precip > 0.0 or any(w in cond_low for w in ["rain", "drizzle", "shower", "वादळ", "पाऊस"])
    is_cloudy = any(w in cond_low for w in ["cloud", "overcast", "ढगाळ", "धुके"])

    if is_rain:
        weather_anim_html = '<div class="anim-cloud rain-cloud"><div class="cloud-body"></div><div class="rain-drops"><span class="drop d1"></span><span class="drop d2"></span><span class="drop d3"></span></div></div>'
    elif is_cloudy:
        weather_anim_html = '<div class="anim-sun-cloud"><div class="sun-glow"></div><div class="cloud-float"></div></div>'
    else:
        weather_anim_html = '<div class="anim-sun"><div class="sun-core"></div><div class="sun-rays"></div></div>'

    wind_unit = localize_unit("km/h", lang)
    rain_unit = localize_unit("mm", lang)
    temp_unit = localize_unit("°C", lang)

    wind_icon = get_icon("wind", size=16, color="#4b5563")
    droplet_icon = get_icon("droplet", size=16, color="#0284c7")
    rain_icon = get_icon("cloud-rain", size=16, color="#0284c7")
    pin_icon = get_icon("map-pin", size=14, color="#166534")

    # Speech Synthesis TTS Setup
    speech_lang = "mr-IN" if lang == "mr" else ("hi-IN" if lang == "hi" else "en-IN")
    escaped_guidance = html.escape(f"{pill_status}. {guidance}").replace("'", "\\'")

    # 5-Day Mini Forecast Strip
    forecast_raw: List[Dict[str, Any]] = weather_data.get("forecast", [])[:5]
    forecast_items_html = ""
    if forecast_raw:
        forecast_items_html = '<div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid #e2ece4; display: grid; grid-template-columns: repeat(auto-fit, minmax(64px, 1fr)); gap: 8px;">'
        for f in forecast_raw:
            f_date = str(f.get("date", ""))[-5:]  # MM-DD
            f_cond = f.get("condition", "Clear")
            f_cond_low = f_cond.lower()
            f_max = f.get("temp_max", "--")
            f_icon = "🌧️" if "rain" in f_cond_low else ("⛅" if "cloud" in f_cond_low else "☀️")
            forecast_items_html += f"""
                <div style="background: #f8faf8; border: 1px solid #e2ece4; border-radius: 12px; padding: 6px 4px; text-align: center;">
                    <div style="font-size: 0.72rem; color: #6b7280; font-weight: 700;">{f_date}</div>
                    <div style="font-size: 1.25rem; margin: 2px 0;">{f_icon}</div>
                    <div style="font-size: 0.85rem; font-weight: 800; color: #0b2316;">{f_max}{temp_unit}</div>
                </div>
            """
        forecast_items_html += '</div>'

    html_content = clean_html(f"""
        <div class="agri-weather-box" style="
            background: #ffffff;
            border: 1.5px solid #d4ebd9;
            border-radius: 22px;
            padding: 20px 22px;
            margin-bottom: 20px;
            box-shadow: 0 8px 24px -4px rgba(15, 56, 34, 0.08);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        ">
            <!-- Header: Location & Temperature -->
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div style="width: 68px; height: 68px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                        {weather_anim_html}
                    </div>
                    <div>
                        <div style="display: flex; align-items: center; gap: 4px; font-size: 0.88rem; font-weight: 800; color: #166534; text-transform: uppercase; letter-spacing: 0.04em;">
                            {pin_icon} {district} • {localized_condition}
                        </div>
                        <div style="font-size: 2.8rem; font-weight: 900; color: #0b2316; line-height: 1.0; margin-top: 4px; letter-spacing: -0.02em;">
                            {temp}<span style="font-size: 1.5rem; font-weight: 700; color: #166534;">{temp_unit}</span>
                        </div>
                    </div>
                </div>
                <!-- 3 Metric Chips: Wind, Humidity, Rain -->
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <div style="background: #f8faf8; border: 1px solid #e2ece4; border-radius: 14px; padding: 8px 12px; text-align: center; min-width: 68px;">
                        <div style="display: flex; align-items: center; justify-content: center; gap: 4px; font-size: 0.74rem; color: #4b5563; font-weight: 700;">{wind_icon} {t('weather_wind', lang)}</div>
                        <div style="font-size: 1.02rem; font-weight: 800; color: #0b2316; margin-top: 2px;">{wind_spd} <span style="font-size: 0.72rem; color: #6b7280;">{wind_unit}</span></div>
                    </div>
                    <div style="background: #f8faf8; border: 1px solid #e2ece4; border-radius: 14px; padding: 8px 12px; text-align: center; min-width: 68px;">
                        <div style="display: flex; align-items: center; justify-content: center; gap: 4px; font-size: 0.74rem; color: #4b5563; font-weight: 700;">{droplet_icon} {t('weather_humidity', lang)}</div>
                        <div style="font-size: 1.02rem; font-weight: 800; color: #0b2316; margin-top: 2px;">{humidity}%</div>
                    </div>
                    <div style="background: #f8faf8; border: 1px solid #e2ece4; border-radius: 14px; padding: 8px 12px; text-align: center; min-width: 68px;">
                        <div style="display: flex; align-items: center; justify-content: center; gap: 4px; font-size: 0.74rem; color: #4b5563; font-weight: 700;">{rain_icon} {t('weather_rain', lang)}</div>
                        <div style="font-size: 1.02rem; font-weight: 800; color: #0b2316; margin-top: 2px;">{precip} <span style="font-size: 0.72rem; color: #6b7280;">{rain_unit}</span></div>
                    </div>
                </div>
            </div>

            <!-- Giant Spray Advisory Status Pill with Audio TTS -->
            <div style="
                background: {banner_bg};
                border: 2px solid {banner_border};
                color: {banner_color};
                border-radius: 18px;
                padding: 14px 18px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
                min-height: 56px;
                box-shadow: 0 4px 12px -2px rgba(0,0,0,0.04);
            ">
                <div style="display: flex; align-items: center; gap: 12px; flex-grow: 1;">
                    <span style="font-size: 1.6rem; flex-shrink: 0;">{banner_icon}</span>
                    <div>
                        <div style="font-size: 1.15rem; font-weight: 900; line-height: 1.2;">
                            {pill_status}
                        </div>
                        <div style="font-size: 0.95rem; font-weight: 600; margin-top: 3px; line-height: 1.4; color: #1f2a1f;">
                            {guidance}
                        </div>
                    </div>
                </div>
                <!-- Interactive Web Speech API Speaker Button -->
                <button
                    onclick="if('speechSynthesis' in window){{ window.speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance('{escaped_guidance}'); u.lang = '{speech_lang}'; u.rate = 0.92; window.speechSynthesis.speak(u); }}"
                    title="Audio Read Aloud"
                    style="
                        background: rgba(255,255,255,0.9);
                        border: 1.5px solid {banner_border};
                        border-radius: 14px;
                        color: {banner_color};
                        cursor: pointer;
                        font-weight: 800;
                        font-size: 0.85rem;
                        padding: 8px 12px;
                        display: inline-flex;
                        align-items: center;
                        gap: 6px;
                        white-space: nowrap;
                        flex-shrink: 0;
                        touch-action: manipulation;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
                    "
                >
                    🔊 {t('spray_read_aloud', lang)}
                </button>
            </div>

            <!-- 5-Day Mini Forecast Strip -->
            {forecast_items_html}
        </div>
    """)

    st.markdown(html_content, unsafe_allow_html=True)
