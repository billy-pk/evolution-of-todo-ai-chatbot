#!/usr/bin/env python3
"""
Standalone MCP Server for Separate Deployment

This script runs the MCP server as a standalone service for 2-service deployment.
Use this when MOUNT_MCP_SERVER=false and MCP runs on a separate host.

Usage:
    python mcp_standalone.py

Environment Variables:
    PORT - Port to run on (default: 8001)
    DATABASE_URL - PostgreSQL connection string
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path to import backend modules
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Import MCP server
from tools.server import mcp

def main():
    """Run the standalone MCP server."""
    import uvicorn
    import contextlib
    from starlette.applications import Starlette
    from starlette.routing import Mount, Route
    from starlette.responses import JSONResponse
    from typing import AsyncIterator

    port = int(os.environ.get("PORT", 8001))
    host = os.environ.get("HOST", "0.0.0.0")

    logger.info(f"🚀 Starting standalone MCP server on {host}:{port}")
    logger.info(f"   MCP endpoint will be at: http://{host}:{port}/mcp")
    logger.info(f"   Database: {os.environ.get('DATABASE_URL', 'Not set')[:50]}...")

    # Get the streamable HTTP ASGI app from FastMCP
    mcp_app = mcp.streamable_http_app()

    # Health check endpoint at root
    async def health_check(request):
        return JSONResponse({
            "status": "healthy",
            "service": "MCP Server",
            "endpoint": "/mcp",
            "message": "MCP server is running. Use POST /mcp for MCP requests."
        })

    # Create lifespan context manager to initialize MCP session manager
    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Initialize MCP session manager on startup."""
        logger.info("🔌 Initializing MCP session manager...")
        async with mcp.session_manager.run():
            logger.info("✅ MCP session manager initialized")
            yield
        logger.info("🔌 MCP session manager shutdown")

    # Mount MCP at /mcp and health check at root
    app = Starlette(
        routes=[
            Route("/", health_check),
            Mount("/mcp", app=mcp_app)
        ],
        lifespan=lifespan
    )

    # Run with uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
