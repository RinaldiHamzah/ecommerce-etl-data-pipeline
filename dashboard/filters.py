from __future__ import annotations

from typing import Any


def build_order_filters(args) -> tuple[str, tuple[Any, ...], dict[str, str]]:
    filters = []
    params: list[Any] = []
    selected = {
        "start_date": args.get("start_date", ""),
        "end_date": args.get("end_date", ""),
        "kota": args.get("kota", ""),
        "channel": args.get("channel", ""),
        "status": args.get("status", ""),}

    if selected["start_date"]:
        filters.append("tanggal_order >= %s")
        params.append(selected["start_date"])
    if selected["end_date"]:
        filters.append("tanggal_order <= %s")
        params.append(selected["end_date"])
    if selected["kota"]:
        filters.append("kota = %s")
        params.append(selected["kota"])
    if selected["channel"]:
        filters.append("channel = %s")
        params.append(selected["channel"])
    if selected["status"]:
        filters.append("status_order = %s")
        params.append(selected["status"])

    where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
    return where_sql, tuple(params), selected
