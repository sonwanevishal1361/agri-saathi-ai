"""Tests for Phase 3 Reliability Enhancements:
- System health diagnostic check (/health)
- Mandi net return formula with market fee and loading charges
- Mandi stale-data cache fallback
- Schedulable refresh script execution
- Structured logging & Sentry initialization
"""

import json
from unittest.mock import patch
from core.health import check_system_health
from services.mandi_service import MandiService
from scripts.refresh_mandi import refresh_mandi_cache
from utils.logging_config import JsonLogFormatter, init_sentry
import logging


def test_system_health_check(db_session):
    """Verify check_system_health returns valid component health status."""
    health = check_system_health()
    assert health["status"] in ("healthy", "degraded")
    assert "database" in health["components"]
    assert health["components"]["database"]["status"] == "healthy"
    assert "latency_ms" in health["components"]["database"]
    assert "ai_provider" in health["components"]
    assert "disk" in health["components"]
    assert health["version"] is not None
    assert health["timestamp"] is not None


def test_mandi_net_return_formula():
    """Verify net return calculation with transport, market fee, and loading charges."""
    # Scenario:
    # Modal price: Rs 7000 / Qtl
    # Quantity: 10 Quintals
    # Distance: 100 km (transport rate: Rs 50/100km -> Rs 50/Qtl -> Rs 500 total)
    # Market fee (APMC cess): 1.5% of modal price -> 1.5% of 7000 = Rs 105/Qtl -> Rs 1050 total
    # Loading charges: Rs 20/Qtl -> Rs 200 total
    # Gross Revenue: 7000 * 10 = Rs 70,000
    # Total Deductions: 500 + 1050 + 200 = Rs 1750
    # Net Return: 70,000 - 1750 = Rs 68,250
    # Net Price per Qtl: 68,250 / 10 = Rs 6825

    calc = MandiService.calculate_net_return(
        modal_price=7000.0,
        quantity_quintals=10.0,
        distance_km=100.0,
        transport_rate_per_100km=50.0,
        market_fee_percent=1.5,
        loading_charge_per_qtl=20.0,
    )

    assert calc["gross_revenue"] == 70000.0
    assert calc["transport_cost"] == 500.0
    assert calc["transport_cost_per_qtl"] == 50.0
    assert calc["market_fee"] == 1050.0
    assert calc["market_fee_per_qtl"] == 105.0
    assert calc["loading_charges"] == 200.0
    assert calc["loading_charge_per_qtl"] == 20.0
    assert calc["total_deductions"] == 1750.0
    assert calc["net_return"] == 68250.0
    assert calc["net_price_per_qtl"] == 6825.0


def test_mandi_get_best_markets_with_extra_charges():
    """Verify get_best_markets incorporates market fee and loading charges."""
    markets = MandiService.get_best_markets(
        commodity="Soybean",
        farmer_district="Nagpur",
        state="Maharashtra",
        top_n=3,
        transport_cost_per_qtl_100km=50.0,
        market_fee_percent=1.0,
        loading_charge_per_qtl=15.0,
    )

    assert len(markets) > 0
    first = markets[0]
    assert "distance_km" in first
    assert "transport_cost_per_qtl" in first
    assert "market_fee_per_qtl" in first
    assert "loading_charge_per_qtl" in first
    assert "estimated_net_price" in first
    assert first["loading_charge_per_qtl"] == 15.0
    assert first["estimated_net_price"] < first["modal_price"]


def test_mandi_stale_cache_fallback(db_session):
    """Verify stale-data fallback when live API is unavailable."""
    cache_key = "mandi_test_stale_commodity_all_all_all"
    sample_payload = {
        "status": "success",
        "records": [
            {
                "commodity": "Test Crop",
                "market": "Test APMC",
                "modal_price": 4500.0,
                "district": "Pune",
                "state": "Maharashtra",
            }
        ],
        "count": 1,
    }

    # Save to cache
    MandiService._save_cache(cache_key, sample_payload)

    # Read from DB cache with allow_stale=True
    cached = MandiService._get_db_cache(cache_key, allow_stale=True)
    assert cached is not None
    assert cached["count"] == 1
    assert cached["records"][0]["commodity"] == "Test Crop"


def test_refresh_mandi_script_execution():
    """Verify schedulable refresh_mandi_cache executes and processes commodities."""
    with patch("services.mandi_service.MandiService.get_prices") as mock_get_prices:
        mock_get_prices.return_value = {
            "status": "success",
            "count": 4,
            "data_mode": "Mocked",
            "records": [],
        }

        total = refresh_mandi_cache(
            commodities=["Cotton (Kapas)", "Soybean"],
            state="Maharashtra",
            limit=10,
        )

        assert total == 8
        assert mock_get_prices.call_count == 2


def test_json_log_formatter():
    """Verify JsonLogFormatter produces valid JSON log records."""
    formatter = JsonLogFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_path.py",
        lineno=42,
        msg="Test log message with params: %s",
        args=("sample",),
        exc_info=None,
    )

    formatted = formatter.format(record)
    parsed = json.loads(formatted)
    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "test_logger"
    assert "Test log message with params: sample" in parsed["message"]
    assert "timestamp" in parsed


def test_init_sentry_without_dsn():
    """Verify init_sentry returns False gracefully when SENTRY_DSN is empty."""
    with patch.dict("os.environ", {"SENTRY_DSN": ""}):
        result = init_sentry()
        assert result is False
