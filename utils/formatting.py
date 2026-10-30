"""Formatting helpers for currency, dates, and agricultural measurements."""

from datetime import date, datetime
from typing import Union


def format_inr(amount: Union[float, int, None]) -> str:
    """Format a monetary amount in Indian Rupees (INR) format (e.g. ₹ 1,50,000.00)."""
    if amount is None:
        return "₹ 0.00"

    try:
        val = float(amount)
    except (ValueError, TypeError):
        return "₹ 0.00"

    # Indian numbering format grouping
    is_negative = val < 0
    val = abs(val)
    parts = f"{val:.2f}".split(".")
    integer_part = parts[0]
    decimal_part = parts[1]

    if len(integer_part) > 3:
        last_three = integer_part[-3:]
        other_numbers = integer_part[:-3]
        # Group in pairs of 2
        res = ""
        while len(other_numbers) > 2:
            res = "," + other_numbers[-2:] + res
            other_numbers = other_numbers[:-2]
        formatted_int = other_numbers + res + "," + last_three
    else:
        formatted_int = integer_part

    sign = "-" if is_negative else ""
    return f"{sign}₹ {formatted_int}.{decimal_part}"


def format_date(dt: Union[date, datetime, str, None]) -> str:
    """Format date into standard human readable string."""
    if not dt:
        return "N/A"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt).date()
        except Exception:
            return dt
    if isinstance(dt, datetime):
        dt = dt.date()
    return dt.strftime("%d %b %Y")
