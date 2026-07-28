from __future__ import annotations


def executive_summary(where_sql: str) -> str:
    return f"""
        SELECT
            COUNT(DISTINCT order_id) AS total_orders,
            COALESCE(SUM(total_harga) FILTER (WHERE status_order = 'Completed'), 0) AS total_revenue,
            COALESCE(AVG(total_harga) FILTER (WHERE status_order = 'Completed'), 0) AS avg_order_value,
            COUNT(DISTINCT customer_id) AS active_customers,
            COALESCE(SUM(quantity), 0) AS products_sold,
            ROUND(
                COUNT(DISTINCT order_id) FILTER (WHERE status_order = 'Cancelled')::NUMERIC
                / NULLIF(COUNT(DISTINCT order_id), 0) * 100,
                2
            ) AS cancellation_rate
        FROM view_order_details
        {where_sql}
    """


RETURN_SUMMARY = """
    SELECT
        COUNT(DISTINCT return_id) AS total_returns,
        COALESCE(SUM(refund_amount), 0) AS total_refund
    FROM returns
"""

RETURN_RATE = """
    SELECT
        ROUND(
            COUNT(DISTINCT r.order_id)::NUMERIC
            / NULLIF(COUNT(DISTINCT o.order_id), 0) * 100,
            2
        ) AS return_rate
    FROM orders o
    LEFT JOIN returns r ON r.order_id = o.order_id
"""

FILTER_OPTIONS = {
    "kota": "SELECT DISTINCT kota AS value FROM view_order_details WHERE kota IS NOT NULL ORDER BY kota",
    "channel": "SELECT DISTINCT channel AS value FROM view_order_details WHERE channel IS NOT NULL ORDER BY channel",
    "status": "SELECT DISTINCT status_order AS value FROM view_order_details WHERE status_order IS NOT NULL ORDER BY status_order",}

DAILY_SALES = """
    SELECT tanggal, jumlah_order, total_revenue
    FROM view_daily_sales
    ORDER BY tanggal
"""

MONTHLY_SALES = """
    SELECT
        DATE_TRUNC('month', tanggal)::DATE AS bulan,
        SUM(jumlah_order) AS jumlah_order,
        SUM(total_revenue) AS total_revenue
    FROM view_daily_sales
    GROUP BY DATE_TRUNC('month', tanggal)
    ORDER BY bulan
"""

SALES_BY_CITY = """
    SELECT kota, COUNT(DISTINCT order_id) AS jumlah_order, SUM(total_harga) AS total_revenue
    FROM view_order_details
    WHERE kota IS NOT NULL
    GROUP BY kota
    ORDER BY total_revenue DESC
"""

SALES_BY_CHANNEL = """
    SELECT channel, COUNT(DISTINCT order_id) AS jumlah_order, SUM(total_harga) AS total_revenue
    FROM view_order_details
    WHERE channel IS NOT NULL
    GROUP BY channel
    ORDER BY total_revenue DESC
"""

TOP_PRODUCTS = """
    SELECT product_name, kategori, jumlah_order, total_qty_terjual, total_revenue, return_rate_persen
    FROM view_product_sales
    ORDER BY total_revenue DESC
    LIMIT 10
"""

TOP_CATEGORIES = """
    SELECT kategori, SUM(jumlah_order) AS jumlah_order, SUM(total_qty_terjual) AS total_qty, SUM(total_revenue) AS total_revenue
    FROM view_product_sales
    GROUP BY kategori
    ORDER BY total_revenue DESC
"""

CUSTOMER_SEGMENTS = """
    SELECT segment, COUNT(*) AS jumlah_customer, SUM(total_belanja) AS total_belanja, AVG(rata_rata_belanja) AS avg_belanja
    FROM view_customer_summary
    GROUP BY segment
    ORDER BY total_belanja DESC
"""

TOP_CUSTOMERS = """
    SELECT customer_name, customer_email, segment, kota, total_order, total_belanja, order_terakhir
    FROM view_customer_summary
    ORDER BY total_belanja DESC
    LIMIT 12
"""

INVENTORY_STATUS = """
    SELECT product_name, kategori, jumlah_gudang_tercatat, total_stok, gudang_stok_menipis, update_terakhir
    FROM view_inventory_status
    ORDER BY gudang_stok_menipis DESC, total_stok ASC
"""

SUPPLIER_PERFORMANCE = """
    SELECT
        s.nama_supplier,
        s.kota,
        AVG(s.lead_time_hari) AS avg_lead_time,
        COUNT(DISTINCT s.product_id) AS jumlah_produk
    FROM suppliers s
    GROUP BY s.nama_supplier, s.kota
    ORDER BY avg_lead_time ASC
"""

PAYMENT_METHODS = """
    SELECT
        metode_pembayaran,
        SUM(jumlah_transaksi) AS jumlah_transaksi,
        COALESCE(SUM(total_nominal), 0) AS total_nominal
    FROM view_payment_summary
    GROUP BY metode_pembayaran
    ORDER BY total_nominal DESC
"""

RETURN_REASONS = """
    SELECT alasan_return, SUM(jumlah_retur) AS jumlah_retur, SUM(total_qty_retur) AS total_qty_retur, SUM(total_refund) AS total_refund
    FROM view_return_summary
    GROUP BY alasan_return
    ORDER BY jumlah_retur DESC
"""

PROMO_EFFECTIVENESS = """
    SELECT promo_code, nama_promo, tipe_diskon, nilai_diskon, status, jumlah_pemakaian, total_revenue_terkait
    FROM view_promo_effectiveness
    ORDER BY jumlah_pemakaian DESC, total_revenue_terkait DESC
"""


def recent_orders(where_sql: str) -> str:
    return f"""
        SELECT order_id, tanggal_order, product_name, kota, channel, status_order, total_harga
        FROM view_order_details
        {where_sql}
        ORDER BY tanggal_order DESC NULLS LAST
        LIMIT 15
    """
