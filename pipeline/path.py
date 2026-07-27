from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
WAREHOUSE_DIR = ROOT / "data" / "warehouse"

RAW_FILES = {
    "customers": RAW_DIR / "raw_customers.csv",
    "inventory": RAW_DIR / "raw_inventory.csv",
    "order_promo": RAW_DIR / "raw_order_promo.csv",
    "orders": RAW_DIR / "raw_orders.csv",
    "payments": RAW_DIR / "raw_payments.csv",
    "products": RAW_DIR / "raw_products.csv",
    "promo": RAW_DIR / "raw_promo.csv",
    "returns": RAW_DIR / "raw_returns.csv",
    "suppliers": RAW_DIR / "raw_suppliers.csv",}
