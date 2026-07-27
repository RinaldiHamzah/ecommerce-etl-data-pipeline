from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database.connector import db_connection


st.set_page_config(
    page_title="Ecommerce Order Dashboard",
    page_icon=None,
    layout="wide",)


def format_currency(value: float | int | None) -> str:
    if pd.isna(value):
        value = 0
    return f"Rp {float(value):,.0f}".replace(",", ".")


@st.cache_data(ttl=300)
def read_query(query: str) -> pd.DataFrame:
    with db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)


@st.cache_data(ttl=300)
def load_dashboard_data() -> dict[str, pd.DataFrame]:
    return {
        "orders": read_query("SELECT * FROM view_order_details"),
        "daily_sales": read_query("SELECT * FROM view_daily_sales"),
        "products": read_query("SELECT * FROM view_product_sales"),
        "payments": read_query("SELECT * FROM view_payment_summary"),
        "returns": read_query("SELECT * FROM view_return_summary"),
        "promo": read_query("SELECT * FROM view_promo_effectiveness"),
        "customers": read_query("SELECT * FROM view_customer_summary"),
        "inventory": read_query("SELECT * FROM view_inventory_status"),
    }


def filter_orders(orders: pd.DataFrame) -> pd.DataFrame:
    orders = orders.copy()
    orders["tanggal_order"] = pd.to_datetime(orders["tanggal_order"], errors="coerce")

    with st.sidebar:
        st.header("Filter")

        min_date = orders["tanggal_order"].min()
        max_date = orders["tanggal_order"].max()
        date_range = st.date_input(
            "Tanggal order",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
        )

        kota_options = sorted(orders["kota"].dropna().unique())
        channel_options = sorted(orders["channel"].dropna().unique())
        status_options = sorted(orders["status_order"].dropna().unique())

        selected_kota = st.multiselect("Kota", kota_options, default=kota_options)
        selected_channel = st.multiselect("Channel", channel_options, default=channel_options)
        selected_status = st.multiselect("Status order", status_options, default=status_options)

    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        orders = orders[
            (orders["tanggal_order"] >= start_date)
            & (orders["tanggal_order"] <= end_date + pd.Timedelta(days=1))
        ]

    if selected_kota:
        orders = orders[orders["kota"].isin(selected_kota)]
    if selected_channel:
        orders = orders[orders["channel"].isin(selected_channel)]
    if selected_status:
        orders = orders[orders["status_order"].isin(selected_status)]

    return orders


def render_overview(orders: pd.DataFrame) -> None:
    completed_orders = orders[orders["status_order"] == "Completed"]
    total_revenue = completed_orders["total_harga"].sum()
    total_orders = orders["order_id"].nunique()
    avg_order_value = completed_orders["total_harga"].mean()
    return_rate = orders["order_id"].isin(
        read_query("SELECT DISTINCT order_id FROM returns")["order_id"]
    ).mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", format_currency(total_revenue))
    col2.metric("Total Orders", f"{total_orders:,}".replace(",", "."))
    col3.metric("Average Order Value", format_currency(avg_order_value))
    col4.metric("Return Rate", f"{return_rate * 100:.2f}%")


def render_sales_tab(orders: pd.DataFrame, daily_sales: pd.DataFrame) -> None:
    st.subheader("Tren Penjualan")
    daily_sales = daily_sales.copy()
    daily_sales["tanggal"] = pd.to_datetime(daily_sales["tanggal"], errors="coerce")
    daily_sales = daily_sales.set_index("tanggal")
    st.line_chart(daily_sales[["total_revenue", "jumlah_order"]])

    st.subheader("Order Terbaru")
    recent_orders = orders.sort_values("tanggal_order", ascending=False).head(20)
    st.dataframe(
        recent_orders[
            [
                "order_id",
                "tanggal_order",
                "product_name",
                "kota",
                "channel",
                "status_order",
                "total_harga",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


def render_products_tab(products: pd.DataFrame, inventory: pd.DataFrame) -> None:
    st.subheader("Top Products")
    top_products = products.sort_values("total_revenue", ascending=False).head(10)
    st.bar_chart(top_products.set_index("product_name")["total_revenue"])
    st.dataframe(top_products, use_container_width=True, hide_index=True)

    st.subheader("Inventory Status")
    low_stock = inventory.sort_values(["gudang_stok_menipis", "total_stok"], ascending=[False, True])
    st.dataframe(low_stock, use_container_width=True, hide_index=True)


def render_payment_return_tab(payments: pd.DataFrame, returns: pd.DataFrame) -> None:
    left, right = st.columns(2)

    with left:
        st.subheader("Payment Method")
        payment_by_method = payments.groupby("metode_pembayaran", as_index=False)["total_nominal"].sum()
        st.bar_chart(payment_by_method.set_index("metode_pembayaran")["total_nominal"])
        st.dataframe(payments, use_container_width=True, hide_index=True)

    with right:
        st.subheader("Returns Analysis")
        return_by_reason = returns.groupby("alasan_return", as_index=False)["jumlah_retur"].sum()
        st.bar_chart(return_by_reason.set_index("alasan_return")["jumlah_retur"])
        st.dataframe(returns, use_container_width=True, hide_index=True)


def render_promo_customer_tab(promo: pd.DataFrame, customers: pd.DataFrame) -> None:
    left, right = st.columns(2)

    with left:
        st.subheader("Promo Effectiveness")
        st.bar_chart(promo.set_index("promo_code")["jumlah_pemakaian"])
        st.dataframe(promo, use_container_width=True, hide_index=True)

    with right:
        st.subheader("Top Customers")
        top_customers = customers.sort_values("total_belanja", ascending=False).head(15)
        st.dataframe(top_customers, use_container_width=True, hide_index=True)


def main() -> None:
    st.title("Ecommerce Order Dashboard")
    st.caption("Dashboard analytics dari PostgreSQL view warehouse.")

    try:
        data = load_dashboard_data()
    except Exception as exc:
        st.error("Gagal membaca data dari PostgreSQL.")
        st.exception(exc)
        st.stop()

    filtered_orders = filter_orders(data["orders"])
    render_overview(filtered_orders)

    tabs = st.tabs(["Sales", "Products & Inventory", "Payments & Returns", "Promo & Customers"])
    with tabs[0]:
        render_sales_tab(filtered_orders, data["daily_sales"])
    with tabs[1]:
        render_products_tab(data["products"], data["inventory"])
    with tabs[2]:
        render_payment_return_tab(data["payments"], data["returns"])
    with tabs[3]:
        render_promo_customer_tab(data["promo"], data["customers"])


if __name__ == "__main__":
    main()
