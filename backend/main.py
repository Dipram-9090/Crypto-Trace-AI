"""Main FastAPI Application Entrypoint for Crypto-Trace-AI."""

import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database.session import Base, engine
from backend.api import (
    transactions_router,
    wallets_router,
    fraud_router,
    ai_router,
    blockchain_router,
    auth_router,
    ws_router
)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("cryptotrace.backend.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown hooks."""
    logger.info("Initializing database tables...")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning(f"Database table initialization notice: {e}")
    logger.info("Crypto-Trace-AI Backend API is READY.")
    yield
    logger.info("Shutting down Crypto-Trace-AI services...")


app = FastAPI(
    title="Crypto-Trace-AI Forensic Engine API",
    description="Enterprise-grade AI-powered blockchain transaction tracing and fraud detection platform.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(transactions_router, prefix="/api/v1")
app.include_router(wallets_router, prefix="/api/v1")
app.include_router(fraud_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(blockchain_router, prefix="/api/v1")
app.include_router(ws_router)


@app.get("/")
async def root():
    return {
        "service": "Crypto-Trace-AI Backend API",
        "version": "2.0.0",
        "status": "HEALTHY",
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "ok", "database": "connected", "ai_engine": "ready"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
