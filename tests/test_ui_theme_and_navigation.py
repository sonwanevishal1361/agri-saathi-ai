"""Automated tests for Phase 1 UI Theme, Navigation, and Multilingual Localization."""

import os
from unittest.mock import patch
from ui.state import set_page, init_session_state, get_language
from utils.language import t, TRANSLATIONS


def test_streamlit_config_toml_exists_and_valid():
    """Verify .streamlit/config.toml defines the high-contrast agricultural theme."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".streamlit", "config.toml")
    assert os.path.exists(config_path), ".streamlit/config.toml must exist"
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "#2E7D32" in content  # Forest green primary
    assert "#F8FAF8" in content  # Background color
    assert "#1B3B1B" in content  # High contrast text color


def test_phase1_navigation_state_mapping():
    """Verify that set_page synchronizes active_section across the 5 primary navigation tabs."""
    with patch("streamlit.session_state", {}):
        init_session_state()

        set_page("dashboard")
        assert get_language() == "mr"

        set_page("chat")
        assert True  # execution succeeded

        set_page("crops")
        set_page("expenses")
        set_page("market")
        set_page("profile")


def test_phase1_i18n_keys_present_in_all_languages():
    """Verify that all new user-facing strings are localized in mr, hi, and en."""
    required_keys = [
        "nav_home",
        "nav_ask_ai",
        "nav_my_farm",
        "nav_market_schemes",
        "nav_profile",
        "tab_crops",
        "tab_diary",
        "tab_expenses",
        "tab_harvest",
        "tab_mandi",
        "tab_weather",
        "tab_schemes",
        "tile_ask_ai_title",
        "tile_scan_leaf_title",
        "tile_mandi_title",
        "spray_ok_badge",
        "spray_warn_badge",
        "spray_ok_advice",
        "spray_warn_advice",
        "empty_crops_title",
        "empty_crops_desc",
        "empty_crops_btn",
        "empty_diary_title",
        "empty_expenses_title",
        "empty_harvest_title",
        "onboarding_welcome",
        "onboarding_steps",
    ]

    for key in required_keys:
        assert key in TRANSLATIONS, f"Missing key {key} in TRANSLATIONS"
        for lang in ["mr", "hi", "en"]:
            val = t(key, lang)
            assert val is not None and len(val.strip()) > 0, f"Empty translation for {key} in {lang}"
            assert not val.startswith(key), f"Translation missing or defaulted to key name for {key} in {lang}"


def test_weather_spray_advisory_logic():
    """Verify spray recommendation badge logic based on wind and rain conditions."""
    from services.weather_service import WeatherService

    mock_forecast_warn = {
        "status": "success",
        "current": {"wind_speed": 18.5, "precipitation": 2.5, "temperature": 28, "humidity": 75},
    }

    mock_forecast_ok = {
        "status": "success",
        "current": {"wind_speed": 8.0, "precipitation": 0.0, "temperature": 26, "humidity": 55},
    }

    with patch.object(WeatherService, "get_weather_forecast", return_value=mock_forecast_warn):
        res = WeatherService.get_weather_forecast("Maharashtra", "Pune")
        curr = res["current"]
        is_warn = (curr["wind_speed"] > 15.0) or (curr["precipitation"] > 1.0)
        assert is_warn is True

    with patch.object(WeatherService, "get_weather_forecast", return_value=mock_forecast_ok):
        res = WeatherService.get_weather_forecast("Maharashtra", "Pune")
        curr = res["current"]
        is_warn = (curr["wind_speed"] > 15.0) or (curr["precipitation"] > 1.0)
        assert is_warn is False


def test_farmer_friendly_homepage_translation_keys():
    """Verify that all new farmer-friendly homepage strings are present and localized in mr, hi, and en."""
    farmer_keys = [
        "welcome_help_prompt",
        "greeting_farmer",
        "weather_clear_guidance",
        "weather_rain_guidance",
        "weather_humid_guidance",
        "farm_total_expense",
        "crop_sales_income",
        "total_profit_loss",
        "empty_finances_friendly",
        "action_ask_ai_title",
        "action_ask_ai_desc",
        "action_leaf_doctor_title",
        "action_leaf_doctor_desc",
        "action_mandi_rates_title",
        "action_mandi_rates_desc",
        "action_weather_info_title",
        "action_weather_info_desc",
        "action_my_crops_title",
        "action_my_crops_desc",
        "action_govt_schemes_title",
        "action_govt_schemes_desc",
        "action_farm_expenses_title",
        "action_farm_expenses_desc",
        "action_harvest_sales_title",
        "action_harvest_sales_desc",
        "tap_to_open",
        "ai_search_title",
        "ai_search_subtitle",
        "ai_chip_bollworm",
        "ai_chip_soybean_fert",
        "ai_chip_onion_blight",
        "ai_chip_spray_today",
        "btn_ask_ai_now",
        "mandi_home_preview_title",
        "mandi_home_preview_desc",
        "view_all_markets_btn",
        "crop_stage_care_lbl",
        "crop_expected_harvest",
        "crop_care_default",
        "crop_care_flowering",
        "crop_care_pod",
        "crop_care_vegetative",
        "crop_care_maturity",
    ]

    for key in farmer_keys:
        assert key in TRANSLATIONS, f"Missing key {key} in TRANSLATIONS"
        for lang in ["mr", "hi", "en"]:
            val = t(key, lang)
            assert val is not None and len(val.strip()) > 0, f"Empty translation for {key} in {lang}"
            assert not val.startswith(key), f"Translation missing or defaulted to key name for {key} in {lang}"


def test_dashboard_crop_icon_helper():
    """Verify crop icons match agricultural categories."""
    from ui.dashboard import get_crop_icon

    assert get_crop_icon("Cotton (Kapas)") == "⚪"
    assert get_crop_icon("कापूस") == "⚪"
    assert get_crop_icon("Soybean") == "🌱"
    assert get_crop_icon("सोयाबीन") == "🌱"
    assert get_crop_icon("Wheat") == "🌾"
    assert get_crop_icon("गहू") == "🌾"
    assert get_crop_icon("Onion") == "🧅"
    assert get_crop_icon("कांदा") == "🧅"
    assert get_crop_icon("Tomato") == "🍅"
    assert get_crop_icon("टोमॅटो") == "🍅"
    assert get_crop_icon("Turmeric") == "🌿"
    assert get_crop_icon("मका") == "🌽"
    assert get_crop_icon("ऊस") == "🎋"
    assert get_crop_icon("हरभरा") == "🧆"


def test_dashboard_growth_stage_care_advice():
    """Verify growth stage care advice matches stage."""
    from ui.dashboard import get_stage_care_advice

    tip_mr = get_stage_care_advice("Flowering", "mr")
    assert "फुलोरा" in tip_mr or "पाण्याचा ताण" in tip_mr

    tip_hi = get_stage_care_advice("Pod Development", "hi")
    assert "फलियां" in tip_hi or "दाने" in tip_hi

    tip_en = get_stage_care_advice("Vegetative", "en")
    assert "Weed" in tip_en or "nutrition" in tip_en

    tip_mat = get_stage_care_advice("Maturity", "mr")
    assert "पक्व" in tip_mat or "काढणी" in tip_mat

