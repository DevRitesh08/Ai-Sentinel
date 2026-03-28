# backend/main.py
import os
import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")

app = FastAPI(
    title="AI Trust Sentinel",
    version="1.0.0",
    description="An AI fact-checking backend that verifies claims and returns a Trust Score (0–100).",
)

# Read allowed origins from environment variable for production CORS
ALLOWED_ORIGINS_RAW = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = (
    ["*"] if ALLOWED_ORIGINS_RAW == "*"
    else [o.strip() for o in ALLOWED_ORIGINS_RAW.split(",")]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_timing(request: Request, call_next):
    """Adds X-Process-Time-Ms header to every response."""
    start = time.time()
    response = await call_next(request)
    elapsed = int((time.time() - start) * 1000)
    response.headers["X-Process-Time-Ms"] = str(elapsed)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({elapsed}ms)")
    return response


# Import and register routers
from routers.verify import router as verify_router
from routers.health import router as health_router

app.include_router(verify_router, prefix="/api")
app.include_router(health_router)
