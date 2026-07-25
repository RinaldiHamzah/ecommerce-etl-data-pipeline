from pathlib import Path
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from config.config import *

WAREHOUSE = ROOT / "data" / "warehouse"

FILES = {

    "customers":"clean_customers.csv",

    "products":"clean_products.csv",

    "suppliers":"clean_suppliers.csv",

    "promo":"clean_promo.csv",

    "inventory":"clean_inventory.csv",

    "orders":"clean_orders.csv",

    "payments":"clean_payments.csv",

    "returns":"clean_returns.csv",

    "order_promo":"clean_order_promo.csv"}

def connect():

    return psycopg2.connect(

        host=DB_HOST,

        port=DB_PORT,

        database=DB_NAME,

        user=DB_USER,

        password=DB_PASSWORD)