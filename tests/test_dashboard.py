import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import app


class DashboardRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.test_client()

    def test_dashboard_pages_return_success(self) -> None:
        paths = ["/", "/sales", "/products", "/customers", "/inventory", "/payments", "/returns", "/promo"]
        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"Ecommerce Order", response.data)


if __name__ == "__main__":
    unittest.main()
