"""Schedulable script to warm and refresh Mandi APMC prices in the background.

Fetches current Agmarknet rates for major agricultural commodities, updating both
the database cache (mandi_price_cache) and long-term price history (mandi_price_history).

Usage:
    python scripts/refresh_mandi.py
    python scripts/refresh_mandi.py --state Maharashtra --limit 50
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from services.mandi_service import MandiService  # noqa: E402
from utils.logging_config import logger  # noqa: E402

DEFAULT_COMMODITIES: List[str] = [
    "Cotton (Kapas)",
    "Soybean",
    "Onion",
    "Wheat",
    "Rice (Paddy)",
    "Gram (Chana)",
    "Tomato",
    "Maize",
    "Groundnut",
    "Pigeon Pea (Tur/Arhar)",
]


def refresh_mandi_cache(
    commodities: List[str] = None,
    state: str = "Maharashtra",
    limit: int = 50,
) -> int:
    """Iterate through given commodities and warm the Mandi database cache."""
    target_commodities = commodities or DEFAULT_COMMODITIES
    total_records = 0
    start_time = datetime.now(timezone.utc)

    print("=" * 65)
    print("  AgriSaathi AI: Mandi Price Cache & History Refresh Task")
    print("=" * 65)
    print(f" Timestamp  : {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f" State      : {state or 'All States'}")
    print(f" Commodities: {len(target_commodities)}")
    print("-" * 65)

    for comm in target_commodities:
        print(f"[*] Fetching prices for '{comm}' in {state}...")
        try:
            res = MandiService.get_prices(
                commodity=comm,
                state=state,
                limit=limit,
            )
            count = res.get("count", 0)
            mode = res.get("data_mode", "Unknown")
            total_records += count
            print(f"    -> Retrieved {count} records [{mode}]")
        except Exception as exc:
            logger.error(f"Error refreshing Mandi cache for '{comm}': {exc}")
            print(f"    [!] Error for '{comm}': {exc}")

    print("=" * 65)
    print(f" Refresh completed successfully. Total market records: {total_records}")
    print("=" * 65)
    logger.info(f"Mandi price cache refresh complete. {total_records} records processed.")
    return total_records


def main():
    parser = argparse.ArgumentParser(description="Refresh AgriSaathi Mandi Price Cache")
    parser.add_argument("--state", default="Maharashtra", help="State to query (default: Maharashtra)")
    parser.add_argument("--limit", type=int, default=50, help="Max records per query")
    parser.add_argument("--commodities", nargs="+", help="Specific commodity names to refresh")
    args = parser.parse_args()

    refresh_mandi_cache(
        commodities=args.commodities,
        state=args.state,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()

