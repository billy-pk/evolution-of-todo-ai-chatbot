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
    MCP_SERVER_URL: str = "http://localhost:8000/mcp"

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 100


# Create a single instance of settings
settings = Settings()