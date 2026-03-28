import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
BACKEND_ENV = ROOT / "backend" / ".env"

if BACKEND_ENV.exists():
    load_dotenv(BACKEND_ENV)

PRIMARY_MODEL = os.getenv("GEMINI_PRIMARY_MODEL", "gemini-2.5-flash")
EXTRACTION_MODEL = os.getenv("OPENAI_EXTRACTION_MODEL", "gpt-4o-mini")

print("=" * 60)
print("  AI Trust Sentinel - API Key Ping Test")
print("=" * 60)

passed = 0
failed = 0

print(f"\n[1] Testing OpenAI ({EXTRACTION_MODEL})...")
try:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=EXTRACTION_MODEL,
        messages=[{"role": "user", "content": "Say exactly: KEY_OK"}],
        max_tokens=10,
    )
    answer = response.choices[0].message.content.strip()
    print(f"  [OK] OpenAI: {answer}")
    passed += 1
except Exception as e:
    print(f"  [FAIL] OpenAI: {e}")
    failed += 1

print(f"\n[2] Testing Gemini ({PRIMARY_MODEL})...")
try:
    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(PRIMARY_MODEL)
    response = model.generate_content("Say exactly: KEY_OK")
    print(f"  [OK] Gemini: {response.text.strip()}")
    passed += 1
except Exception as e:
    print(f"  [FAIL] Gemini: {e}")
    failed += 1

print("\n[3] Testing Tavily...")
try:
    from tavily import TavilyClient

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = client.search("What is the Eiffel Tower?", max_results=1)
    title = response["results"][0]["title"]
    print(f"  [OK] Tavily: {title[:60]}")
    passed += 1
except Exception as e:
    print(f"  [FAIL] Tavily: {e}")
    failed += 1

print("\n[4] Testing Upstash Redis...")
try:
    import redis

    client = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
    client.set("ats:ping_test", "KEY_OK", ex=30)
    value = client.get("ats:ping_test")
    print(f"  [OK] Redis: {value}")
    client.delete("ats:ping_test")
    passed += 1
except Exception as e:
    print(f"  [FAIL] Redis: {e}")
    print("      Make sure REDIS_URL starts with rediss://")
    failed += 1

print("\n" + "=" * 60)
print(f"  Results: {passed}/4 passed, {failed} failed")
if failed == 0:
    print("  All keys verified - safe to start building.")
else:
    print("  Fix failed keys before proceeding.")
print("=" * 60 + "\n")

sys.exit(failed)
