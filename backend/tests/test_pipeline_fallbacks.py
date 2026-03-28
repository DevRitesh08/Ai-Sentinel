import asyncio
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from services.llm_primary import PrimaryLLMError  # noqa: E402
from services.pipeline import run_verification_pipeline  # noqa: E402


def make_resolution(query: str) -> SimpleNamespace:
    return SimpleNamespace(
        resolved_query=query,
        used_context=False,
        context_turns_used=0,
    )


def make_offline_response(answer: str) -> dict:
    return {
        "trust_score": 81,
        "answer": answer,
        "confidence": 91,
        "verifier_used": False,
        "claims": [],
        "sentences": [],
        "from_cache": True,
        "latency_ms": 32,
        "trust_label": "MODERATE CONFIDENCE",
        "trust_color": "#FFD166",
    }


class PipelineFallbackTests(unittest.TestCase):
    def run_async(self, coroutine):
        return asyncio.run(coroutine)

    def test_quota_failure_uses_offline_demo_response(self):
        with (
            patch.dict("os.environ", {"OFFLINE_MODE": "false"}, clear=False),
            patch("services.pipeline.resolve_query", new=AsyncMock(return_value=make_resolution("demo question"))),
            patch("services.pipeline.get_cached", return_value=None),
            patch(
                "services.pipeline.call_primary",
                new=AsyncMock(side_effect=PrimaryLLMError("quota hit", "quota_exceeded")),
            ),
            patch(
                "services.pipeline.get_offline_response",
                return_value=make_offline_response("Offline demo answer."),
            ),
            patch("services.pipeline.call_ollama_primary", new=AsyncMock()),
        ):
            response = self.run_async(run_verification_pipeline("demo question"))

        self.assertEqual(response.status, "degraded")
        self.assertEqual(response.degraded_reason, "quota_exceeded")
        self.assertEqual(response.answer_source, "offline_demo")
        self.assertEqual(response.answer, "Offline demo answer.")

    def test_quota_failure_uses_ollama_primary_fallback(self):
        with (
            patch.dict("os.environ", {"OFFLINE_MODE": "false"}, clear=False),
            patch("services.pipeline.resolve_query", new=AsyncMock(return_value=make_resolution("fresh question"))),
            patch("services.pipeline.get_cached", return_value=None),
            patch(
                "services.pipeline.call_primary",
                new=AsyncMock(side_effect=PrimaryLLMError("quota hit", "quota_exceeded")),
            ),
            patch("services.pipeline.get_offline_response", return_value=None),
            patch(
                "services.pipeline.call_ollama_primary",
                new=AsyncMock(return_value={"answer": "Local fallback answer.", "confidence": 35}),
            ),
        ):
            response = self.run_async(run_verification_pipeline("fresh question"))

        self.assertEqual(response.status, "degraded")
        self.assertEqual(response.degraded_reason, "quota_exceeded")
        self.assertEqual(response.answer_source, "ollama_fallback")
        self.assertEqual(response.answer, "Local fallback answer.")
        self.assertGreaterEqual(len(response.sentences), 1)

    def test_quota_failure_without_fallback_returns_visible_error_answer(self):
        with (
            patch.dict("os.environ", {"OFFLINE_MODE": "false"}, clear=False),
            patch("services.pipeline.resolve_query", new=AsyncMock(return_value=make_resolution("fresh question"))),
            patch("services.pipeline.get_cached", return_value=None),
            patch(
                "services.pipeline.call_primary",
                new=AsyncMock(side_effect=PrimaryLLMError("quota hit", "quota_exceeded")),
            ),
            patch("services.pipeline.get_offline_response", return_value=None),
            patch(
                "services.pipeline.call_ollama_primary",
                new=AsyncMock(side_effect=PrimaryLLMError("ollama down", "provider_unavailable")),
            ),
        ):
            response = self.run_async(run_verification_pipeline("fresh question"))

        self.assertEqual(response.status, "error")
        self.assertEqual(response.degraded_reason, "quota_exceeded")
        self.assertEqual(response.answer_source, "none")
        self.assertIn("Provider quota reached", response.answer)


if __name__ == "__main__":
    unittest.main()
