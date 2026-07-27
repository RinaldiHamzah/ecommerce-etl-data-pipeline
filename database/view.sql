-- =============================================================================
-- view.sql
-- View analitik/reporting siap pakai di atas 9 tabel warehouse.
-- =============================================================================

DROP VIEW IF EXISTS view_order_details;
DROP VIEW IF EXISTS view_customer_summary;
DROP VIEW IF EXISTS view_product_sales;
DROP VIEW IF EXISTS view_inventory_status;
DROP VIEW IF EXISTS view_payment_summary;
DROP VIEW IF EXISTS view_return_summary;
DROP VIEW IF EXISTS view_daily_sales;
DROP VIEW IF EXISTS view_promo_effectiveness;

-- view_order_details
-- Order lengkap dengan info produk, pelanggan, status pembayaran, & promo
-- yang dipakai (kalau ada). Ini view "flat" utama untuk laporan penjualan.
CREATE VIEW view_order_details AS
SELECT
    o.order_id,
    o.tanggal_order,
    o.product_id,
    pd.product_name,
    pd.kategori,
    o.quantity,
    o.harga_satuan,
    o.total_harga,
    o.kota,
    o.channel,
    o.status          AS status_order,
    o.customer_id,
    c.customer_email,
    c.customer_name,
    c.segment         AS customer_segment,
    p.payment_id,
    p.metode_pembayaran,
    p.status_pembayaran,
    p.jumlah_bayar,
    p.biaya_admin,
    op.promo_code,
    pr.nama_promo,
    pr.tipe_diskon,
    pr.nilai_diskon
FROM orders o
LEFT JOIN products pd      ON pd.product_id = o.product_id
LEFT JOIN customers c      ON c.customer_id = o.customer_id
LEFT JOIN payments p       ON p.order_id = o.order_id
LEFT JOIN order_promo op   ON op.order_id = o.order_id
LEFT JOIN promo pr         ON pr.promo_code = op.promo_code;

-- view_customer_summary
-- Ringkasan transaksi per pelanggan: total order, total belanja, rata-rata,
-- order terakhir.
CREATE VIEW view_customer_summary AS
SELECT
    c.customer_id,
    c.customer_name,
    c.customer_email,
    c.segment,
    c.kota,
    COUNT(o.order_id)                              AS total_order,
    COALESCE(SUM(o.total_harga), 0)                AS total_belanja,
    COALESCE(ROUND(AVG(o.total_harga), 0), 0)       AS rata_rata_belanja,
    MAX(o.tanggal_order)                            AS order_terakhir
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_email, c.segment, c.kota;

-- view_product_sales
-- Performa penjualan per produk: total qty terjual, total revenue, jumlah
-- retur, dan rating retur (return rate).
CREATE VIEW view_product_sales AS
SELECT
    pd.product_id,
    pd.product_name,
    pd.kategori,
    pd.harga_satuan,
    COUNT(DISTINCT o.order_id)                                     AS jumlah_order,
    COALESCE(SUM(o.quantity), 0)                                   AS total_qty_terjual,
    COALESCE(SUM(o.total_harga), 0)                                AS total_revenue,
    COALESCE(SUM(r.quantity_return), 0)                            AS total_qty_retur,
    ROUND(
        COALESCE(SUM(r.quantity_return), 0)::NUMERIC
        / NULLIF(SUM(o.quantity), 0) * 100, 2
    )                                                                AS return_rate_persen
FROM products pd
LEFT JOIN orders o   ON o.product_id = pd.product_id
LEFT JOIN returns r  ON r.order_id = o.order_id
GROUP BY pd.product_id, pd.product_name, pd.kategori, pd.harga_satuan;

-- view_inventory_status
-- Total stok per produk (across semua gudang) + jumlah gudang yang stoknya
-- di bawah ambang batas (di sini dipakai contoh ambang 10).
CREATE VIEW view_inventory_status AS
SELECT
    pd.product_id,
    pd.product_name,
    pd.kategori,
    COUNT(inv.inventory_id)                                    AS jumlah_gudang_tercatat,
    COALESCE(SUM(inv.stok_tersedia), 0)                         AS total_stok,
    COUNT(*) FILTER (WHERE inv.stok_tersedia < 10)              AS gudang_stok_menipis,
    MAX(inv.last_update)                                        AS update_terakhir
FROM products pd
LEFT JOIN inventory inv ON inv.product_id = pd.product_id
GROUP BY pd.product_id, pd.product_name, pd.kategori;

-- view_payment_summary
-- Ringkasan pembayaran per metode & status.
CREATE VIEW view_payment_summary AS
SELECT
    metode_pembayaran,
    status_pembayaran,
    COUNT(*)                       AS jumlah_transaksi,
    SUM(jumlah_bayar)              AS total_nominal,
    SUM(biaya_admin)               AS total_biaya_admin
FROM payments
GROUP BY metode_pembayaran, status_pembayaran
ORDER BY metode_pembayaran, status_pembayaran;

-- view_return_summary
-- Ringkasan retur per alasan & status.
CREATE VIEW view_return_summary AS
SELECT
    alasan_return,
    status_return,
    COUNT(*)                    AS jumlah_retur,
    SUM(quantity_return)        AS total_qty_retur,
    SUM(refund_amount)          AS total_refund
FROM returns
GROUP BY alasan_return, status_return
ORDER BY jumlah_retur DESC;

-- view_daily_sales
-- Penjualan harian (untuk grafik tren).
CREATE VIEW view_daily_sales AS
SELECT
    DATE(tanggal_order)              AS tanggal,
    COUNT(order_id)                  AS jumlah_order,
    SUM(total_harga)                 AS total_revenue,
    ROUND(AVG(total_harga), 0)       AS rata_rata_order_value
FROM orders
WHERE status <> 'Cancelled'
GROUP BY DATE(tanggal_order)
ORDER BY tanggal;

-- view_promo_effectiveness
-- Efektivitas tiap kode promo: berapa kali dipakai & total revenue order yg memakainya.
CREATE VIEW view_promo_effectiveness AS
SELECT
    pr.promo_code,
    pr.nama_promo,
    pr.tipe_diskon,
    pr.nilai_diskon,
    pr.status,
    COUNT(op.order_id)                     AS jumlah_pemakaian,
    COALESCE(SUM(o.total_harga), 0)        AS total_revenue_terkait
FROM promo pr
LEFT JOIN order_promo op ON op.promo_code = pr.promo_code
LEFT JOIN orders o       ON o.order_id = op.order_id
GROUP BY pr.promo_code, pr.nama_promo, pr.tipe_diskon, pr.nilai_diskon, pr.status
ORDER BY jumlah_pemakaian DESC;
