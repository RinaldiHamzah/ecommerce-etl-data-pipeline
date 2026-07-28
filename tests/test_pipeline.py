import unittest
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.path import WAREHOUSE_DIR
from pipeline.runner import run_pipeline
from pipeline.validation import load_warehouse_tables, validate_tables

EXPECTED_TABLES = {
    "products",
    "customers",
    "promo",
    "suppliers",
    "inventory",
    "orders",
    "payments",
    "returns",
    "order_promo",}

class PipelineOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        run_pipeline()

    def test_all_warehouse_files_exist(self) -> None:
        for table in EXPECTED_TABLES:
            with self.subTest(table=table):
                self.assertTrue((WAREHOUSE_DIR / f"{table}_clean.csv").exists())

    def test_orders_output_has_customer_id(self) -> None:
        orders = pd.read_csv(WAREHOUSE_DIR / "orders_clean.csv")

        self.assertIn("customer_id", orders.columns)

    def test_warehouse_outputs_pass_validation(self) -> None:
        tables = load_warehouse_tables()

        self.assertEqual(validate_tables(tables), [])

if __name__ == "__main__":
    unittest.main()
