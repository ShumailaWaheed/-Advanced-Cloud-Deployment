"""Main FastAPI application for the event-driven todo chatbot."""

import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.utils.database import db_pool
from src.utils.logger import setup_logger
from src.utils.middleware import SecurityHeadersMiddleware, CorrelationIdMiddleware, RateLimitMiddleware
from src.api.task_routes import router as task_router
from src.api.auth_routes import router as auth_router
from src.api.chat_routes import router as chat_router
from src.api.recurring_task_routes import router as recurring_task_router
from src.api.search_routes import router as search_router

# Setup logging
setup_logger("src", logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Startup
    logger.info("Starting todo chatbot application...")
    await db_pool.initialize_pool()
    logger.info("Database pool initialized")
    yield
    # Shutdown
    logger.info("Shutting down todo chatbot application...")
    await db_pool.close_pool()
    logger.info("Database pool closed")


app = FastAPI(
    title="Event-Driven Todo Chatbot API",
    description="API for managing tasks in the event-driven todo chatbot system",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware stack (order matters: outermost first)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(task_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(recurring_task_router)
app.include_router(search_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_healthy = await db_pool.health_check()
    return {
        "status": "healthy" if db_healthy else "degraded",
        "services": {
            "database": "up" if db_healthy else "down",
        },
    }


@app.get("/ready")
async def readiness_check():
    """Readiness probe for Kubernetes."""
    db_healthy = await db_pool.health_check()
    if not db_healthy:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": "database unavailable"},
        )
    return {"status": "ready"}
