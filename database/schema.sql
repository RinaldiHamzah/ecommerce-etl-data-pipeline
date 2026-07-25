-- ============================================
-- DATABASE : Ecommerce Order
-- PostgreSQL
-- ============================================

DROP TABLE IF EXISTS order_promo CASCADE;
DROP TABLE IF EXISTS returns CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS promo CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;

CREATE TABLE products (

    product_id VARCHAR(20) PRIMARY KEY,

    product_name VARCHAR(200) NOT NULL,

    kategori VARCHAR(100) NOT NULL,

    harga_satuan NUMERIC(12,2) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CHECK (harga_satuan > 0)

);

CREATE TABLE customers (

    customer_id VARCHAR(20) PRIMARY KEY,

    customer_name VARCHAR(150) NOT NULL,

    customer_email VARCHAR(150) UNIQUE,

    phone_number VARCHAR(25),

    gender VARCHAR(20),

    join_date DATE,

    kota VARCHAR(100),

    segment VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CHECK (
        gender IN (
            'Laki-Laki',
            'Perempuan'
        )
    )

);

CREATE TABLE orders (

    order_id VARCHAR(20) PRIMARY KEY,

    customer_id VARCHAR(20),

    product_id VARCHAR(20) NOT NULL,

    quantity INTEGER NOT NULL,

    harga_satuan NUMERIC(12,2) NOT NULL,

    total_harga NUMERIC(12,2) NOT NULL,

    tanggal_order DATE,

    kota VARCHAR(100),

    channel VARCHAR(50),

    status VARCHAR(30),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_order_customer
        FOREIGN KEY(customer_id)
        REFERENCES customers(customer_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_order_product
        FOREIGN KEY(product_id)
        REFERENCES products(product_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CHECK(quantity>0),

    CHECK(total_harga>=0),

    CHECK(
        status IN
        (
            'Pending',
            'Completed',
            'Cancelled',
            'Shipped'
        )
    )

);

CREATE TABLE inventory (

    inventory_id SERIAL PRIMARY KEY,

    product_id VARCHAR(20) NOT NULL,

    gudang VARCHAR(100),

    stok_tersedia INTEGER,

    last_update DATE,

    CONSTRAINT fk_inventory_product

        FOREIGN KEY(product_id)

        REFERENCES products(product_id)

        ON DELETE CASCADE,

    UNIQUE(product_id,gudang),

    CHECK(stok_tersedia>=0)

);

CREATE TABLE suppliers (

    supplier_id VARCHAR(20) PRIMARY KEY,

    product_id VARCHAR(20),

    nama_supplier VARCHAR(150),

    kontak VARCHAR(100),

    kota VARCHAR(100),

    lead_time_hari INTEGER,

    CONSTRAINT fk_supplier_product

        FOREIGN KEY(product_id)

        REFERENCES products(product_id)

        ON DELETE SET NULL,

    CHECK(lead_time_hari>0)

);

CREATE TABLE promo (

    promo_code VARCHAR(30) PRIMARY KEY,

    nama_promo VARCHAR(150),

    tipe_diskon VARCHAR(20),

    nilai_diskon NUMERIC(10,2),

    tanggal_mulai DATE,

    tanggal_selesai DATE,

    status VARCHAR(20),

    CHECK(
        tipe_diskon
        IN
        (
            'Fixed',
            'Percentage'
        )
    ),

    CHECK(
        status
        IN
        (
            'Active',
            'Expired'
        )
    ),

    CHECK(
        tanggal_selesai>=tanggal_mulai
    )

);

CREATE TABLE payments (

    payment_id VARCHAR(20) PRIMARY KEY,

    order_id VARCHAR(20) UNIQUE,

    jumlah_bayar NUMERIC(12,2),

    biaya_admin NUMERIC(12,2),

    tanggal_bayar DATE,

    metode_pembayaran VARCHAR(50),

    status_pembayaran VARCHAR(30),

    CONSTRAINT fk_payment_order

        FOREIGN KEY(order_id)

        REFERENCES orders(order_id)

        ON DELETE CASCADE,

    CHECK(jumlah_bayar>=0),

    CHECK(biaya_admin>=0)

);

CREATE TABLE returns (

    return_id VARCHAR(20) PRIMARY KEY,

    order_id VARCHAR(20),

    quantity_return INTEGER,

    refund_amount NUMERIC(12,2),

    tanggal_return DATE,

    alasan_return TEXT,

    status_return VARCHAR(50),

    CONSTRAINT fk_return_order

        FOREIGN KEY(order_id)

        REFERENCES orders(order_id)

        ON DELETE CASCADE,

    CHECK(quantity_return>0),

    CHECK(refund_amount>=0)

);

CREATE TABLE order_promo (

    order_id VARCHAR(20),

    promo_code VARCHAR(30),

    PRIMARY KEY
    (
        order_id,
        promo_code
    ),

    CONSTRAINT fk_orderpromo_order

        FOREIGN KEY(order_id)

        REFERENCES orders(order_id)

        ON DELETE CASCADE,

    CONSTRAINT fk_orderpromo_promo

        FOREIGN KEY(promo_code)

        REFERENCES promo(promo_code)

        ON DELETE CASCADE

);

