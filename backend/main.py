"""
FastAPI Application Entry Point

T020: FastAPI app initialization with CORS configuration
T035: Apply JWT middleware to all /api routes
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from middleware import JWTBearer
import logging

# Configure logging to show INFO level messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get MCP app if mounting (must happen before creating FastAPI app)
# Following pattern from: https://github.com/modelcontextprotocol/python-sdk/pull/1712
import contextlib
from typing import AsyncIterator

mcp_app = None
mcp_lifespan = None

if settings.MOUNT_MCP_SERVER:
    try:
        from tools.server import get_mcp_app, mcp as mcp_server

        mcp_app = get_mcp_app()

        # Create custom lifespan that runs MCP session manager
        # FastAPI doesn't automatically trigger lifespan of mounted sub-apps
        @contextlib.asynccontextmanager
        async def mcp_lifespan(app: FastAPI) -> AsyncIterator[None]:
            """FastAPI lifespan that initializes the MCP session manager."""
            async with mcp_server.session_manager.run():
                yield

        logging.getLogger(__name__).info("✅ MCP app and lifespan created")
    except Exception as e:
        logging.getLogger(__name__).error(f"❌ Failed to create MCP app: {e}")
        import traceback
        traceback.print_exc()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    T020: Initializes FastAPI with CORS configuration
    """
    app = FastAPI(
        title="Todo API",
        description="API for managing todo tasks with authentication",
        version="1.0.0",
        lifespan=mcp_lifespan  # Pass MCP lifespan to FastAPI
    )

    # T020: Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],

        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Authorization"]
    )

    return app


# Create the main application instance
app = create_app()


@app.head("/health")
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


# Mount MCP server if MOUNT_MCP_SERVER is enabled (unified deployment mode)
if settings.MOUNT_MCP_SERVER and mcp_app is not None:
    try:
        # Mount MCP app at /mcp following FastMCP + FastAPI pattern
        app.mount("/mcp", mcp_app)
        logging.getLogger(__name__).info("✅ MCP server mounted at /mcp (unified deployment mode)")
    except Exception as e:
        logging.getLogger(__name__).error(f"❌ Failed to mount MCP server: {e}")
        import traceback
        traceback.print_exc()
elif not settings.MOUNT_MCP_SERVER:
    logging.getLogger(__name__).info("ℹ️  MCP server not mounted - expecting separate service on port 8001")


# T044: Include chat route (User Story 6 - Conversation History)
# Chat endpoint already has JWTBearer in its dependencies
try:
    from routes import chat
    app.include_router(chat.router)  # No need for prefix - already in router
    logging.getLogger(__name__).info("Chat route registered successfully")
except ImportError as e:
    logging.getLogger(__name__).error(f"Failed to import chat route: {e}")
except Exception as e:
    logging.getLogger(__name__).error(f"Error registering chat route: {e}")

# ChatKit integration routes (no JWT middleware - handles auth internally)
# These endpoints bridge ChatKit UI with our custom conversation database
try:
    from routes import chatkit
    app.include_router(chatkit.router)
    app.include_router(chatkit.chatkit_router)
    logging.getLogger(__name__).info("ChatKit routes registered successfully")
except ImportError as e:
    logging.getLogger(__name__).error(f"Failed to import chatkit route: {e}")
except Exception as e:
    logging.getLogger(__name__).error(f"Error registering chatkit route: {e}")
