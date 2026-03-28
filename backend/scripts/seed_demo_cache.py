# backend/scripts/seed_demo_cache.py
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# During dev, test against localhost. Once deployed, change to production.
API_URL = os.getenv("API_URL", "http://localhost:8000/api")

DEMO_QUERIES = [
    # Primary demo queries — must be instant
    "Was Albert Einstein really bad at math in school?",
    "Is the Great Wall of China visible from outer space?",
    "Did Napoleon Bonaparte have an unusually short stature?",
    "Was the Eiffel Tower originally meant to be a temporary structure?",
    "Do we really only use 10 percent of our brains?",

    # Backup queries — for judge interaction
    "Was Walt Disney's body cryogenically frozen after his death?",
    "Did carrots originally come in purple before orange?",
    "Was the Great Fire of London caused by a baker in Pudding Lane?",
    "Did humans and dinosaurs ever coexist on Earth?",
    "Is it true that lightning never strikes the same place twice?",
]

async def seed_cache():
    print(f"Seeding {len(DEMO_QUERIES)} demo queries into cache...")
    print(f"API: {API_URL}")
    print()

    async with httpx.AsyncClient(timeout=60, base_url=API_URL) as client:
        for i, query in enumerate(DEMO_QUERIES, 1):
            try:
                response = await client.post("/verify", json={"query": query})
                data     = response.json()
                score    = data.get("trust_score", "N/A")
                cached   = data.get("from_cache", False)

                # latency_ms is normally present, but handled specifically here
                latency  = data.get("latency_ms", 0)

                status_icon = "⚡" if cached else "✓"
                print(f"  {status_icon} [{i:02d}/{len(DEMO_QUERIES)}] "
                      f"Score={score:3} | {latency:5}ms | {query[:55]}")

            except Exception as e:
                print(f"  ✗ [{i:02d}/{len(DEMO_QUERIES)}] FAILED: {e} | {query[:55]}")

            # Small delay to avoid rate limiting during seeding
            await asyncio.sleep(1.5)

    print()
    print("Cache seeding complete.")
    print("Run again to verify all queries return from_cache: true")

if __name__ == "__main__":
    asyncio.run(seed_cache())
