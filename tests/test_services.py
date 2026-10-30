"""Tests for Weather, Mandi, and Government Schemes services."""

from unittest.mock import patch
from services.weather_service import WeatherService
from services.mandi_service import MandiService
from services.schemes_service import SchemesService


def test_weather_service_states_and_districts():
    states = WeatherService.get_supported_states()
    assert "Maharashtra" in states
    assert "Punjab" in states

    districts = WeatherService.get_districts_for_state("Maharashtra")
    assert "Pune" in districts
    assert "Nashik" in districts


def test_weather_service_structure_on_mocked_response():
    mock_payload = {
        "current": {
            "temperature_2m": 28.5,
            "relative_humidity_2m": 65,
            "apparent_temperature": 29.0,
            "precipitation": 0.0,
            "wind_speed_10m": 12.0,
            "weather_code": 1,
        },
        "daily": {
            "time": ["2026-10-29", "2026-10-30", "2026-10-31"],
            "temperature_2m_max": [31.0, 30.5, 30.0],
            "temperature_2m_min": [19.0, 18.5, 18.0],
            "precipitation_sum": [0.0, 0.0, 5.0],
            "precipitation_probability_max": [10, 20, 65],
            "weather_code": [1, 2, 61],
        },
    }

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_payload

        res = WeatherService.get_weather_forecast("Maharashtra", "Pune")
        assert res["status"] == "success"
        assert res["current"]["temperature"] == 28.5
        assert len(res["forecast"]) == 3
        assert len(res["agricultural_advice"]) >= 1


def test_mandi_service_benchmark_records():
    res = MandiService.get_mandi_prices(commodity="Cotton", state="Maharashtra")
    assert res["status"] == "success"
    assert res["count"] >= 1
    rec = res["records"][0]
    assert rec["commodity"] == "Cotton (Kapas)"
    assert rec["state"] == "Maharashtra"
    assert rec["unit"] == "Rs / Quintal"
    assert rec["modal_price"] > 0
    assert rec["is_sample_benchmark"] is True


def test_schemes_service_filtering():
    all_schemes = SchemesService.get_all_schemes()
    assert len(all_schemes) >= 5

    # Filter PM-Kisan
    kisan = SchemesService.filter_schemes(search="PM-KISAN")
    assert len(kisan) >= 1
    assert "pm-kisan" == kisan[0]["id"]
    assert "https://pmkisan.gov.in/" in kisan[0]["official_url"]

    # Filter by category
    insurance = SchemesService.filter_schemes(category="Crop Insurance")
    assert len(insurance) >= 1
    assert insurance[0]["id"] == "pmfby"
