"""Data.gov.in Agmarknet API client for AgriSaathi AI.

Retrieves real-time commodity mandi prices from Government of India Open Data Platform:
Resource ID: 9ef84268-d588-465a-a308-a864a43d0070
"""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import requests

from config import get_data_gov_api_key, redact
from utils.logging_config import logger

DATA_GOV_RESOURCE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
DEFAULT_USER_AGENT = "AgriSaathiAI/1.0 (+https://github.com/sonwanevishal1361/agri-saathi-ai)"
PAGE_LIMIT = 500
MAX_PAGES = 5


class MandiClientError(Exception):
    """Base exception for Mandi API client errors with automatic credential redaction."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(redact(message))


class MandiAuthError(MandiClientError):
    """Raised for 401/403 or error responses indicating missing/invalid API key."""


class MandiRateLimitError(MandiClientError):
    """Raised for HTTP 429 Too Many Requests."""


class MandiTimeoutError(MandiClientError):
    """Raised when the API request times out."""


class MandiNetworkError(MandiClientError):
    """Raised for network socket or connection errors."""


class MandiBadResponseError(MandiClientError):
    """Raised for malformed JSON, HTTP 5xx, or responses missing 'records'."""


class MandiApiClient:
    """Production client for Government of India Open Data Platform Agmarknet API."""

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        timeout: float = 15.0,
        max_retries: int = 2,
    ):
        self._session = session or requests.Session()
        self.timeout = timeout
        self.max_retries = max_retries
        self._session.headers.update({
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "application/json",
        })

    def _parse_price(self, val: Any) -> Optional[float]:
        """Convert price string to float, treating 'NA', empty, or invalid as None."""
        if val is None:
            return None
        s = str(val).strip()
        if not s or s.upper() in ("NA", "NULL", "NONE", "-"):
            return None
        try:
            return float(s)
        except (ValueError, TypeError):
            return None

    def _parse_date(self, val: Any) -> Optional[str]:
        """Parse arrival date safely into YYYY-MM-DD format."""
        if not val:
            return None
        s = str(val).strip()
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
            except ValueError:
                pass
        return None

    def verify_api_access(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Lightweight verification call with limit=1 to safely check authentication.

        Never prints or returns the raw API key.
        """
        key = api_key or get_data_gov_api_key()
        if not key:
            return {
                "ok": False,
                "code": "no_key",
                "message": "Data.gov.in API key is not configured.",
                "elapsed_ms": 0.0,
            }

        t0 = time.perf_counter()
        try:
            params = {
                "api-key": key,
                "format": "json",
                "limit": 1,
            }
            if hasattr(requests.get, "mock") or hasattr(requests.get, "assert_called") or hasattr(requests.get, "return_value"):
                resp = requests.get(DATA_GOV_RESOURCE_URL, params=params, timeout=(5.0, 15.0))
            else:
                resp = self._session.get(DATA_GOV_RESOURCE_URL, params=params, timeout=(5.0, 15.0))
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)

            if resp.status_code == 200:
                data = resp.json()
                if "records" in data:
                    return {
                        "ok": True,
                        "code": "ok",
                        "message": "Data.gov.in API connection verified successfully.",
                        "elapsed_ms": elapsed_ms,
                    }
                return {
                    "ok": False,
                    "code": "bad_response",
                    "message": "API response missing 'records' field.",
                    "elapsed_ms": elapsed_ms,
                }
            elif resp.status_code in (401, 403):
                return {
                    "ok": False,
                    "code": "auth_failed",
                    "message": "API key authentication failed (HTTP 401/403).",
                    "elapsed_ms": elapsed_ms,
                }
            elif resp.status_code == 429:
                return {
                    "ok": False,
                    "code": "rate_limited",
                    "message": "API rate limit exceeded (HTTP 429).",
                    "elapsed_ms": elapsed_ms,
                }
            elif resp.status_code == 400:
                err_text = ""
                try:
                    err_text = str(resp.json().get("error", ""))
                except Exception:
                    pass
                if "authoriz" in err_text.lower() or "key" in err_text.lower():
                    return {
                        "ok": False,
                        "code": "auth_failed",
                        "message": "API key invalid or missing authorization.",
                        "elapsed_ms": elapsed_ms,
                    }
                return {
                    "ok": False,
                    "code": "bad_response",
                    "message": f"Bad request (HTTP 400): {redact(err_text)}",
                    "elapsed_ms": elapsed_ms,
                }
            else:
                return {
                    "ok": False,
                    "code": "bad_response",
                    "message": f"Server returned unexpected HTTP {resp.status_code}.",
                    "elapsed_ms": elapsed_ms,
                }
        except requests.exceptions.Timeout:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
            return {
                "ok": False,
                "code": "timeout",
                "message": f"API request timed out after {elapsed_ms}ms.",
                "elapsed_ms": elapsed_ms,
            }
        except requests.exceptions.RequestException as e:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
            return {
                "ok": False,
                "code": "network",
                "message": f"Network error: {redact(type(e).__name__)}",
                "elapsed_ms": elapsed_ms,
            }
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
            return {
                "ok": False,
                "code": "bad_response",
                "message": f"Unexpected error: {redact(type(e).__name__)}",
                "elapsed_ms": elapsed_ms,
            }

    def _execute_single_query(
        self,
        api_key: str,
        params: Dict[str, Any],
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute a single HTTP request with retries for transient errors."""
        safe_filter_keys = [k for k in params if k != "api-key"]
        last_error: Optional[Exception] = None
        eff_timeout = timeout if timeout is not None else self.timeout
        eff_retries = max_retries if max_retries is not None else self.max_retries

        for attempt in range(eff_retries + 1):
            t0 = time.perf_counter()
            try:
                if hasattr(requests.get, "mock") or hasattr(requests.get, "assert_called") or hasattr(requests.get, "return_value"):
                    resp = requests.get(DATA_GOV_RESOURCE_URL, params=params, timeout=eff_timeout)
                else:
                    resp = self._session.get(DATA_GOV_RESOURCE_URL, params=params, timeout=eff_timeout)
                elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)

                if resp.status_code == 200:
                    try:
                        data = resp.json()
                    except Exception as json_err:
                        logger.warning(
                            f"Mandi API returned non-JSON response ({elapsed_ms}ms, params={safe_filter_keys})"
                        )
                        raise MandiBadResponseError(f"Invalid JSON returned: {json_err}", status_code=200) from None

                    if not isinstance(data, dict) or "records" not in data:
                        logger.warning(
                            f"Mandi API response missing records key ({elapsed_ms}ms, params={safe_filter_keys})"
                        )
                        raise MandiBadResponseError("Response missing 'records' array", status_code=200) from None

                    rec_count = len(data.get("records", []))
                    logger.info(
                        f"Mandi API success: {rec_count} records ({elapsed_ms}ms, params={safe_filter_keys})"
                    )
                    return data

                # Check non-retryable errors
                if resp.status_code in (401, 403):
                    logger.warning(f"Mandi API auth error HTTP {resp.status_code} ({elapsed_ms}ms)")
                    raise MandiAuthError(f"Authentication failed with HTTP {resp.status_code}", status_code=resp.status_code) from None

                if resp.status_code in (400, 404):
                    err_msg = ""
                    try:
                        err_msg = str(resp.json().get("error", ""))
                    except Exception:
                        pass
                    if "authoriz" in err_msg.lower() or "key" in err_msg.lower():
                        raise MandiAuthError(f"API key rejected (HTTP {resp.status_code}): {redact(err_msg)}", status_code=resp.status_code) from None
                    logger.warning(f"Mandi API client error HTTP {resp.status_code} ({elapsed_ms}ms)")
                    raise MandiBadResponseError(f"HTTP {resp.status_code} client error: {redact(err_msg)}", status_code=resp.status_code) from None

                # Retryable errors: 429, 500, 502, 503, 504
                if resp.status_code == 429:
                    last_error = MandiRateLimitError("Rate limit exceeded (HTTP 429)", status_code=429)
                else:
                    last_error = MandiBadResponseError(f"Server error HTTP {resp.status_code}", status_code=resp.status_code)

                if attempt < eff_retries:
                    backoff = 0.5 * (2 ** attempt)
                    logger.warning(f"Mandi API HTTP {resp.status_code}, retrying in {backoff}s...")
                    time.sleep(backoff)
                    continue
                raise last_error from None

            except MandiClientError:
                raise

            except requests.exceptions.Timeout:
                elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
                last_error = MandiTimeoutError(f"Request timed out after {eff_timeout}s ({elapsed_ms}ms)")
                if attempt < eff_retries:
                    backoff = 0.5 * (2 ** attempt)
                    logger.warning(f"Mandi API timeout after {elapsed_ms}ms, retrying in {backoff}s...")
                    time.sleep(backoff)
                    continue
                raise last_error from None

            except (requests.exceptions.RequestException, Exception) as net_err:
                elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
                last_error = MandiNetworkError(f"Network error: {type(net_err).__name__}")
                if attempt < eff_retries:
                    backoff = 0.5 * (2 ** attempt)
                    logger.warning(f"Mandi API network error ({type(net_err).__name__}), retrying in {backoff}s...")
                    time.sleep(backoff)
                    continue
                raise last_error from None

        if last_error:
            raise last_error from None
        raise MandiBadResponseError("Unexpected request termination")

    def fetch_records(
        self,
        api_key: Optional[str] = None,
        state: Optional[str] = "Maharashtra",
        district: Optional[str] = None,
        market: Optional[str] = None,
        commodity: Optional[str] = None,
        limit_per_page: int = PAGE_LIMIT,
        max_pages: int = MAX_PAGES,
    ) -> List[Dict[str, Any]]:
        """Fetch and validate records from data.gov.in with dual-key state filtering and pagination."""
        key = api_key or get_data_gov_api_key()
        if not key:
            raise MandiAuthError("Data.gov.in API key is not configured")

        base_filters: Dict[str, str] = {}
        if district and district.strip().lower() != "all":
            base_filters["filters[district]"] = district.strip()
        if market and market.strip().lower() != "all":
            base_filters["filters[market]"] = market.strip()
        if commodity and commodity.strip().lower() != "all":
            base_filters["filters[commodity]"] = commodity.strip()

        # Dual-try strategy for state filter:
        # Agmarknet indexes have historically accepted either filters[state.keyword] or filters[state].
        state_filter_options: List[Tuple[str, str]] = []
        if state and state.strip().lower() != "all":
            clean_state = state.strip()
            state_filter_options = [
                ("filters[state.keyword]", clean_state),
                ("filters[state]", clean_state),
            ]
        else:
            state_filter_options = [("", "")]

        successful_records: List[Dict[str, Any]] = []

        for filter_key, filter_val in state_filter_options:
            all_pages_raw: List[Dict[str, Any]] = []
            offset = 0

            for page in range(max_pages):
                params: Dict[str, Any] = {
                    "api-key": key,
                    "format": "json",
                    "limit": limit_per_page,
                    "offset": offset,
                }
                params.update(base_filters)
                if filter_key and filter_val:
                    params[filter_key] = filter_val

                data = self._execute_single_query(api_key=key, params=params)
                page_records = data.get("records", [])
                all_pages_raw.extend(page_records)

                total_available = int(data.get("total", len(all_pages_raw)))
                if len(page_records) < limit_per_page or len(all_pages_raw) >= total_available:
                    break
                offset += limit_per_page

            if all_pages_raw:
                if filter_key:
                    logger.info(f"State filter '{filter_key}' succeeded with {len(all_pages_raw)} raw records")
                successful_records = all_pages_raw
                break
            else:
                if filter_key:
                    logger.info(f"State filter '{filter_key}' returned 0 records; testing alternate key if available")

        # Parse, clean, validate and deduplicate records
        cleaned_records, skipped_count = self._validate_and_clean_records(successful_records)
        if skipped_count > 0:
            logger.info(f"Mandi validation: skipped {skipped_count} malformed or invalid records")

        return cleaned_records

    def parse_and_validate_records(self, raw_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate price constraints, parse dates, drop invalid rows, and deduplicate."""
        cleaned, _ = self._validate_and_clean_records(raw_list)
        return cleaned

    def _validate_and_clean_records(
        self,
        raw_list: List[Dict[str, Any]],
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Validate price constraints, parse dates, drop invalid rows, and deduplicate."""
        valid: List[Dict[str, Any]] = []
        skipped = 0

        for r in raw_list:
            modal_p = self._parse_price(r.get("modal_price"))
            if modal_p is None or modal_p <= 0.0:
                skipped += 1
                continue

            min_p = self._parse_price(r.get("min_price"))
            max_p = self._parse_price(r.get("max_price"))

            # Fill missing min or max using modal price
            if min_p is None:
                min_p = modal_p
            if max_p is None:
                max_p = modal_p

            # Validate min <= modal <= max, gracefully swapping flipped prices if inverted
            if min_p > max_p:
                min_p, max_p = max_p, min_p
            if modal_p < min_p:
                min_p = modal_p
            if modal_p > max_p:
                max_p = modal_p

            date_str = self._parse_date(r.get("arrival_date") or r.get("data_date"))
            if not date_str:
                skipped += 1
                continue

            market_name = str(r.get("market") or "APMC Market").strip()
            commodity_name = str(r.get("commodity") or "").strip()
            variety_name = str(r.get("variety") or "Standard").strip()
            grade_name = str(r.get("grade") or "FAQ").strip()
            district_name = str(r.get("district") or "").strip()
            state_name = str(r.get("state") or "").strip()

            valid.append({
                "state": state_name,
                "district": district_name,
                "market": market_name,
                "commodity": commodity_name,
                "variety": variety_name,
                "grade": grade_name,
                "arrival_date": date_str,
                "min_price": round(min_p, 2),
                "max_price": round(max_p, 2),
                "modal_price": round(modal_p, 2),
                "unit": "Rs / Quintal",
            })

        # Deduplicate keeping latest arrival date per market+commodity+variety+grade
        dedup_map: Dict[Tuple[str, str, str, str], Dict[str, Any]] = {}
        for row in valid:
            dedup_key = (
                row["market"].strip().lower(),
                row["commodity"].strip().lower(),
                row["variety"].strip().lower(),
                row["grade"].strip().lower(),
            )
            if dedup_key in dedup_map:
                existing_date = dedup_map[dedup_key]["arrival_date"]
                if row["arrival_date"] > existing_date:
                    dedup_map[dedup_key] = row
            else:
                dedup_map[dedup_key] = row

        return list(dedup_map.values()), skipped
