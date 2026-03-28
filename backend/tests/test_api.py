import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402
from models.schemas import VerifyResponse  # noqa: E402


def make_response(**overrides):
    payload = {
        "trust_score": 72,
        "answer": "A contextualized answer.",
        "confidence": 80,
        "verifier_used": False,
        "claims": [],
        "sentences": [],
        "from_cache": False,
        "latency_ms": 123,
        "error": None,
        "trust_label": "MODERATE CONFIDENCE",
        "trust_color": "#FFD166",
        "resolved_query": "What is the maximum survivable fall height into water for a human under realistic conditions?",
        "used_context": True,
        "context_turns_used": 2,
        "status": "ok",
        "degraded_reason": None,
        "answer_source": "primary",
    }
    payload.update(overrides)
    return VerifyResponse(**payload)


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

    @patch("routers.verify.run_verification_pipeline", new_callable=AsyncMock)
    def test_verify_accepts_history_and_returns_context_fields(self, mock_pipeline):
        mock_pipeline.return_value = make_response()

        response = self.client.post(
            "/api/verify",
            json={
                "query": "What is the limit?",
                "history": [
                    {"role": "user", "content": "Can you survive any fall in water?"},
                    {"role": "assistant", "content": "No. Water can still be fatal at very high speeds."},
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["resolved_query"],
            "What is the maximum survivable fall height into water for a human under realistic conditions?",
        )
        self.assertTrue(response.json()["used_context"])
        self.assertEqual(response.json()["context_turns_used"], 2)

        args, kwargs = mock_pipeline.await_args
        self.assertEqual(args[0], "What is the limit?")
        self.assertEqual(len(kwargs["history"]), 2)


if __name__ == "__main__":
    unittest.main()
