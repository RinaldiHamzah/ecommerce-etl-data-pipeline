import unittest
import pandas as pd
from pipeline.validation import validate_tables

class ValidationTests(unittest.TestCase):
    def test_validate_tables_accepts_valid_minimal_tables(self) -> None:
        tables = {
            "products": pd.DataFrame(
                {   "product_id": ["P001"],
                    "product_name": ["Kahf Facial Wash"],
                    "kategori": ["Face Care"],
                    "harga_satuan": [32000],}),
            "customers": pd.DataFrame(
                {   "customer_id": ["CUST-0001"],
                    "customer_name": ["Budi"],
                    "join_date": ["2024-01-01"],}),
            "promo": pd.DataFrame(
                {   "promo_code": ["PROMO10"],
                    "tipe_diskon": ["Percentage"],
                    "nilai_diskon": [10],
                    "tanggal_mulai": ["2024-01-01"],
                    "tanggal_selesai": ["2024-12-31"],}),
            "suppliers": pd.DataFrame(
                {   "supplier_id": ["SUP-0001"],
                    "product_id": ["P001"],
                    "lead_time_hari": [3],}),
            "inventory": pd.DataFrame(
                {"product_id": ["P001"],
                    "stok_tersedia": [10],
                    "last_update": ["2024-01-01"],}),
            "orders": pd.DataFrame(
                {   "order_id": ["ORD-0001"],
                    "product_id": ["P001"],
                    "quantity": [2],
                    "harga_satuan": [32000],
                    "total_harga": [64000],
                    "tanggal_order": ["2024-07-01"],}),
            "payments": pd.DataFrame(
                {   "payment_id": ["PAY-0001"],
                    "order_id": ["ORD-0001"],
                    "jumlah_bayar": [64000],
                    "biaya_admin": [1000],
                    "tanggal_bayar": ["2024-07-01"],}),
            "returns": pd.DataFrame(
                {   "return_id": ["RET-0001"],
                    "order_id": ["ORD-0001"],
                    "quantity_return": [1],
                    "refund_amount": [32000],
                    "tanggal_return": ["2024-07-02"],}),
                    
                    "order_promo": pd.DataFrame(
                    {"order_id": ["ORD-0001"],
                    "promo_code": ["PROMO10"],}),}

        self.assertEqual(validate_tables(tables), [])

    def test_validate_tables_reports_duplicate_primary_key(self) -> None:
        tables = {
            "products": pd.DataFrame(
                {   "product_id": ["P001", "P001"],
                    "product_name": ["A", "B"],
                    "kategori": ["Face Care", "Face Care"],
                    "harga_satuan": [10000, 12000],})}
        issues = validate_tables(tables)
        self.assertTrue(any(issue.rule == "primary_key_unique" for issue in issues))

    def test_validate_tables_reports_invalid_foreign_key(self) -> None:
        tables = {
            "products": pd.DataFrame(
                {   "product_id": ["P001"],
                    "product_name": ["A"],
                    "kategori": ["Face Care"],
                    "harga_satuan": [10000],}),
            "orders": pd.DataFrame(
                {   "order_id": ["ORD-0001"],
                    "product_id": ["P999"],
                    "quantity": [1],
                    "harga_satuan": [10000],
                    "total_harga": [10000],}),}

        issues = validate_tables(tables)
        self.assertTrue(any(issue.rule == "foreign_key_valid" for issue in issues))


if __name__ == "__main__":
    unittest.main()
