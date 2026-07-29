from __future__ import annotations

from dashboard import queries
from dashboard.service import fetch_one
from dashboard.loping import as_float


def get_kpis(where_sql: str, params: tuple) -> dict:
    summary = fetch_one(queries.executive_summary(where_sql), params)
    returns = fetch_one(queries.RETURN_SUMMARY)
    return_rate = fetch_one(queries.RETURN_RATE)

    summary["total_refund"] = returns.get("total_refund", 0)
    summary["total_returns"] = returns.get("total_returns", 0)
    summary["return_rate"] = return_rate.get("return_rate", 0)
    summary["net_revenue"] = as_float(summary.get("total_revenue")) - as_float(summary.get("total_refund"))
    return summary
