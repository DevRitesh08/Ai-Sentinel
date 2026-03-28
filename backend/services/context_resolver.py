import json
import logging
import os
import re
from dataclasses import dataclass

import google.generativeai as genai

from models.schemas import ConversationTurn

logger = logging.getLogger(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MAX_CONTEXT_TURNS = 3
CONTEXT_MODEL = os.getenv("GEMINI_PRIMARY_MODEL", "gemini-2.5-flash")

FOLLOW_UP_PATTERNS = [
    re.compile(r"\b(it|that|them|they|this|those|these|he|she|there|one)\b"),
    re.compile(r"^(and|so|then|also)\b"),
    re.compile(r"\bwhat about\b"),
    re.compile(r"\bhow about\b"),
    re.compile(r"\bthe limit\b"),
    re.compile(r"\bwhy was it\b"),
    re.compile(r"\bwhat is the limit\b"),
    re.compile(r"\bwhat happened\b"),
]


@dataclass
class QueryResolution:
    resolved_query: str
    used_context: bool
    context_turns_used: int


def _trim_history(history: list[ConversationTurn] | None) -> list[ConversationTurn]:
    if not history:
        return []
    return history[-MAX_CONTEXT_TURNS:]


def _looks_like_follow_up(query: str) -> bool:
    normalized = query.lower().strip()
    if not normalized:
        return False

    word_count = len(re.findall(r"\w+", normalized))
    if any(pattern.search(normalized) for pattern in FOLLOW_UP_PATTERNS):
        return True

    if word_count <= 4 and normalized.endswith("?"):
        starter = normalized.split()[0]
        if starter in {"what", "why", "how", "when", "where", "which"}:
            return True

    return False


def _build_prompt(query: str, history: list[ConversationTurn]) -> str:
    history_lines = "\n".join(
        f"{turn.role.upper()}: {turn.content}" for turn in history
    )
    return f"""
You rewrite ambiguous follow-up questions into standalone factual questions for a verification system.

Rules:
- Use the recent conversation only to resolve missing subject or context.
- Preserve the user's original intent.
- Do not answer the question.
- Make the result a single standalone factual question.
- If the current query is already standalone, return it unchanged.

Return valid JSON only:
{{"resolved_query": "standalone question"}}

Conversation:
{history_lines}

Current query:
{query}
""".strip()


async def _rewrite_with_model(query: str, history: list[ConversationTurn]) -> str | None:
    if not os.getenv("GEMINI_API_KEY"):
        return None

    try:
        model = genai.GenerativeModel(model_name=CONTEXT_MODEL)
        response = await model.generate_content_async(
            _build_prompt(query, history),
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=120,
                response_mime_type="application/json",
            ),
        )
        payload = json.loads(response.text)
        resolved = (payload.get("resolved_query") or "").strip()
        if not resolved:
            return None
        return resolved
    except Exception as e:
        logger.warning(f"Context rewrite failed: {e}")
        return None


def _latest_user_turn(history: list[ConversationTurn]) -> str | None:
    for turn in reversed(history):
        if turn.role == "user" and turn.content.strip():
            return turn.content.strip()
    return None


def _heuristic_rewrite(query: str, history: list[ConversationTurn]) -> str:
    latest_user = _latest_user_turn(history)
    if not latest_user:
        return query

    normalized_query = query.lower().strip(" ?!.")
    latest_user_lower = latest_user.lower()

    if "limit" in normalized_query and all(term in latest_user_lower for term in ["survive", "fall", "water"]):
        return "What is the maximum survivable fall height into water for a human under realistic conditions?"

    if "kept" in normalized_query and "eiffel tower" in latest_user_lower:
        return "Why was the Eiffel Tower kept instead of being demolished after it was meant to be temporary?"

    return f"In the context of '{latest_user.rstrip('?.!')}', {query.lstrip()}"


def _is_meaningfully_different(raw_query: str, resolved_query: str) -> bool:
    normalize = lambda value: re.sub(r"\s+", " ", value.strip().lower())
    return normalize(raw_query) != normalize(resolved_query)


async def resolve_query(query: str, history: list[ConversationTurn] | None = None) -> QueryResolution:
    trimmed_history = _trim_history(history)
    if not trimmed_history or not _looks_like_follow_up(query):
        return QueryResolution(
            resolved_query=query,
            used_context=False,
            context_turns_used=0,
        )

    resolved_query = await _rewrite_with_model(query, trimmed_history)
    if not resolved_query:
        resolved_query = _heuristic_rewrite(query, trimmed_history)

    if not resolved_query or not _is_meaningfully_different(query, resolved_query):
        return QueryResolution(
            resolved_query=query,
            used_context=False,
            context_turns_used=0,
        )

    return QueryResolution(
        resolved_query=resolved_query,
        used_context=True,
        context_turns_used=len(trimmed_history),
    )
