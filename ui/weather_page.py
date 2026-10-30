"""Weather Forecast and Agricultural Advisories UI page."""

import streamlit as st
from services.weather_service import WeatherService
from core.auth import AuthenticatedFarmer


def render_weather_page(farmer: AuthenticatedFarmer):
    """Render real-time weather forecasts and agricultural advisories."""
    st.title("🌦️ हवामान अंदाज व कृषी सल्ला (Weather & Advisory)")
    st.markdown("पिकांचे नुकसान टाळण्यासाठी Open-Meteo वर आधारित स्थानिक हवामान अंदाज.")

    states = WeatherService.get_supported_states()
    default_state_idx = states.index(farmer.state) if farmer.state in states else (states.index("Maharashtra") if "Maharashtra" in states else 0)

    c1, c2 = st.columns(2)
    with c1:
        sel_state = st.selectbox("📍 राज्य निवडा (State)", options=states, index=default_state_idx)
    with c2:
        districts = WeatherService.get_districts_for_state(sel_state)
        default_dist_idx = districts.index(farmer.district) if farmer.district in districts else 0
        sel_dist = st.selectbox("🏙️ जिल्हा निवडा (District)", options=districts, index=default_dist_idx)

    # Fetch live weather forecast
    with st.spinner("हवामान माहिती मिळवत आहे..."):
        weather_data = WeatherService.get_weather_forecast(sel_state, sel_dist)

    if weather_data.get("status") != "success":
        st.warning(f"⚠️ हवामान सेवा सध्या अनुपलब्ध आहे: {weather_data.get('error', 'सेवा प्रतिसाद देत नाही.')}")
        st.caption("कृपया इंटरनेट कनेक्शन तपासा किंवा काही वेळाने पुन्हा प्रयत्न करा.")
        return

    curr = weather_data.get("current", {})
    loc = weather_data.get("location", {})
    advisories = weather_data.get("agricultural_advice", [])
    forecast = weather_data.get("forecast", [])

    # Current Weather Display Card
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #e8f5e9, #c8e6c9); border: 1px solid #a5d6a7; border-radius: 12px; padding: 20px; margin-bottom: 25px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h3 style="color: #1b5e20; margin: 0;">📍 {loc.get('district')}, {loc.get('state')}</h3>
                    <p style="margin: 4px 0 0 0; color: #388e3c; font-size: 1.1rem; font-weight: 500;">
                        {curr.get('condition')}
                    </p>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 2.4rem; font-weight: bold; color: #1b5e20;">
                        {curr.get('temperature')}°C
                    </span>
                    <br>
                    <span style="color: #555; font-size: 0.9rem;">(जाणवणारे तापमान: {curr.get('apparent_temperature')}°C)</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 Weather Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("💧 आर्द्रता (Humidity)", f"{curr.get('humidity')}%")
    with m2:
        st.metric("🌧️ पाऊस (Precipitation)", f"{curr.get('precipitation')} mm")
    with m3:
        st.metric("💨 वाऱ्याचा वेग (Wind)", f"{curr.get('wind_speed')} km/h")
    with m4:
        st.metric("📡 डेटा स्रोत", "Open-Meteo")

    st.markdown("---")

    # Agricultural Advisories with Uncertainty Notice
    st.markdown("##### 🌾 हवामानावर आधारित कृषी सल्ला (Agricultural Advisory)")
    if advisories:
        for adv in advisories:
            st.info(f"💡 {adv}")
    else:
        st.write("सध्या हवामान सामान्य आहे. नेहमीच्या शेती कामांमध्ये कोणताही मोठा बदल करण्याची आवश्यकता नाही.")

    st.markdown("---")

    # 5-Day Forecast
    st.markdown("##### 📅 पुढील ५ दिवसांचा अंदाज (5-Day Forecast)")
    if forecast:
        f_cols = st.columns(len(forecast))
        for idx, item in enumerate(forecast):
            with f_cols[idx]:
                with st.container(border=True):
                    st.markdown(f"**{item.get('date')}**")
                    st.caption(f"{item.get('condition')}")
                    st.markdown(f"🔺 **{item.get('temp_max')}°C**")
                    st.markdown(f"🔻 {item.get('temp_min')}°C")
                    st.caption(f"🌧️ {item.get('precipitation_mm')} mm ({item.get('precipitation_probability') or 0}%)")

    st.caption(f"माहिती पुनर्प्राप्ती वेळ: {weather_data.get('retrieved_at')} | अधिकृत पोर्टल: [{weather_data.get('source')}]({weather_data.get('source_url')})")
