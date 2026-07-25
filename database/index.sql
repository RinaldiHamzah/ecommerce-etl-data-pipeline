-- =====================================
-- INDEX PRODUCTS
-- =====================================

CREATE INDEX idx_products_kategori
ON products(kategori);

CREATE INDEX idx_products_name
ON products(product_name);

-- =====================================
-- INDEX CUSTOMERS
-- =====================================

CREATE INDEX idx_customer_email
ON customers(customer_email);

CREATE INDEX idx_customer_city
ON customers(kota);

CREATE INDEX idx_customer_segment
ON customers(segment);

-- =====================================
-- INDEX ORDERS
-- =====================================

CREATE INDEX idx_orders_customer
ON orders(customer_id);

CREATE INDEX idx_orders_product
ON orders(product_id);

CREATE INDEX idx_orders_date
ON orders(tanggal_order);

CREATE INDEX idx_orders_status
ON orders(status);

CREATE INDEX idx_orders_channel
ON orders(channel);

CREATE INDEX idx_orders_city
ON orders(kota);

CREATE INDEX idx_inventory_product
ON inventory(product_id);

CREATE INDEX idx_inventory_warehouse
ON inventory(gudang);

CREATE INDEX idx_supplier_product
ON suppliers(product_id);

CREATE INDEX idx_supplier_city
ON suppliers(kota);

CREATE INDEX idx_payment_date
ON payments(tanggal_bayar);

CREATE INDEX idx_payment_method
ON payments(metode_pembayaran);

CREATE INDEX idx_payment_status
ON payments(status_pembayaran);

CREATE INDEX idx_return_date
ON returns(tanggal_return);

CREATE INDEX idx_return_status
ON returns(status_return);

CREATE INDEX idx_promo_status
ON promo(status);

CREATE INDEX idx_promo_date
ON promo(tanggal_mulai);

CREATE INDEX idx_promo_end
ON promo(tanggal_selesai);

CREATE INDEX idx_orderpromo_promo
ON order_promo(promo_code);

CREATE INDEX idx_orders_city_status
ON orders(kota,status);

CREATE INDEX idx_orders_date_status
ON orders(tanggal_order,status);

CREATE INDEX idx_orders_product_date
ON orders(product_id,tanggal_order);