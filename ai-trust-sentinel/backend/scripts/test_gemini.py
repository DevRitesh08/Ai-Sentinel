import asyncio
import os
from dotenv import load_dotenv

os.chdir("d:/Vibe/Ai Sentinel/ai-trust-sentinel/backend")
load_dotenv(".env")

from services.llm_primary import call_primary

async def test():
    try:
        res = await call_primary("Do humans only use 10% of their brain?")
        print(res)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(test())
