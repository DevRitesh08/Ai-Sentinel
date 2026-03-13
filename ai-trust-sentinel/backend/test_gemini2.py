import traceback
import sys
import os
import asyncio
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv(".env")

from services.llm_primary import call_primary

async def test():
    try:
        res = await call_primary("test query")
        with open("error.txt", "w") as f:
            f.write(str(res))
    except Exception as e:
        with open("error.txt", "w") as f:
            f.write(traceback.format_exc())

asyncio.run(test())
