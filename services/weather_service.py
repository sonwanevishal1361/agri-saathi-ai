"""Weather service integrating Open-Meteo API for real-time agricultural forecasts."""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import requests
from utils.logging_config import logger

# WMO Weather interpretation codes (WW)
WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog and depositing rime fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm: Slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

# Coordinate mapping for prominent agricultural districts in India
INDIAN_DISTRICT_COORDINATES: Dict[str, Dict[str, Tuple[float, float]]] = {
    "Maharashtra": {
        "Pune": (18.5204, 73.8567),
        "Nashik": (19.9975, 73.7898),
        "Nagpur": (21.1458, 79.0882),
        "Chhatrapati Sambhajinagar (Aurangabad)": (19.8762, 75.3433),
        "Amravati": (20.9320, 77.7523),
        "Solapur": (17.6599, 75.9064),
        "Kolhapur": (16.7050, 74.2433),
        "Akola": (20.7002, 77.0082),
        "Yavatmal": (20.3888, 78.1204),
        "Satara": (17.6805, 74.0183),
        "Sangli": (16.8524, 74.5815),
        "Jalgaon": (21.0077, 75.5626),
        "Ahmednagar": (19.0952, 74.7480),
        "Nanded": (19.1383, 77.3210),
        "Latur": (18.4088, 76.5604),
        "Beed": (18.9891, 75.7601),
    },
    "Punjab": {
        "Ludhiana": (30.9010, 75.8573),
        "Amritsar": (31.6340, 74.8723),
        "Patiala": (30.3398, 76.3869),
        "Jalandhar": (31.3260, 75.5762),
        "Bathinda": (30.2110, 74.9455),
        "Sangrur": (30.2458, 75.8421),
    },
    "Uttar Pradesh": {
        "Lucknow": (26.8467, 80.9462),
        "Varanasi": (25.3176, 82.9739),
        "Kanpur": (26.4499, 80.3319),
        "Agra": (27.1767, 78.0081),
        "Prayagraj": (25.4358, 81.8463),
        "Meerut": (28.9845, 77.7064),
        "Bareilly": (28.3670, 79.4304),
        "Gorakhpur": (26.7606, 83.3732),
    },
    "Madhya Pradesh": {
        "Bhopal": (23.2599, 77.4126),
        "Indore": (22.7196, 75.8577),
        "Jabalpur": (23.1815, 79.9864),
        "Gwalior": (26.2183, 78.1828),
        "Ujjain": (23.1765, 75.7885),
        "Hoshangabad (Narmadapuram)": (22.7519, 77.7289),
        "Sehore": (23.2032, 77.0844),
    },
    "Gujarat": {
        "Ahmedabad": (23.0225, 72.5714),
        "Rajkot": (22.3039, 70.8022),
        "Surat": (21.1702, 72.8311),
        "Vadodara": (22.3072, 73.1812),
        "Junagadh": (21.5222, 70.4579),
        "Bhavnagar": (21.7645, 72.1519),
        "Mehsana": (23.5880, 72.3693),
    },
    "Karnataka": {
        "Bengaluru Rural": (13.2846, 77.4988),
        "Mysuru": (12.2958, 76.6394),
        "Belagavi": (15.8497, 74.4977),
        "Dharwad": (15.4589, 75.0078),
        "Shivamogga": (13.9299, 75.5681),
        "Kalaburagi": (17.3297, 76.8343),
    },
    "Telangana": {
        "Hyderabad": (17.3850, 78.4867),
        "Warangal": (17.9689, 79.5941),
        "Karimnagar": (18.4386, 79.1288),
        "Nizamabad": (18.6725, 78.0941),
        "Khammam": (17.2473, 80.1514),
    },
    "Andhra Pradesh": {
        "Guntur": (16.3067, 80.4365),
        "Vijayawada": (16.5062, 80.6480),
        "Kurnool": (15.8281, 78.0373),
        "Visakhapatnam": (17.6868, 83.2185),
        "Anantapur": (14.6819, 77.6006),
    },
    "Rajasthan": {
        "Jaipur": (26.9124, 75.7873),
        "Jodhpur": (26.2389, 73.0243),
        "Kota": (25.2138, 75.8648),
        "Sri Ganganagar": (29.9038, 73.8772),
        "Bikaner": (28.0229, 73.3119),
    },
    "Haryana": {
        "Karnal": (29.6857, 76.9905),
        "Hisar": (29.1492, 75.7217),
        "Ambala": (30.3782, 76.7767),
        "Rohtak": (28.8955, 76.6066),
    },
    "Bihar": {
        "Patna": (25.5941, 85.1376),
        "Muzaffarpur": (26.1209, 85.3647),
        "Bhagalpur": (25.2425, 86.9842),
        "Gaya": (24.7914, 85.0002),
    },
    "West Bengal": {
        "Kolkata": (22.5726, 88.3639),
        "Bardhaman": (23.2324, 87.8615),
        "Murshidabad": (24.1759, 88.2802),
        "Hooghly": (22.9030, 88.3968),
    },
    "Tamil Nadu": {
        "Coimbatore": (11.0168, 76.9558),
        "Madurai": (9.9252, 78.1198),
        "Thanjavur": (10.7870, 79.1378),
        "Salem": (11.6643, 78.1460),
    },
}


class WeatherService:

    @staticmethod
    def get_supported_states() -> List[str]:
        """Return list of supported Indian states."""
        return sorted(list(INDIAN_DISTRICT_COORDINATES.keys()))

    @staticmethod
    def get_districts_for_state(state: str) -> List[str]:
        """Return list of districts for a given state."""
        return sorted(list(INDIAN_DISTRICT_COORDINATES.get(state, {}).keys()))

    @staticmethod
    def get_coordinates(state: str, district: str) -> Optional[Tuple[float, float]]:
        """Lookup coordinates for state and district."""
        state_dict = INDIAN_DISTRICT_COORDINATES.get(state)
        if state_dict and district in state_dict:
            return state_dict[district]
        # Fallback to state capital or first district if available
        if state_dict:
            return next(iter(state_dict.values()))
        return (20.5937, 78.9629)  # Default center of India

    @staticmethod
    def get_weather_forecast(
        state: str,
        district: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Fetch live weather forecast from Open-Meteo API.

        Does not invent data. Returns structured payload with provider status and
        agricultural advisories stating operational uncertainty.
        """
        # Determine coordinates
        if latitude is None or longitude is None:
            coords = WeatherService.get_coordinates(state, district)
            if not coords:
                return {
                    "status": "unavailable",
                    "error": f"Coordinates not found for {district}, {state}.",
                    "source": "Open-Meteo",
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                }
            lat, lon = coords
        else:
            lat, lon = latitude, longitude

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
            "timezone": "auto",
            "forecast_days": 5,
        }

        try:
            resp = requests.get(url, params=params, timeout=8)
            if resp.status_code != 200:
                logger.warning(f"Open-Meteo returned status {resp.status_code}: {resp.text}")
                return {
                    "status": "unavailable",
                    "error": f"Weather service responded with error code {resp.status_code}.",
                    "source": "Open-Meteo (open-meteo.com)",
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                }

            data = resp.json()
            current = data.get("current", {})
            daily = data.get("daily", {})

            current_weather_code = current.get("weather_code", 0)
            current_condition = WMO_WEATHER_CODES.get(current_weather_code, "Partly Cloudy")

            # Parse daily forecast
            forecast_items = []
            dates = daily.get("time", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            precip_sums = daily.get("precipitation_sum", [])
            precip_probs = daily.get("precipitation_probability_max", [])
            codes = daily.get("weather_code", [])

            for i in range(len(dates)):
                w_code = codes[i] if i < len(codes) else 0
                forecast_items.append({
                    "date": dates[i],
                    "condition": WMO_WEATHER_CODES.get(w_code, "Clear"),
                    "temp_max": max_temps[i] if i < len(max_temps) else None,
                    "temp_min": min_temps[i] if i < len(min_temps) else None,
                    "precipitation_mm": precip_sums[i] if i < len(precip_sums) else 0.0,
                    "precipitation_probability": precip_probs[i] if i < len(precip_probs) else None,
                })

            # Derive actionable farming advice based on precipitation & temperature
            advice = WeatherService._generate_farming_advice(current, forecast_items)

            return {
                "status": "success",
                "location": {
                    "state": state,
                    "district": district,
                    "latitude": lat,
                    "longitude": lon,
                },
                "current": {
                    "temperature": current.get("temperature_2m"),
                    "humidity": current.get("relative_humidity_2m"),
                    "apparent_temperature": current.get("apparent_temperature"),
                    "precipitation": current.get("precipitation"),
                    "wind_speed": current.get("wind_speed_10m"),
                    "condition": current_condition,
                    "weather_code": current_weather_code,
                },
                "forecast": forecast_items,
                "agricultural_advice": advice,
                "source": "Open-Meteo Weather API",
                "source_url": "https://open-meteo.com/",
                "retrieved_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API request failed: {e}")
            return {
                "status": "unavailable",
                "error": f"Network error contacting weather service: {str(e)}",
                "source": "Open-Meteo",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }

    @staticmethod
    def _generate_farming_advice(current: Dict[str, Any], forecast: List[Dict[str, Any]]) -> List[str]:
        """Generate cautious, weather-based farming advisories explicitly stating uncertainty."""
        notes = []
        # Check upcoming rain
        upcoming_rain = sum(item.get("precipitation_mm", 0.0) or 0.0 for item in forecast[:3])
        high_prob_rain = any((item.get("precipitation_probability") or 0) > 60 for item in forecast[:3])

        if upcoming_rain > 15.0 or high_prob_rain:
            notes.append(
                "Rain predicted in the next 48-72 hours. Note: Weather forecasts have inherent uncertainty. "
                "Consider postponing spraying of insecticides/fungicides and irrigation to avoid chemical runoff."
            )
            notes.append("Ensure proper drainage in low-lying crop fields to prevent waterlogging.")
        else:
            notes.append(
                "Dry weather expected over the next 3 days. Favorable conditions for intercultural operations "
                "and planned harvesting or pesticide application, subject to local field observations."
            )

        curr_temp = current.get("temperature_2m")
        if curr_temp and curr_temp > 38.0:
            notes.append(
                "High temperatures (>38°C) detected. Provide light, frequent evening irrigation to protect "
                "sensitive crops from heat stress."
            )
        elif curr_temp and curr_temp < 10.0:
            notes.append(
                "Low night temperatures detected. Monitor vegetable and orchard crops for cold injury or frost risk."
            )

        return notes
