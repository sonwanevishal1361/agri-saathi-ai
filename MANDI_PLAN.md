# MANDI_PLAN.md — Live Mandi Price Integration Architecture Plan

## 1. Executive Summary & Baseline Inspection
This document outlines the architecture for integrating live agricultural mandi prices from the Government of India Open Data Platform (**Data.gov.in Agmarknet Resource ID: `9ef84268-d588-465a-a308-a864a43d0070`**) into **AgriSaathi AI**.

---

## 2. Current Behavior & Existing Architecture

### 2.1 Current Mandi Service (`services/mandi_service.py`)
- **API Fetching**: Contains an internal method `_fetch_live_data_gov()` using `requests.get()` with `timeout=8`, no custom `User-Agent`, and only `filters[state]` (which often fails or times out against the NIC gateway).
- **Fallback Chain**:
  1. In-memory cache (`_in_memory_cache`, TTL 60m).
  2. Database cache (`mandi_price_cache` table).
  3. Static benchmark dataset (`BENCHMARK_MANDI_RECORDS`).
- **Data Provenance**: When the API key is absent or failing, it silently falls back to 25 hardcoded benchmark records dated `2026-10-30`. This violates the zero-invention requirement for live farmer queries.
- **Freshness**: Uses naive `datetime.now().date()` without Asia/Kolkata (IST) timezone awareness.

### 2.2 Models (`models/mandi_history.py`)
- `MandiPriceHistory`: Captures price snapshots with unique constraint on `("state", "district", "market", "commodity", "variety", "arrival_date")`. Completely additive and persistent.
- `MandiPriceCache`: Stores JSON blobs indexed by `cache_key` with `cached_at` and `expires_at`.

### 2.3 UI Pages
- `ui/market_page.py`: Interactive page with commodity selector, state selector, district filter, transport deductions, podium cards for top 3 markets, bar chart, and price trends.
- Displays `mandi_res.get('data_mode')` and notice banners.

### 2.4 Chat Service (`services/chat_service.py`)
- Currently lacks intent detection for mandi prices. Farmers asking *"कांदा भाव काय आहे?"* (What is the onion price?) receive general LLM advice without verified live numbers from Agmarknet.

### 2.5 Config Names in Use
- `DATA_GOV_API_KEY`: Pydantic field in `config.py`.
- `DATA_GOV_IN_API_KEY`: Backward-compatibility alias.
- `MANDI_CACHE_TTL_MINUTES`: Integer, default `60`.
- `MANDI_MAX_RECORDS`: Integer, default `100`.

---

## 3. Gaps Identified

| # | Gap Area | Issue Description | Mitigation |
|---|---|---|---|
| 1 | **Secret Precedence** | `_load_streamlit_secrets_into_env()` skipped keys already present in `os.environ` even if empty. | Enforce trimmed, non-empty precedence: `st.secrets` $\to$ `os.environ` $\to$ fallback alias. |
| 2 | **NIC Gateway Firewall** | Default `python-requests` User-Agent causes socket drop/`ReadTimeout` on `api.data.gov.in`. | Use `requests.Session` with custom `User-Agent: AgriSaathiAI/1.0 (+https://github.com/...)` and `Accept: application/json`. |
| 3 | **Filter Key Semantics** | Agmarknet uses `filters[state.keyword]` on newer indexes and `filters[state]` on older ones. | Implement dual-try filter logic (fallback from `state.keyword` to `state`). |
| 4 | **Key Leakage Risk** | `requests` exceptions or error payloads might include URL with query params `?api-key=...`. | Typed exceptions raised `from None` with mandatory `redact()` applied to all messages, logs, and URLs. |
| 5 | **Timezone Accuracy** | Midnight boundaries for "today" were computed using UTC/local time rather than Indian Standard Time. | Explicit `zoneinfo.ZoneInfo("Asia/Kolkata")` handling for arrival dates. |
| 6 | **Zero Invention** | When live prices for today are unavailable, the system should state that today's prices are not yet published and show the latest real date, rather than substituting sample numbers. | Return explicit `source: "live" \| "cache" \| "stale_cache" \| "unavailable"` and `status: "no_data"` without mock data in production paths. |
| 7 | **Chat Grounding** | Chat LLM can hallucinate market prices. | Deterministic Python interception of mandi price queries, injecting verified API records into Gemini context, with regex/numeric post-check and deterministic fallback. |

---

## 4. Exact Files to be Created or Modified

1. **`core/config.py` & `config.py`**:
   - Provide `core/config.py` re-export module.
   - Implement `get_data_gov_api_key()`, `is_mandi_api_configured()`, and `redact(text: str) -> str`.
   - Ensure strict precedence order for `st.secrets["DATA_GOV_API_KEY"]` $\to$ `env DATA_GOV_API_KEY` $\to$ `st.secrets["DATA_GOV_IN_API_KEY"]` $\to$ `env DATA_GOV_IN_API_KEY`.
2. **`.streamlit/secrets.toml.example`**:
   - Create template file with redacted placeholder comments. Ensure `.streamlit/secrets.toml` is in `.gitignore`.
3. **`services/mandi_api_client.py` (New File)**:
   - Dedicated Data.gov.in Agmarknet API client.
   - Typed exceptions: `MandiAuthError`, `MandiRateLimitError`, `MandiTimeoutError`, `MandiNetworkError`, `MandiBadResponseError`.
   - `requests.Session`, User-Agent, exponential backoff for 429/5xx, pagination up to 500 records per page (max 5 pages).
   - Safe verification method `verify_api_access()`.
4. **`services/mandi_service.py`**:
   - Extend `get_mandi_prices(state="Maharashtra", district=None, market=None, commodity=None)` to return a structured result object.
   - IST freshness classification: `"today"`, `"yesterday"`, `"recent"`, `"old"`.
   - Safe concurrent caching in `MandiPriceCache` and trend persistence in `MandiPriceHistory`.
   - Maintain full backward compatibility for existing callers (`calculate_net_return`, `get_best_markets`, `get_price_trend`).
5. **`ui/market_page.py`**:
   - Add freshness badge and data source caption.
   - Display farmer-friendly status messages without altering existing podium/chart UI.
6. **`utils/language.py`**:
   - Add localized strings for today not published, no data found, service unavailable, and showing cached data.
7. **`services/chat_service.py`**:
   - Detect mandi price intent in Marathi, Hindi, and English.
   - Fetch verified data in Python, inject into Gemini system prompt within a delimited block, verify price numbers in response, and provide deterministic fallback summary.
8. **`scripts/check_mandi_api.py` (New File)**:
   - Safe CLI script for the user to verify their Data.gov.in API key without exposing it.
9. **`tests/test_mandi_live_service.py` (New File)**:
   - Comprehensive unit test suite covering key precedence, API client parsing, error handling, redaction, secret leakage prevention, caching, and AI chat intent.
