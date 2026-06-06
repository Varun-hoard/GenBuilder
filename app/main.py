"""
GenBuilder — FastAPI Application Entry Point

Boots the application, configures logging, CORS, and mounts the API router.
Run with:  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import results_router, router as api_router
from app.core.config import get_settings
from app.services.storage_service import OUTPUT_DIR


# ── Logging ───────────────────────────────────────────────────────────

def _configure_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# ── Lifespan ──────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hooks."""
    settings = get_settings()
    _configure_logging(debug=settings.DEBUG)

    logger = logging.getLogger(__name__)
    logger.info("🚀  %s v%s starting up", settings.APP_NAME, settings.APP_VERSION)
    logger.info("   Debug mode : %s", settings.DEBUG)
    logger.info("   LLM model  : %s", settings.OPENAI_MODEL_NAME)
    logger.info("   Output dir : %s", OUTPUT_DIR)

    yield  # ← application runs here

    logger.info("🛑  %s shutting down", settings.APP_NAME)


# ── Application ───────────────────────────────────────────────────────

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "An LLM-driven agentic pipeline that interprets natural language "
        "engineering constraints and generates structured parameter sets "
        "consumable by generative design solvers."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────

import os
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────

app.include_router(api_router)
app.include_router(results_router)


# ── Root Redirect ─────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to interactive API docs."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")
