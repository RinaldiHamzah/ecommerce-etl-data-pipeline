from __future__ import annotations

from flask import Blueprint, current_app, render_template, request

from dashboard import charts, queries
from dashboard.filters import build_order_filters
from dashboard.metrics import get_kpis
from dashboard.services import fetch_all
from dashboard.utils import add_bar_width, normalize_payment_label

dashboard_bp = Blueprint("dashboard", __name__)


def filter_options() -> dict[str, list[dict]]:
    return {name: fetch_all(query) for name, query in queries.FILTER_OPTIONS.items()}


def base_context(active_page: str) -> dict:
    where_sql, params, selected = build_order_filters(request.args)
    return {
        "active_page": active_page,
        "selected": selected,
        "filter_options": filter_options(),
        "where_sql": where_sql,
        "params": params,
    }


@dashboard_bp.errorhandler(Exception)
def handle_error(error):
    current_app.logger.exception("Dashboard request failed")
    return render_template("error.html", error=error, active_page="error"), 500


@dashboard_bp.route("/")
def overview():
    context = base_context("overview")
    daily_sales = fetch_all(queries.DAILY_SALES)
    top_products = add_bar_width(fetch_all(queries.TOP_PRODUCTS), "total_revenue")
    payment_methods = fetch_all(queries.PAYMENT_METHODS)
    for row in payment_methods:
        row["metode_pembayaran"] = normalize_payment_label(row.get("metode_pembayaran"))
    return_reasons = add_bar_width(fetch_all(queries.RETURN_REASONS), "jumlah_retur")
    promo_effectiveness = add_bar_width(fetch_all(queries.PROMO_EFFECTIVENESS), "jumlah_pemakaian")
    kpis = get_kpis(context["where_sql"], context["params"])

    top_product = top_products[0] if top_products else {}
    top_payment = payment_methods[0] if payment_methods else {}
    top_return = return_reasons[0] if return_reasons else {}
    top_promo = promo_effectiveness[0] if promo_effectiveness else {}

    context.update(
        kpis=kpis,
        daily_sales=daily_sales[-14:],
        top_products=top_products,
        payment_methods=add_bar_width(payment_methods, "total_nominal"),
        return_reasons=return_reasons[:6],
        promo_effectiveness=promo_effectiveness[:6],
        insights=[
            {
                "label": "Top revenue product",
                "title": top_product.get("product_name", "-"),
                "description": f"{top_product.get('kategori', '-')} leads revenue contribution.",
                "value": top_product.get("total_revenue", 0),
                "format": "money",
            },
            {
                "label": "Preferred payment",
                "title": top_payment.get("metode_pembayaran", "-"),
                "description": f"{top_payment.get('jumlah_transaksi', 0)} successful payment records.",
                "value": top_payment.get("total_nominal", 0),
                "format": "money",
            },
            {
                "label": "Return hotspot",
                "title": top_return.get("alasan_return", "-"),
                "description": "Most common return reason to investigate.",
                "value": top_return.get("jumlah_retur", 0),
                "format": "number",
            },
            {
                "label": "Best promo usage",
                "title": top_promo.get("promo_code", "-"),
                "description": top_promo.get("nama_promo", "Promo usage performance."),
                "value": top_promo.get("jumlah_pemakaian", 0),
                "format": "number",
            },
        ],
        recent_orders=fetch_all(queries.recent_orders(context["where_sql"]), context["params"]),
        revenue_chart=charts.line_chart(daily_sales, "tanggal", "total_revenue", "Revenue"),
        payment_chart=charts.donut_chart(payment_methods, "metode_pembayaran", "total_nominal", "Payment Method"),
    )
    return render_template("dashboard.html", **context)


@dashboard_bp.route("/sales")
def sales():
    context = base_context("sales")
    daily_sales = fetch_all(queries.DAILY_SALES)
    monthly_sales = fetch_all(queries.MONTHLY_SALES)
    sales_by_city = fetch_all(queries.SALES_BY_CITY)
    sales_by_channel = fetch_all(queries.SALES_BY_CHANNEL)
    context.update(
        daily_sales=daily_sales,
        monthly_sales=monthly_sales,
        sales_by_city=sales_by_city,
        sales_by_channel=sales_by_channel,
        daily_chart=charts.line_chart(daily_sales, "tanggal", "total_revenue", "Daily Revenue"),
        monthly_chart=charts.bar_chart(monthly_sales, "bulan", "total_revenue", "Monthly Revenue"),
        city_chart=charts.bar_chart(sales_by_city, "kota", "total_revenue", "Sales by City"),
        channel_chart=charts.donut_chart(sales_by_channel, "channel", "total_revenue", "Sales by Channel"),
    )
    return render_template("sales.html", **context)


@dashboard_bp.route("/products")
def products():
    context = base_context("products")
    top_products = fetch_all(queries.TOP_PRODUCTS)
    top_categories = fetch_all(queries.TOP_CATEGORIES)
    context.update(
        top_products=top_products,
        top_categories=top_categories,
        product_chart=charts.horizontal_bar(top_products, "total_revenue", "product_name", "Product Revenue"),
        category_chart=charts.donut_chart(top_categories, "kategori", "total_revenue", "Category Revenue"),
    )
    return render_template("products.html", **context)


@dashboard_bp.route("/customers")
def customers():
    context = base_context("customers")
    segments = fetch_all(queries.CUSTOMER_SEGMENTS)
    top_customers = fetch_all(queries.TOP_CUSTOMERS)
    context.update(
        segments=segments,
        top_customers=top_customers,
        segment_chart=charts.donut_chart(segments, "segment", "total_belanja", "Customer Segments"),
    )
    return render_template("customers.html", **context)


@dashboard_bp.route("/inventory")
def inventory():
    context = base_context("inventory")
    inventory_status = fetch_all(queries.INVENTORY_STATUS)
    supplier_performance = fetch_all(queries.SUPPLIER_PERFORMANCE)
    context.update(
        inventory_status=inventory_status,
        supplier_performance=supplier_performance,
        stock_chart=charts.bar_chart(inventory_status, "product_name", "total_stok", "Stock", "amber"),
        supplier_chart=charts.bar_chart(supplier_performance, "nama_supplier", "avg_lead_time", "Lead Time", "blue"),
    )
    return render_template("inventory.html", **context)


@dashboard_bp.route("/payments")
def payments():
    context = base_context("payments")
    payment_methods = fetch_all(queries.PAYMENT_METHODS)
    for row in payment_methods:
        row["metode_pembayaran"] = normalize_payment_label(row.get("metode_pembayaran"))
    context.update(
        payment_methods=payment_methods,
        payment_chart=charts.donut_chart(payment_methods, "metode_pembayaran", "total_nominal", "Payment Method"),
    )
    return render_template("payments.html", **context)


@dashboard_bp.route("/returns")
def returns():
    context = base_context("returns")
    return_reasons = fetch_all(queries.RETURN_REASONS)
    context.update(
        return_reasons=return_reasons,
        return_chart=charts.bar_chart(return_reasons, "alasan_return", "jumlah_retur", "Return Reasons", "red"),
    )
    return render_template("returns.html", **context)


@dashboard_bp.route("/promo")
def promo():
    context = base_context("promo")
    promo_effectiveness = fetch_all(queries.PROMO_EFFECTIVENESS)
    context.update(
        promo_effectiveness=promo_effectiveness,
        promo_chart=charts.bar_chart(promo_effectiveness, "promo_code", "jumlah_pemakaian", "Promo Usage", "green"),
    )
    return render_template("promo.html", **context)
