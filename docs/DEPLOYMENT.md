# Deployment Guide

This repo is designed for a split deployment:

- Backend on Railway
- Frontend on Vercel

## Backend On Railway

### Root settings

- Root directory: `backend`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2`

### Required environment variables

- `GEMINI_API_KEY`
- `OPENAI_API_KEY`
- `TAVILY_API_KEY`
- `REDIS_URL`

### Recommended environment variables

- `GEMINI_PRIMARY_MODEL=gemini-2.5-flash`
- `GEMINI_VERIFIER_MODEL=gemini-2.5-pro`
- `OPENAI_EXTRACTION_MODEL=gpt-4o-mini`
- `CONFIDENCE_THRESHOLD=75`
- `CACHE_TTL_SECONDS=3600`
- `MAX_CLAIMS=5`
- `MAX_TAVILY_RESULTS=3`

### Post-deploy checks

1. Open `/health`
2. Open `/health/full`
3. Send a request to `/api/verify`
4. Confirm CORS settings allow the frontend

## Frontend On Vercel

### Root settings

- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`

### Environment variables

- `VITE_API_URL=https://your-railway-backend.up.railway.app/api`

### Post-deploy checks

1. Load the homepage
2. Submit a sample myth query
3. Confirm claims and sources render correctly
4. Check mobile layout

## Before You Put The Demo In The README

- Verify the deployed backend is not returning `404`
- Run 5-10 sample queries manually
- Capture screenshots and one short GIF
- Note real median latency and cost numbers
- Add the public URL to the README only after the above passes
