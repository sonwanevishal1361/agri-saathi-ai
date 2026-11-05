#!/usr/bin/env python3
"""Diagnostic script to verify Data.gov.in Agmarknet Mandi API connectivity.

Safely checks API key configuration and executes a read probe.
NEVER exposes or logs secret API keys.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import get_data_gov_api_key, is_mandi_api_configured, redact  # noqa: E402
from services.mandi_api_client import (  # noqa: E402
    MandiApiClient,
    MandiAuthError,
    MandiRateLimitError,
    MandiTimeoutError,
    MandiNetworkError,
    MandiClientError,
)


def main():
    print("=" * 64)
    print("AgriSaathi AI — Data.gov.in Mandi API Verification Probe")
    print("=" * 64)

    is_configured = is_mandi_api_configured()
    if not is_configured:
        print("API Key Status: ⚠️ NOT CONFIGURED")
        print("Note: DATA_GOV_API_KEY was not found in Streamlit Secrets or Environment.")
        print("To configure, add DATA_GOV_API_KEY in:")
        print("  - Streamlit Cloud: App Settings -> Secrets")
        print("  - Local: .streamlit/secrets.toml or .env file")
        print("=" * 64)
        return 0

    api_key = get_data_gov_api_key()
    masked_key = redact(api_key)
    print(f"API Key Status: ✅ CONFIGURED (Key: {masked_key}, Length: {len(api_key)})")
    print("Target Resource: Current Daily Price of Various Commodities from Various Markets (Mandi)")
    print("Endpoint ID: 9ef84268-d588-465a-a308-a864a43d0070")
    print("\nExecuting live probe (State: Maharashtra, Limit: 5)...")

    client = MandiApiClient(timeout=15, max_retries=2)
    try:
        probe = client.verify_api_access(api_key=api_key, state="Maharashtra")
        status_code = probe.get("status_code", 200)
        record_count = probe.get("record_count", 0)
        sample = probe.get("sample_record")

        print(f"HTTP Response: {status_code} OK")
        print(f"Records Returned: {record_count}")

        if sample:
            print("\nSample Auction Arrival:")
            print(f"  • Market: {sample.get('market')} ({sample.get('district')}, {sample.get('state')})")
            print(f"  • Commodity: {sample.get('commodity')} ({sample.get('variety')})")
            print(f"  • Date: {sample.get('data_date')}")
            print(f"  • Modal Price: ₹{sample.get('modal_price')}/Quintal (Min: ₹{sample.get('min_price')}, Max: ₹{sample.get('max_price')})")

        print("\nAPI Connectivity Status: ✅ SUCCESSFUL (All checks passed)")
        print("=" * 64)
        return 0

    except MandiAuthError as e:
        print("HTTP Response: 401 / 403 Authentication Error")
        print(f"Error Details: {redact(str(e))}")
        print("API Connectivity Status: ❌ AUTHENTICATION FAILED")
        print("Please verify that your DATA_GOV_API_KEY is active on data.gov.in.")
        print("=" * 64)
        return 1

    except MandiRateLimitError as e:
        print("HTTP Response: 429 Too Many Requests")
        print(f"Error Details: {redact(str(e))}")
        print("API Connectivity Status: ⚠️ RATE LIMITED")
        print("The API key has exceeded the hourly/daily request threshold.")
        print("=" * 64)
        return 1

    except (MandiTimeoutError, MandiNetworkError) as e:
        print("HTTP Response: Network / Gateway Timeout")
        print(f"Error Details: {redact(str(e))}")
        print("API Connectivity Status: ⚠️ CONNECTION TIMEOUT")
        print("Government data.gov.in portal may be undergoing maintenance.")
        print("=" * 64)
        return 1

    except MandiClientError as e:
        print("HTTP Response: Bad Response")
        print(f"Error Details: {redact(str(e))}")
        print("API Connectivity Status: ❌ FAILED")
        print("=" * 64)
        return 1

    except Exception as e:
        print(f"Unexpected Exception: {redact(str(e))}")
        print("API Connectivity Status: ❌ UNEXPECTED ERROR")
        print("=" * 64)
        return 1


if __name__ == "__main__":
    sys.exit(main())
