from __future__ import annotations

from typing import Any

import plotly.graph_objects as go


COLORS = {
    "teal": "#0f9f9a",
    "blue": "#4267d8",
    "green": "#2f9d62",
    "amber": "#c48722",
    "red": "#c34b57",
    "ink": "#1d2733",}


def chart_html(fig: go.Figure) -> str:
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=24, r=16, t=32, b=32),
        font=dict(family="Inter, Segoe UI, Arial", size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=330,
        hovermode="x unified",)
    return fig.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})


def line_chart(rows: list[dict[str, Any]], x: str, y: str, name: str) -> str:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[r[x] for r in rows], y=[r[y] for r in rows], mode="lines+markers", name=name, line=dict(color=COLORS["teal"], width=3)))
    return chart_html(fig)


def bar_chart(rows: list[dict[str, Any]], x: str, y: str, name: str, color: str = "blue") -> str:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[r[x] for r in rows], y=[r[y] for r in rows], name=name, marker_color=COLORS[color]))
    return chart_html(fig)


def horizontal_bar(rows: list[dict[str, Any]], x: str, y: str, name: str, color: str = "green") -> str:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[r[x] for r in rows], y=[r[y] for r in rows], orientation="h", name=name, marker_color=COLORS[color]))
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return chart_html(fig)


def donut_chart(rows: list[dict[str, Any]], label: str, value: str, name: str) -> str:
    fig = go.Figure()
    fig.add_trace(go.Pie(labels=[r[label] for r in rows], values=[r[value] for r in rows], hole=0.58, name=name))
    return chart_html(fig)
