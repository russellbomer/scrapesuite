"""Base transform utilities."""

from datetime import datetime
from typing import cast

import pandas as pd

Frame = pd.DataFrame


def safe_to_iso(dt_str: str | None) -> str | None:
    """
    Convert datetime string to ISO format, or return None if invalid.

    Uses pandas.to_datetime with UTC and coercion.
    """
    if not dt_str:
        return None

    try:
        dt_any = pd.to_datetime(dt_str, utc=True, errors="coerce")
        if pd.isna(dt_any):
            return None
        dt = cast(datetime, dt_any)
        return dt.isoformat()
    except Exception:
        return None
