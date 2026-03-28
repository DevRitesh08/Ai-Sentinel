import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402


class ApiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_verify_rejects_too_short_query(self):
        response = self.client.post("/api/verify", json={"query": "x"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Query too short", response.json()["detail"])

    def test_verify_rejects_non_semantic_query(self):
        response = self.client.post("/api/verify", json={"query": "???"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("meaningful text", response.json()["detail"])

    def test_verify_requires_query_field(self):
        response = self.client.post("/api/verify", json={})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
