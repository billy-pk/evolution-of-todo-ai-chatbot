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


# Create a single instance of settings
settings = Settings()