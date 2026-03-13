# test_keys.py — Run this from the project root before starting the server.
# Verifies all 4 API keys are working. Fix any failures before proceeding.
#
# Usage:
#   cd backend
#   venv\Scripts\activate  (Windows) or source venv/bin/activate (Mac/Linux)
#   python ../test_keys.py

import os
import sys

# Load .env from backend directory
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "backend", ".env"))

print("=" * 60)
print("  AI Trust Sentinel — API Key Ping Test")
print("=" * 60)

passed = 0
failed = 0

# ── Test 1: OpenAI ────────────────────────────────────────────────────────────
print("\n[1] Testing OpenAI (GPT-4o-mini)...")
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say exactly: KEY_OK"}],
        max_tokens=10
    )
    answer = res.choices[0].message.content.strip()
    print(f"  ✓ OpenAI: {answer}")
    passed += 1
except Exception as e:
    print(f"  ✗ OpenAI FAILED: {e}")
    failed += 1

# ── Test 2: Gemini ────────────────────────────────────────────────────────────
print("\n[2] Testing Gemini Flash...")
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
    res = model.generate_content("Say exactly: KEY_OK")
    print(f"  ✓ Gemini: {res.text.strip()}")
    passed += 1
except Exception as e:
    print(f"  ✗ Gemini FAILED: {e}")
    failed += 1

# ── Test 3: Tavily ────────────────────────────────────────────────────────────
print("\n[3] Testing Tavily...")
try:
    from tavily import TavilyClient
    tc = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    res = tc.search("What is the Eiffel Tower?", max_results=1)
    title = res["results"][0]["title"]
    print(f"  ✓ Tavily: {title[:60]}")
    passed += 1
except Exception as e:
    print(f"  ✗ Tavily FAILED: {e}")
    failed += 1

# ── Test 4: Redis (Upstash) ───────────────────────────────────────────────────
print("\n[4] Testing Upstash Redis...")
try:
    import redis
    r = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
    r.set("ats:ping_test", "KEY_OK", ex=30)
    val = r.get("ats:ping_test")
    print(f"  ✓ Redis: {val}")
    r.delete("ats:ping_test")  # cleanup
    passed += 1
except Exception as e:
    print(f"  ✗ Redis FAILED: {e}")
    print("    → Make sure REDIS_URL starts with rediss:// (double s)")
    failed += 1

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"  Results: {passed}/4 passed, {failed} failed")
if failed == 0:
    print("  🚀 All keys verified — safe to start building!")
else:
    print("  ⚠  Fix failed keys before proceeding. Dead keys at hour 5 = catastrophic.")
print("=" * 60 + "\n")

sys.exit(failed)  # Exits with error code equal to number of failures
