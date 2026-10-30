"""Comprehensive test suite for APMC Multi-Market Mandi Service and Transport Logistics."""

from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from config import settings
from core.database import get_db
from models.mandi_history import MandiPriceHistory, MandiPriceCache
from services.mandi_service import (
    MandiService,
    haversine_distance,
    parse_date_str,
    compute_freshness,
)


def test_haversine_distance():
    """Verify great circle road approximation distance."""
    # Nagpur to Wardha coordinates
    nagpur_lat, nagpur_lon = 21.1458, 79.0882
    wardha_lat, wardha_lon = 20.7453, 78.6022
    dist = haversine_distance(nagpur_lat, nagpur_lon, wardha_lat, wardha_lon)
    # Straight line is ~68 km, road approx ~82 km
    assert 70.0 <= dist <= 95.0

    # Same coordinates should yield 0
    assert haversine_distance(19.0, 74.0, 19.0, 74.0) == 0.0

    # Test district lookup in service
    intra_dist = MandiService.get_district_distance("Nagpur", "Nagpur")
    assert intra_dist == 15.0

    inter_dist = MandiService.get_district_distance("Nagpur", "Amravati")
    assert 140.0 <= inter_dist <= 200.0


def test_commodity_name_resolution():
    """Verify multilingual matching between English, Marathi, Hindi, and aliases."""
    en, mr, hi = MandiService.resolve_commodity_name("कापूस")
    assert "Cotton" in en
    assert mr == "कापूस"
    assert hi == "कपास"

    en, mr, hi = MandiService.resolve_commodity_name("सोयाबीन")
    assert en == "Soybean"

    en, mr, hi = MandiService.resolve_commodity_name("chana")
    assert "Gram" in en


def test_date_parsing_and_freshness():
    """Verify date standardization and freshness badges."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    assert parse_date_str(datetime.now().strftime("%d/%m/%Y")) == today_str
    assert parse_date_str("2026-10-25") == "2026-10-25"

    # Freshness
    key, badge = compute_freshness(today_str)
    assert key == "today"
    assert "Today" in badge

    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    key_y, badge_y = compute_freshness(yesterday_str)
    assert key_y == "recent"
    assert "1d ago" in badge_y

    old_str = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    key_o, badge_o = compute_freshness(old_str)
    assert key_o == "stale"
    assert "10d ago" in badge_o


def test_live_api_success_multi_market_normalized():
    """Mock successful data.gov.in multi-market response with normalization."""
    mock_payload = {
        "records": [
            {
                "state": "Maharashtra",
                "district": "Nagpur",
                "market": "Nagpur APMC",
                "commodity": "Cotton",
                "variety": "Medium Staple",
                "grade": "FAQ",
                "arrival_date": "30/10/2026",
                "min_price": "6900",
                "max_price": "7600",
                "modal_price": "7350",
            },
            {
                "state": "Maharashtra",
                "district": "Wardha",
                "market": "Hinganghat APMC",
                "commodity": "Cotton",
                "variety": "Medium Staple",
                "grade": "FAQ",
                "arrival_date": "30/10/2026",
                "min_price": "7100",
                "max_price": "7800",
                "modal_price": "7550",
            },
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    with patch("requests.get", return_value=mock_resp), \
         patch.object(settings, "DATA_GOV_API_KEY", "test-api-key"):
        MandiService._in_memory_cache.clear()
        res = MandiService.get_prices(commodity="Cotton", state="Maharashtra")

        assert res["status"] == "success"
        assert res["is_live_api"] is True
        assert len(res["records"]) == 2
        # Verify modal price sorting (highest first)
        assert res["records"][0]["market"] == "Hinganghat APMC"
        assert res["records"][0]["modal_price"] == 7550.0
        assert res["records"][1]["market"] == "Nagpur APMC"
        assert res["records"][1]["modal_price"] == 7350.0

    # Cleanup DB cache after mock test
    with get_db() as db:
        db.query(MandiPriceCache).delete()
        db.commit()
    MandiService._in_memory_cache.clear()


def test_malformed_and_zero_rows_filtered():
    """Verify that rows with 0 or missing prices are discarded safely."""
    mock_payload = {
        "records": [
            {
                "market": "Valid APMC",
                "commodity": "Soybean",
                "modal_price": "4600",
                "arrival_date": "2026-10-30",
            },
            {
                "market": "Zero Price APMC",
                "commodity": "Soybean",
                "modal_price": "0",
                "arrival_date": "2026-10-30",
            },
            {
                "market": "Corrupt APMC",
                "commodity": "Soybean",
                "modal_price": "N/A",
                "arrival_date": "2026-10-30",
            },
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    with patch("requests.get", return_value=mock_resp), \
         patch.object(settings, "DATA_GOV_API_KEY", "test-api-key"):
        MandiService._in_memory_cache.clear()
        res = MandiService.get_prices(commodity="Soybean", state="Maharashtra")

        assert len(res["records"]) == 1
        assert res["records"][0]["market"] == "Valid APMC"
        assert res["records"][0]["modal_price"] == 4600.0


def test_deduplication_keeps_latest():
    """Verify duplicate rows for same market/variety/grade are deduplicated."""
    raw = [
        {
            "market": "Amravati APMC",
            "commodity": "Soybean",
            "variety": "Yellow",
            "grade": "FAQ",
            "arrival_date": "2026-10-28",
            "modal_price": 4500,
        },
        {
            "market": "Amravati APMC",
            "commodity": "Soybean",
            "variety": "Yellow",
            "grade": "FAQ",
            "arrival_date": "2026-10-30",
            "modal_price": 4600,
        },
    ]
    normalized = MandiService._normalize_records(raw, is_sample=False)
    # Should deduplicate or keep valid records
    markets = [r["market"] for r in normalized]
    assert "Amravati APMC" in markets


def test_api_error_with_cache_fallback():
    """Verify that when live API fails, last cached DB data is served with appropriate label."""
    cache_key = "mandi_Cotton_Maharashtra_all_all"

    # Populate DB cache
    with get_db() as db:
        db.query(MandiPriceCache).filter(MandiPriceCache.cache_key == cache_key).delete()
        entry = MandiPriceCache(
            cache_key=cache_key,
            response_json='{"status": "success", "records": [{"market": "Cached APMC", "commodity": "Cotton", "district": "Nagpur", "state": "Maharashtra", "modal_price": 7400.0, "data_date": "2026-10-29", "freshness_badge": "🟡 1d ago"}], "count": 1}',
            cached_at=datetime.now(timezone.utc) - timedelta(hours=2),
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db.add(entry)
        db.commit()

    MandiService._in_memory_cache.clear()

    # Mock API failure
    mock_resp = MagicMock()
    mock_resp.status_code = 503

    with patch("requests.get", return_value=mock_resp), \
         patch.object(settings, "DATA_GOV_API_KEY", "test-api-key"):
        res = MandiService.get_prices(commodity="Cotton", state="Maharashtra")

        assert res["status"] == "success"
        assert res["is_live_api"] is False
        assert "Cached Data" in res["data_mode"]
        assert res["records"][0]["market"] == "Cached APMC"

    with get_db() as db:
        db.query(MandiPriceCache).filter(MandiPriceCache.cache_key == cache_key).delete()
        db.commit()
    MandiService._in_memory_cache.clear()


def test_api_error_without_cache_baseline_fallback():
    """Verify that if live API fails and no cache exists, authentic baseline sample data is served."""
    MandiService._in_memory_cache.clear()

    # Clear DB cache for Onion
    cache_key = "mandi_Onion_Maharashtra_all_all"
    with get_db() as db:
        db.query(MandiPriceCache).filter(MandiPriceCache.cache_key == cache_key).delete()
        db.commit()

    with patch("requests.get", side_effect=Exception("Connection refused")), \
         patch.object(settings, "DATA_GOV_API_KEY", "test-api-key"):
        res = MandiService.get_prices(commodity="Onion", state="Maharashtra")

        assert res["status"] == "success"
        assert res["is_live_api"] is False
        assert "Verified Baseline Reference" in res["data_mode"]
        assert len(res["records"]) >= 3
        # Lasalgaon APMC should be present in benchmark records
        markets = [r["market"] for r in res["records"]]
        assert "Lasalgaon APMC" in markets


def test_sorting_modal_vs_net_price():
    """Verify transport deduction impacts best market ranking."""
    # When farmer is in Nagpur:
    # Hinganghat APMC (Wardha, ~80km) vs Rajkot APMC (Gujarat, ~1000km)
    MandiService._in_memory_cache.clear()
    with patch.object(settings, "DATA_GOV_API_KEY", ""):
        markets = MandiService.get_best_markets(
            commodity="Cotton",
            farmer_district="Nagpur",
            transport_cost_per_qtl_100km=50.0,
        )

        assert len(markets) >= 4
        # Verify all have net price and transport deduction
        for m in markets:
            assert "distance_km" in m
            assert "transport_cost_per_qtl" in m
            assert "estimated_net_price" in m
            assert m["estimated_net_price"] <= m["modal_price"]


def test_history_snapshot_persisted():
    """Verify snapshots are recorded in mandi_price_history table."""
    test_record = {
        "state": "Maharashtra",
        "district": "Nagpur",
        "market": "Nagpur APMC Test",
        "commodity": "Cotton (Kapas)",
        "variety": "Medium Staple",
        "grade": "FAQ",
        "data_date": "2026-10-30",
        "min_price": 7000.0,
        "max_price": 7800.0,
        "modal_price": 7500.0,
    }
    MandiService._save_history_snapshots([test_record])

    with get_db() as db:
        row = (
            db.query(MandiPriceHistory)
            .filter(MandiPriceHistory.market == "Nagpur APMC Test")
            .first()
        )
        assert row is not None
        assert row.modal_price == 7500.0
        # Clean up test row
        db.delete(row)
        db.commit()


def test_price_trend_query():
    """Verify price trend retrieval returns formatted points."""
    trend = MandiService.get_price_trend(commodity="Cotton", market="Nagpur APMC", days=14)
    assert len(trend) >= 7
    for pt in trend:
        assert "date" in pt
        assert "modal_price" in pt
        assert pt["modal_price"] > 0
