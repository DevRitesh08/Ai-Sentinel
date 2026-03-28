import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from models.schemas import ConversationTurn  # noqa: E402
from services.context_resolver import resolve_query  # noqa: E402


class ContextResolverTests(unittest.TestCase):
    def run_async(self, coroutine):
        return asyncio.run(coroutine)

    def test_standalone_query_skips_context(self):
        result = self.run_async(
            resolve_query(
                "What is the boiling point of water?",
                history=[
                    ConversationTurn(role="user", content="Can you survive any fall in water?"),
                    ConversationTurn(role="assistant", content="It depends on height and speed."),
                ],
            )
        )

        self.assertEqual(result.resolved_query, "What is the boiling point of water?")
        self.assertFalse(result.used_context)
        self.assertEqual(result.context_turns_used, 0)

    @patch("services.context_resolver._rewrite_with_model", new_callable=AsyncMock)
    def test_limit_follow_up_uses_context(self, mock_rewrite):
        mock_rewrite.return_value = None

        result = self.run_async(
            resolve_query(
                "What is the limit?",
                history=[
                    ConversationTurn(role="user", content="Can you survive any fall in water?"),
                    ConversationTurn(role="assistant", content="No. Very high-speed impacts can still be fatal."),
                ],
            )
        )

        self.assertTrue(result.used_context)
        self.assertIn("survivable fall height", result.resolved_query.lower())
        self.assertIn("water", result.resolved_query.lower())
        self.assertEqual(result.context_turns_used, 2)

    @patch("services.context_resolver._rewrite_with_model", new_callable=AsyncMock)
    def test_eiffel_tower_follow_up_uses_context(self, mock_rewrite):
        mock_rewrite.return_value = None

        result = self.run_async(
            resolve_query(
                "Why was it kept?",
                history=[
                    ConversationTurn(role="user", content="Was the Eiffel Tower originally meant to be a temporary structure?"),
                    ConversationTurn(role="assistant", content="Yes. It was intended to stand for 20 years."),
                ],
            )
        )

        self.assertTrue(result.used_context)
        self.assertIn("eiffel tower", result.resolved_query.lower())
        self.assertIn("kept", result.resolved_query.lower())

    @patch("services.context_resolver._rewrite_with_model", new_callable=AsyncMock)
    def test_model_resolution_wins_when_available(self, mock_rewrite):
        mock_rewrite.return_value = "Why was the Eiffel Tower kept instead of being demolished after it was meant to be temporary?"

        result = self.run_async(
            resolve_query(
                "Why was it kept?",
                history=[
                    ConversationTurn(role="user", content="Was the Eiffel Tower originally meant to be a temporary structure?"),
                    ConversationTurn(role="assistant", content="Yes. It was intended to stand for 20 years."),
                ],
            )
        )

        self.assertTrue(result.used_context)
        self.assertEqual(
            result.resolved_query,
            "Why was the Eiffel Tower kept instead of being demolished after it was meant to be temporary?",
        )


if __name__ == "__main__":
    unittest.main()
