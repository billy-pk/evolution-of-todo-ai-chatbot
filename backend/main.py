"""
FastAPI Application Entry Point

T020: FastAPI app initialization with CORS configuration
T035: Apply JWT middleware to all /api routes
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from middleware import JWTBearer


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    T020: Initializes FastAPI with CORS configuration
    """
    app = FastAPI(
        title="Todo API",
        description="API for managing todo tasks with authentication",
        version="1.0.0"
    )

    # T020: Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # Next.js development server
            "http://localhost:3001",  # Alternative Next.js port
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Authorization"]
    )

    return app


# Create the main application instance
app = create_app()


@app.get("/health")
async def health_check():
    """
    T086: Health check endpoint with database connection verification.
    GET /api/health (also accessible at /health for convenience).
    Does not require JWT authentication but verifies database connectivity.
    """
    from db import engine
    from sqlmodel import text

    health_status = {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database": "disconnected"
    }

    try:
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = f"error: {str(e)}"

    return health_status


# Alias for /api/health (same handler)
@app.get("/api/health")
async def health_check_api():
    """
    T086: Health check endpoint at /api/health.
    Does not require JWT authentication - defined before middleware is applied.
    """
    return await health_check()


# T035: Import and include routes with JWT middleware applied
# All routes under /api will require JWT authentication
try:
    from routes import tasks
    app.include_router(
        tasks.router,
        prefix="/api",
        dependencies=[Depends(JWTBearer())]  # T035: Apply JWT middleware to all /api routes
    )
except ImportError:
    pass  # Routes will be added later when they are created
