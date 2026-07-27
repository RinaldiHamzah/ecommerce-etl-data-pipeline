from pipeline.cleaning import (
    clean_customers,
    clean_inventory,
    clean_order_promo,
    clean_orders,
    clean_payments,
    clean_products,
    clean_promo,
    clean_returns,
    clean_suppliers,)
from pipeline.input_output import load_raw_data, write_processed_files
from pipeline.path import RAW_FILES, ROOT, WAREHOUSE_DIR
from pipeline.cek_quality import check_zero_columns

def run_pipeline() -> None:
    print("ROOT:", ROOT)
    print("WAREHOUSE_DIR:", WAREHOUSE_DIR)

    cleaned_tables = {}

    products = clean_products(load_raw_data(RAW_FILES["products"]))
    cleaned_tables["products"] = products

    promo = clean_promo(load_raw_data(RAW_FILES["promo"]))
    cleaned_tables["promo"] = promo

    suppliers = clean_suppliers(load_raw_data(RAW_FILES["suppliers"]))
    cleaned_tables["suppliers"] = suppliers

    customers = clean_customers(load_raw_data(RAW_FILES["customers"]))
    cleaned_tables["customers"] = customers

    inventory = clean_inventory(load_raw_data(RAW_FILES["inventory"]))
    cleaned_tables["inventory"] = inventory

    orders = clean_orders(load_raw_data(RAW_FILES["orders"]), products)
    cleaned_tables["orders"] = orders

    payments = clean_payments(load_raw_data(RAW_FILES["payments"]))
    cleaned_tables["payments"] = payments

    returns = clean_returns(load_raw_data(RAW_FILES["returns"]), orders)
    cleaned_tables["returns"] = returns

    order_promo = clean_order_promo(load_raw_data(RAW_FILES["order_promo"]))
    cleaned_tables["order_promo"] = order_promo

    write_processed_files(cleaned_tables)

    print(f"Pipeline selesai. Data disimpan di {WAREHOUSE_DIR}")
    for name, tdf in cleaned_tables.items():
        print(f"- {name}: {len(tdf)} baris, {len(tdf.columns)} kolom")

    check_zero_columns(cleaned_tables)