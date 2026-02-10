"""
Utility helpers for the CityBike platform.

Provides validation, date parsing, and formatting functions.
Keep I/O-free — these are pure helper functions.
"""

import re
from datetime import datetime
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

VALID_BIKE_TYPES = {"classic", "electric"}
VALID_USER_TYPES = {"casual", "member"}
VALID_TRIP_STATUSES = {"completed", "cancelled"}
VALID_MAINTENANCE_TYPES = {
    "tire_repair",
    "brake_adjustment",
    "battery_replacement",
    "chain_lubrication",
    "general_inspection",
}

# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_positive(value: float, name: str = "value") -> float:
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")
    return value

def validate_non_negative(value: float, name: str = "value") -> float:
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")
    return value

def validate_email(email: str) -> str:
    if not isinstance(email, str) or "@" not in email:
        raise ValueError(f"Invalid email: {email!r}")
    return email

def validate_in(value: Any, allowed: set, name: str = "value") -> Any:
    if value not in allowed:
        raise ValueError(f"{name} must be one of {allowed}, got {value!r}")
    return value

# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_datetime(text: str) -> datetime:
    return datetime.strptime(text, DATETIME_FORMAT)

def parse_date(text: str) -> datetime:
    return datetime.strptime(text, DATE_FORMAT)

# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_duration(minutes: float) -> str:
    h = int(minutes // 60)
    m = int(minutes % 60)
    return f"{h}h {m}m"

def fmt_currency(amount: float) -> str:
    return f"€{amount:.2f}"
