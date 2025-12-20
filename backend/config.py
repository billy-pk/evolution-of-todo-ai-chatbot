from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )

    # Database
    DATABASE_URL: str

    # Authentication
    BETTER_AUTH_SECRET: str
    BETTER_AUTH_URL: str = "http://localhost:3000"  # Better Auth frontend URL for JWKS

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Environment
    ENVIRONMENT: str = "development"

    # Connection Pooling (for database)
    DB_POOL_SIZE: int = 5
    DB_POOL_MAX_OVERFLOW: int = 10

    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_API_TIMEOUT: int = 30

    # MCP Server Configuration
    # Set to True to mount MCP server on FastAPI (unified deployment for Render/Vercel)
    # Set to False to run MCP server separately on port 8001 (local dev or separate services)
    # Default: True (most cloud deployments use single service)
    MOUNT_MCP_SERVER: bool = True

    # MCP server URL - automatically adjusted based on MOUNT_MCP_SERVER
    # When mounted: http://localhost:8000/mcp
    # When separate: http://localhost:8001/mcp
    MCP_SERVER_URL: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 100

    @property
    def mcp_server_url(self) -> str:
        """
        Get MCP server URL based on deployment mode.

        Returns:
            str: MCP server URL
        """
        if self.MCP_SERVER_URL:
            return self.MCP_SERVER_URL

        if self.MOUNT_MCP_SERVER:
            # Unified mode: MCP mounted on FastAPI
            return f"http://localhost:{self.API_PORT}/mcp"
        else:
            # Separate mode: MCP on port 8001
            return "http://localhost:8001/mcp"


# Create a single instance of settings
settings = Settings()