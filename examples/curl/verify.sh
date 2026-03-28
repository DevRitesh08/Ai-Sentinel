#!/usr/bin/env bash
set -euo pipefail

API_URL="${ATS_API_URL:-http://localhost:8000/api}"
QUERY="${1:-Was the Eiffel Tower meant to be temporary?}"

curl -X POST "${API_URL}/verify" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"${QUERY}\"}"
