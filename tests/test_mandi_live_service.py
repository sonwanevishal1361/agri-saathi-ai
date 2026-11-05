"""Comprehensive offline unit and integration tests for Data.gov.in Agmarknet integration.

Covers:
- API Key resolution hierarchy, sanitization, and whitespace/quote trimming
- MandiApiClient network handling, dual-try parameters, typed exceptions, validation
- MandiService multi-tier caching (in-memory, DB fresh, DB stale fallback)
- Zero-invention production guarantee
- Secret redaction and leak prevention across logs, prompts, and exceptions
- ChatService mandi intent detection (mr, hi, en), prompt grounding, and hallucination checks
"""

import os
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
import pytest

from config import (
    get_data_gov_api_key,
    redact,
    _clean_key,
    settings,
)
from core.database import get_db
from models.mandi_history import MandiPriceCache
from models.user import User
from services.mandi_api_client import (
    MandiApiClient,
    MandiAuthError,
    MandiRateLimitError,
    MandiTimeoutError,
)
from services.mandi_service import (
    MandiService,
    compute_freshness,
    IST,
)
from services.chat_service import (
    ChatService,
    detect_mandi_intent,
    build_mandi_summary_text,
    verify_mandi_reply_integrity,
)


# ==============================================================================
# 1. API KEY RESOLUTION & SANITIZATION TESTS
# ==============================================================================


def test_clean_key_strips_quotes_and_whitespace():
    """Verify that _clean_key trims quotes and trailing whitespace."""
    assert _clean_key('  "my_secret_key"  ') == "my_secret_key"
    assert _clean_key("  'my_secret_key'  ") == "my_secret_key"
    assert _clean_key("\n\tmy_secret_key\r\n") == "my_secret_key"
    assert _clean_key("   ") == ""
    assert _clean_key(None) == ""


def test_api_key_resolution_hierarchy():
    """Verify strict precedence: st.secrets DATA_GOV_API_KEY -> env DATA_GOV_API_KEY -> alias."""
    # Test env fallback
    with patch.dict(os.environ, {"DATA_GOV_API_KEY": "env_primary_key"}, clear=False):
        with patch("streamlit.secrets", {"DATA_GOV_API_KEY": "streamlit_primary_key"}):
            assert get_data_gov_api_key() == "streamlit_primary_key"

    with patch.dict(os.environ, {"DATA_GOV_API_KEY": "env_primary_key"}, clear=False):
        with patch("streamlit.secrets", {}):
            assert get_data_gov_api_key() == "env_primary_key"

    # Alias fallback
    with patch.dict(os.environ, {"DATA_GOV_API_KEY": "", "DATA_GOV_IN_API_KEY": "env_alias_key"}, clear=False):
        with patch("streamlit.secrets", {}):
            assert get_data_gov_api_key() == "env_alias_key"


def test_redact_masks_secret_key():
    """Verify redact() prevents key leakage in text."""
    test_key = "CONFIDENTIAL_KEY_999XYZ"
    with patch("config.get_data_gov_api_key", return_value=test_key):
        sample_url = f"https://api.data.gov.in/resource/123?api-key={test_key}&format=json"
        masked = redact(sample_url)
        assert test_key not in masked
        assert "***" in masked


# ==============================================================================
# 2. MANDI API CLIENT UNIT TESTS (OFFLINE MOCKED)
# ==============================================================================


def test_mandi_client_record_parsing_and_validation():
    """Verify parsing, date normalization, and validation rules."""
    client = MandiApiClient()
    raw = [
        {
            "state": "Maharashtra",
            "district": "Nagpur",
            "market": "Nagpur APMC",
            "commodity": "Cotton",
            "variety": "Medium Staple",
            "grade": "FAQ",
            "arrival_date": "29/10/2026",
            "min_price": "6800",
            "max_price": "7600",
            "modal_price": "7300",
        },
        # Row with min > max (should swap or adjust)
        {
            "state": "Maharashtra",
            "district": "Wardha",
            "market": "Hinganghat APMC",
            "commodity": "Cotton",
            "variety": "Medium Staple",
            "grade": "FAQ",
            "arrival_date": "2026-10-29",
            "min_price": "7800",
            "max_price": "7000",
            "modal_price": "7400",
        },
        # Corrupt / Zero row (should be dropped)
        {
            "state": "Maharashtra",
            "district": "Nagpur",
            "market": "Bad APMC",
            "commodity": "Cotton",
            "modal_price": "0",
        },
    ]

    cleaned, skipped = client._validate_and_clean_records(raw)
    assert len(cleaned) == 2
    assert skipped == 1

    r0 = cleaned[0]
    assert r0["arrival_date"] == "2026-10-29"
    assert r0["modal_price"] == 7300.0
    assert r0["min_price"] == 6800.0

    r1 = cleaned[1]
    assert r1["min_price"] <= r1["max_price"]


def test_mandi_client_deduplication():
    """Verify that multiple records for the same market, commodity, variety, and grade keep the latest date."""
    client = MandiApiClient()
    raw = [
        {
            "market": "Lasalgaon APMC",
            "commodity": "Onion",
            "variety": "Red",
            "grade": "FAQ",
            "arrival_date": "2026-10-25",
            "modal_price": "2400",
        },
        {
            "market": "Lasalgaon APMC",
            "commodity": "Onion",
            "variety": "Red",
            "grade": "FAQ",
            "arrival_date": "2026-10-30",
            "modal_price": "2850",
        },
    ]
    cleaned = client.parse_and_validate_records(raw)
    assert len(cleaned) == 1
    assert cleaned[0]["arrival_date"] == "2026-10-30"
    assert cleaned[0]["modal_price"] == 2850.0


def test_mandi_client_auth_error_not_retried():
    """Verify 401/403 triggers MandiAuthError without retries."""
    client = MandiApiClient(max_retries=3)
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Invalid API Key"

    with patch.object(client._session, "get", return_value=mock_resp) as mock_get:
        with pytest.raises(MandiAuthError):
            client.fetch_records(api_key="invalid_test_key", state="Maharashtra")
        # Ensure it failed immediately on first attempt without retrying
        assert mock_get.call_count == 1


def test_mandi_client_rate_limit_error():
    """Verify 429 triggers MandiRateLimitError."""
    client = MandiApiClient(max_retries=1)
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.text = "Rate Limit Exceeded"

    with patch.object(client._session, "get", return_value=mock_resp):
        with pytest.raises(MandiRateLimitError):
            client.fetch_records(api_key="valid_key", state="Maharashtra")


def test_mandi_client_timeout_and_network_retry():
    """Verify transient timeouts trigger retries and finally raise MandiTimeoutError."""
    client = MandiApiClient(max_retries=1, timeout=0.1)
    import requests

    with patch.object(client._session, "get", side_effect=requests.exceptions.Timeout("Read timeout")):
        with patch("time.sleep", return_value=None):
            with pytest.raises(MandiTimeoutError):
                client.fetch_records(api_key="valid_key", state="Maharashtra")


def test_mandi_client_dual_try_parameter_fallback():
    """Verify client tries filters[state.keyword] and falls back to filters[state] if empty."""
    client = MandiApiClient(max_retries=0)

    # First attempt with .keyword returns 0 records, second attempt with plain filter returns 2 records
    resp_empty = MagicMock(status_code=200, json=lambda: {"records": []})
    resp_success = MagicMock(
        status_code=200,
        json=lambda: {
            "records": [
                {
                    "market": "Pune APMC",
                    "commodity": "Wheat",
                    "modal_price": 2800,
                    "arrival_date": "2026-10-30",
                }
            ]
        },
    )

    with patch.object(client._session, "get", side_effect=[resp_empty, resp_success]) as mock_get:
        records = client.fetch_records(api_key="valid_key", state="Maharashtra", commodity="Wheat")
        assert len(records) == 1
        assert mock_get.call_count == 2


# ==============================================================================
# 3. MANDI SERVICE MULTI-TIER CACHING & STALE FALLBACK
# ==============================================================================


def test_mandi_service_stale_cache_fallback():
    """Verify fallback to stale DB cache when live API fails with network timeout."""
    cache_key = "mandi_Cotton_Maharashtra_all_all"

    # Insert a stale entry into DB
    with get_db() as db:
        db.query(MandiPriceCache).filter(MandiPriceCache.cache_key == cache_key).delete()
        entry = MandiPriceCache(
            cache_key=cache_key,
            response_json='{"status": "success", "records": [{"market": "Stale APMC", "commodity": "Cotton (Kapas)", "modal_price": 7200.0, "data_date": "2026-10-24"}], "latest_arrival_date": "2026-10-24"}',
            cached_at=datetime.now(timezone.utc) - timedelta(days=2),
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        db.add(entry)
        db.commit()

    MandiService._in_memory_cache.clear()

    # Simulate network timeout
    with patch("services.mandi_service.get_data_gov_api_key", return_value="fake_key"):
        client = MandiService.get_api_client()
        with patch.object(client, "fetch_records", side_effect=MandiTimeoutError("Gateway Timeout")):
            res = MandiService.get_mandi_prices(commodity="Cotton", state="Maharashtra")

            assert res["status"] == "success"
            assert res["source"] == "stale_cache"
            assert res["message_key"] == "mandi_showing_cached"
            assert "Cached Data" in res["data_mode"]
            assert len(res["records"]) == 1
            assert res["records"][0]["market"] == "Stale APMC"

    # Cleanup
    with get_db() as db:
        db.query(MandiPriceCache).filter(MandiPriceCache.cache_key == cache_key).delete()
        db.commit()


def test_mandi_service_zero_invention_in_production():
    """Verify that in production mode, when no data is returned, status is 'no_data' with zero synthetic benchmark rows."""
    MandiService._in_memory_cache.clear()

    with patch.object(settings, "APP_ENV", "production"):
        with patch("config.get_data_gov_api_key", return_value="valid_key"):
            client = MandiService.get_api_client()
            with patch.object(client, "fetch_records", return_value=[]):
                res = MandiService.get_mandi_prices(
                    commodity="RareCommodityNotPublished",
                    state="Maharashtra",
                    allow_benchmark=False,
                )

                assert res["status"] == "no_data"
                assert res["records"] == []
                assert res["count"] == 0
                assert res["message_key"] == "mandi_no_data_found"


def test_mandi_service_freshness_classification():
    """Verify IST-aligned freshness categories (today, recent, stale)."""
    today_str = datetime.now(IST).strftime("%Y-%m-%d")
    yesterday_str = (datetime.now(IST) - timedelta(days=1)).strftime("%Y-%m-%d")
    recent_str = (datetime.now(IST) - timedelta(days=3)).strftime("%Y-%m-%d")
    old_str = (datetime.now(IST) - timedelta(days=15)).strftime("%Y-%m-%d")

    k_today, b_today = compute_freshness(today_str)
    assert k_today == "today"
    assert "Today" in b_today

    k_yest, b_yest = compute_freshness(yesterday_str)
    assert k_yest == "recent"
    assert "1d ago" in b_yest

    k_recent, _ = compute_freshness(recent_str)
    assert k_recent == "recent"

    k_old, _ = compute_freshness(old_str)
    assert k_old == "stale"


# ==============================================================================
# 4. SECRET LEAK PREVENTION TESTS
# ==============================================================================


def test_secret_key_never_leaked_in_logs_or_prompts():
    """Verify that fake secret key is never leaked in system prompt, logs, or error responses."""
    secret = "SUPER_SECRET_TOKEN_ABC123456789"
    with patch("config.get_data_gov_api_key", return_value=secret):
        # 1. Check redact function
        assert secret not in redact(f"Querying URL with api-key={secret}")

        # 2. Check exception string
        err = MandiAuthError(f"HTTP 401 with token {secret}")
        assert secret not in redact(str(err))

        # 3. Check Chat grounding block
        mandi_intent = {"is_mandi": True, "commodity": "Cotton", "district": "Nagpur"}
        with patch("services.chat_service.detect_mandi_intent", return_value=mandi_intent):
            mock_res = {
                "source": "live",
                "latest_arrival_date": "2026-10-30",
                "records": [
                    {
                        "market": "Nagpur APMC",
                        "district": "Nagpur",
                        "variety": "Medium",
                        "data_date": "2026-10-30",
                        "min_price": 7000.0,
                        "max_price": 7800.0,
                        "modal_price": 7400.0,
                    }
                ],
            }
            with patch.object(MandiService, "get_mandi_prices", return_value=mock_res):
                # Ensure ChatService does not embed key in prompt
                with get_db() as db:
                    # Create temporary test conversation
                    user = db.query(User).first()
                    if user:
                        conv = ChatService.create_conversation(db, user.id, "Mandi Query")
                        ctx = ChatService.prepare_chat_context(
                            db,
                            user.id,
                            conv.id,
                            "कापूस भाव काय आहे?",
                            language="mr",
                        )
                        prompt_str = str(ctx["messages_payload"])
                        assert secret not in prompt_str


# ==============================================================================
# 5. CHAT AI MANDI INTENT & GROUNDING TESTS
# ==============================================================================


def test_detect_mandi_intent_multilingual():
    """Verify intent detector works in Marathi, Hindi, and English."""
    # Marathi
    i_mr = detect_mandi_intent("नागपूर बाजारात कापसाचा काय भाव आहे?")
    assert i_mr["is_mandi"] is True
    assert i_mr["commodity"] == "Cotton (Kapas)"
    assert i_mr["district"] == "Nagpur"

    i_mr2 = detect_mandi_intent("आजचे सोयाबीनचे दर काय आहेत?")
    assert i_mr2["is_mandi"] is True
    assert i_mr2["commodity"] == "Soybean"

    # Hindi
    i_hi = detect_mandi_intent("नासिक मंडी में प्याज का भाव क्या चल रहा है?")
    assert i_hi["is_mandi"] is True
    assert i_hi["commodity"] == "Onion"
    assert i_hi["district"] == "Nashik"

    # English
    i_en = detect_mandi_intent("What is the current wheat rate in Pune?")
    assert i_en["is_mandi"] is True
    assert i_en["commodity"] == "Wheat"
    assert i_en["district"] == "Pune"

    # Non-mandi query
    i_none = detect_mandi_intent("माझ्या कापूस पिकावर बोंडअळीचा प्रादुर्भाव झाला आहे, काय औषध मारावे?")
    assert i_none["is_mandi"] is False


def test_build_mandi_summary_text_table_format():
    """Verify deterministic fallback table generation."""
    sample_res = {
        "source": "live",
        "has_today_prices": True,
        "latest_arrival_date": "2026-10-30",
        "records": [
            {
                "market": "Nagpur APMC",
                "district": "Nagpur",
                "variety": "Medium",
                "min_price": 7000.0,
                "max_price": 7800.0,
                "modal_price": 7450.0,
            }
        ],
    }

    tbl_mr = build_mandi_summary_text(sample_res, language="mr")
    assert "कृषी उत्पन्न बाजार समिती" in tbl_mr
    assert "Nagpur APMC" in tbl_mr
    assert "7450" in tbl_mr

    tbl_hi = build_mandi_summary_text(sample_res, language="hi")
    assert "कृषि उपज मंडी समिति" in tbl_hi
    assert "7450" in tbl_hi

    tbl_en = build_mandi_summary_text(sample_res, language="en")
    assert "APMC Mandi Market Rates" in tbl_en
    assert "7450" in tbl_en


def test_verify_mandi_reply_integrity_catches_hallucinations():
    """Verify hallucination detector flags fabricated prices."""
    records = [
        {
            "market": "Nagpur APMC",
            "modal_price": 7300.0,
            "min_price": 6800.0,
            "max_price": 7650.0,
        }
    ]

    # Grounded reply with valid price
    grounded_reply = "नागपूर बाजार समितीमध्ये कापसाचा मॉडेल भाव ₹7,300 प्रति क्विंटल आहे."
    assert verify_mandi_reply_integrity(grounded_reply, records) is True

    # Hallucinated reply with fabricated astronomical price
    hallucinated_reply = "नागपूर बाजार समितीमध्ये कापसाचा भाव 18000 रुपये प्रति क्विंटल सुरू आहे."
    assert verify_mandi_reply_integrity(hallucinated_reply, records) is False
