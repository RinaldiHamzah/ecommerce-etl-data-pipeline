from __future__ import annotations
import math
from pathlib import Path
import sys
from typing import Any
import pandas as pd
import psycopg2.extras

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database.connector import db_connection

ROOT = Path(__file__).resolve().parents[1]
WAREHOUSE_DIR = ROOT / "data" / "warehouse"

CLEAN_FILES = {
    "products": WAREHOUSE_DIR / "products_clean.csv",
    "customers": WAREHOUSE_DIR / "customers_clean.csv",
    "promo": WAREHOUSE_DIR / "promo_clean.csv",
    "suppliers": WAREHOUSE_DIR / "suppliers_clean.csv",
    "inventory": WAREHOUSE_DIR / "inventory_clean.csv",
    "orders": WAREHOUSE_DIR / "orders_clean.csv",
    "payments": WAREHOUSE_DIR / "payments_clean.csv",
    "returns": WAREHOUSE_DIR / "returns_clean.csv",
    "order_promo": WAREHOUSE_DIR / "order_promo_clean.csv",
}

LOAD_ORDER = [
    "products",
    "customers",
    "promo",
    "suppliers",
    "inventory",
    "orders",
    "payments",
    "returns",
    "order_promo",
]

PRIMARY_KEYS = {
    "products": ["product_id"],
    "customers": ["customer_id"],
    "promo": ["promo_code"],
    "suppliers": ["supplier_id"],
    "orders": ["order_id"],
    "payments": ["payment_id"],
    "returns": ["return_id"],
    "order_promo": ["order_id", "promo_code"],
}

TABLE_COLUMNS = {
    "products": ["product_id", "product_name", "kategori", "harga_satuan"],
    "customers": [
        "customer_id",
        "customer_name",
        "customer_email",
        "phone_number",
        "gender",
        "join_date",
        "kota",
        "segment",
    ],
    "orders": [
        "order_id",
        "customer_id",
        "product_id",
        "quantity",
        "harga_satuan",
        "total_harga",
        "tanggal_order",
        "kota",
        "channel",
        "status",
    ],
    "inventory": ["product_id", "gudang", "stok_tersedia", "last_update"],
    "suppliers": ["supplier_id", "product_id", "nama_supplier", "kontak", "kota", "lead_time_hari"],
    "promo": [
        "promo_code",
        "nama_promo",
        "tipe_diskon",
        "nilai_diskon",
        "tanggal_mulai",
        "tanggal_selesai",
        "status",
    ],
    "payments": [
        "payment_id",
        "order_id",
        "jumlah_bayar",
        "biaya_admin",
        "tanggal_bayar",
        "metode_pembayaran",
        "status_pembayaran",
    ],
    "returns": [
        "return_id",
        "order_id",
        "quantity_return",
        "refund_amount",
        "tanggal_return",
        "alasan_return",
        "status_return",
    ],
    "order_promo": ["order_id", "promo_code"],
}

# Kolom-kolom bertipe tanggal/waktu per tabel -- perlu dikonversi eksplisit
# supaya psycopg2 tidak salah kirim sebagai string biasa.
DATE_COLUMNS = {
    "customers": ["join_date"],
    "promo": ["tanggal_mulai", "tanggal_selesai"],
    "inventory": ["last_update"],
    "orders": ["tanggal_order"],
    "payments": ["tanggal_bayar"],
    "returns": ["tanggal_return"],}


def clean_value(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if pd.isna(v):
        return None
    return v


def load_csv(name: str) -> pd.DataFrame:
    path = CLEAN_FILES[name]
    if not path.exists():
        raise FileNotFoundError(f"File clean untuk tabel '{name}' tidak ditemukan: {path}")

    df = pd.read_csv(path)

    for col in DATE_COLUMNS.get(name, []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    columns = TABLE_COLUMNS[name]
    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        print(
            f"Kolom tidak ada di CSV untuk tabel '{name}', diisi NULL: "
            + ", ".join(missing_columns)
        )
        for col in missing_columns:
            df[col] = None

    return df[columns]


def upsert_dataframe(conn, table: str, df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    columns = list(df.columns)
    pk_cols = PRIMARY_KEYS.get(table)
    if pk_cols:
        df = df.drop_duplicates(subset=pk_cols, keep="last")

    col_list_sql = ", ".join(columns)
    placeholder_sql = ", ".join(["%s"] * len(columns))

    if pk_cols:
        update_cols = [c for c in columns if c not in pk_cols]
        if update_cols:
            update_sql = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)
            conflict_sql = f"ON CONFLICT ({', '.join(pk_cols)}) DO UPDATE SET {update_sql}"
        else:
            conflict_sql = f"ON CONFLICT ({', '.join(pk_cols)}) DO NOTHING"
    else:
        conflict_sql = ""
    sql = f"""
        INSERT INTO {table} ({col_list_sql})
        VALUES %s
        {conflict_sql}
    """

    records = [tuple(clean_value(v) for v in row) for row in df.itertuples(index=False, name=None)]

    with conn.cursor() as cur:
        psycopg2.extras.execute_values(cur, sql, records, page_size=500)

    return len(records)


def get_existing_values(conn, table: str, column: str) -> set[Any]:
    with conn.cursor() as cur:
        cur.execute(f"SELECT {column} FROM {table}")
        return {row[0] for row in cur.fetchall()}


def filter_foreign_keys(conn, name: str, df: pd.DataFrame) -> pd.DataFrame:
    if name in {"payments", "returns"} and "order_id" in df.columns:
        order_ids = get_existing_values(conn, "orders", "order_id")
        before = len(df)
        df = df[df["order_id"].isin(order_ids)]
        dropped = before - len(df)
        if dropped:
            print(f"  - {name:<15} : {dropped} baris dilewati karena order_id tidak ada")

    if name == "order_promo":
        order_ids = get_existing_values(conn, "orders", "order_id")
        promo_codes = get_existing_values(conn, "promo", "promo_code")
        before = len(df)
        df = df[df["order_id"].isin(order_ids) & df["promo_code"].isin(promo_codes)]
        dropped = before - len(df)
        if dropped:
            print(f"  - {name:<15} : {dropped} baris dilewati karena FK tidak ada")

    return df


def load_table(conn, name: str) -> int:
    df = load_csv(name)
    df = filter_foreign_keys(conn, name, df)
    if name == "inventory":
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE inventory RESTART IDENTITY")
        cols = [c for c in df.columns]
        col_list_sql = ", ".join(cols)
        sql = f"INSERT INTO inventory ({col_list_sql}) VALUES %s"
        records = [tuple(clean_value(v) for v in row) for row in df.itertuples(index=False, name=None)]
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(cur, sql, records, page_size=500)
        return len(records)

    return upsert_dataframe(conn, name, df)

def run_loader() -> None:
    with db_connection() as conn:
        print("Mulai load data ke PostgreSQL (mode: upsert)...\n")
        for name in LOAD_ORDER:
            count = load_table(conn, name)
            print(f"  - {name:<15} : {count} baris diproses")
    print("\nSemua tabel selesai diloading.")

if __name__ == "__main__":
    run_loader()
