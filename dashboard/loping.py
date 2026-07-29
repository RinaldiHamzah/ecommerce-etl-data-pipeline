from __future__ import annotations

from decimal import Decimal
from typing import Any


def as_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def money(value: Any) -> str:
    return "Rp {:,.0f}".format(as_float(value)).replace(",", ".")


def number(value: Any) -> str:
    return "{:,.0f}".format(as_float(value)).replace(",", ".")


def percent(value: Any) -> str:
    return f"{as_float(value):.2f}%"


def normalize_payment_label(value: Any) -> str:
    if value is None:
        return "Unknown"
    normalized = str(value).strip().lower().replace("_", " ").replace("-", " ")
    mapping = {
        "cod": "COD",
        "qris": "QRIS",
        "e wallet": "E-Wallet",
        "bank transfer": "Bank Transfer",
        "virtual account": "Virtual Account",
        "credit card": "Credit Card",}
    return mapping.get(normalized, str(value).strip().title())


def add_bar_width(rows: list[dict[str, Any]], value_key: str) -> list[dict[str, Any]]:
    max_value = max((as_float(row.get(value_key)) for row in rows), default=0)
    for row in rows:
        current = as_float(row.get(value_key))
        row["bar_width"] = 0 if max_value == 0 else round((current / max_value) * 100, 2)
    return rows
