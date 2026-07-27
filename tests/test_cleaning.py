import unittest
import pandas as pd
from pipeline.cleaning import clean_order_promo, clean_orders, clean_payments, clean_returns


class CleaningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.products = pd.DataFrame(
            {   "product_id": ["P001"],
                "product_name": ["Kahf Facial Wash"],
                "kategori": ["Face Care"],
                "harga_satuan": [32000],})
        self.customers = pd.DataFrame(
            {   "customer_id": ["CUST-0001"],
                "customer_email": ["customer1@email.com"],})
        self.orders = pd.DataFrame(
            {   "order_id": ["ORD-0001"],
                "product_id": ["P001"],
                "customer_email": ["customer1@email.com"],
                "quantity": [2],
                "tanggal_order": ["2024-07-01"],
                "kota": ["Jakarta"],
                "channel": ["website"],
                "status": ["completed"],})
        self.cleaned_orders = clean_orders(self.orders, self.products, self.customers)

    def test_clean_orders_adds_customer_id_from_email(self) -> None:
        self.assertIn("customer_id", self.cleaned_orders.columns)
        self.assertEqual(self.cleaned_orders.loc[0, "customer_id"], "CUST-0001")

    def test_clean_orders_calculates_total_harga(self) -> None:
        self.assertEqual(self.cleaned_orders.loc[0, "total_harga"], 64000)

    def test_clean_payments_drops_unknown_order_id(self) -> None:
        payments = pd.DataFrame(
            {   "payment_id": ["PAY-0001", "PAY-0002"],
                "order_id": ["ORD-0001", "ORD-9999"],
                "jumlah_bayar": [64000, 100000],
                "biaya_admin": [1000, 1000],
                "tanggal_bayar": ["2024-07-01", "2024-07-02"],})

        cleaned = clean_payments(payments, self.cleaned_orders)

        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.loc[0, "order_id"], "ORD-0001")

    def test_clean_returns_drops_unknown_order_id(self) -> None:
        returns = pd.DataFrame(
            {   "return_id": ["RET-0001", "RET-0002"],
                "order_id": ["ORD-0001", "ORD-9999"],
                "quantity_return": [1, 1],
                "refund_amount": [32000, 50000],
                "tanggal_return": ["2024-07-03", "2024-07-04"],
                "alasan_return": ["rusak", "rusak"],})
        cleaned = clean_returns(returns, self.cleaned_orders)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.loc[0, "order_id"], "ORD-0001")

    def test_clean_order_promo_drops_unknown_references(self) -> None:
        order_promo = pd.DataFrame(
            {   "order_id": ["ORD-0001", "ORD-9999", "ORD-0001"],
                "promo_code": ["PROMO10", "PROMO10", "MISSING"],})
        promo = pd.DataFrame({"promo_code": ["PROMO10"]})
        cleaned = clean_order_promo(order_promo, self.cleaned_orders, promo)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.loc[0, "order_id"], "ORD-0001")
        self.assertEqual(cleaned.loc[0, "promo_code"], "PROMO10")

if __name__ == "__main__":
    unittest.main()