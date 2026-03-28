"""
Minimal Python example for calling the AI Trust Sentinel API.

Usage:
    python examples/python/verify_request.py

Optional:
    set ATS_API_URL=http://localhost:8000/api
"""

import json
import os
from urllib import request

API_URL = os.getenv("ATS_API_URL", "http://localhost:8000/api")
QUERY = os.getenv("ATS_QUERY", "Was the Eiffel Tower meant to be temporary?")

payload = json.dumps({"query": QUERY}).encode("utf-8")
req = request.Request(
    f"{API_URL}/verify",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)

with request.urlopen(req, timeout=30) as response:
    result = json.loads(response.read().decode("utf-8"))

print(json.dumps(result, indent=2))
