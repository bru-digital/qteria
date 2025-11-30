"""
Application configuration management.
Loads settings from environment variables using pydantic-settings.
"""
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

# Find project root (directory containing .env)
def find_project_root() -> Path:
    """Find project root by looking for .env file."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".env").exists():
            return parent
    return Path.cwd()

PROJECT_ROOT = find_project_root()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Project Info
    PROJECT_NAME: str = "Qteria API"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/v1"
    DESCRIPTION: str = (
        "AI-driven document pre-assessment platform for TIC industry. "
        "Transform manual compliance checks into AI-powered assessments "
        "with evidence-based results in <10 minutes."
    )

    # Environment
    ENVIRONMENT: str = Field(default="development", alias="PYTHON_ENV")

    # Database
    DATABASE_URL: str = Field(
        ..., description="PostgreSQL database URL (pooled connection)"
    )
    DATABASE_URL_UNPOOLED: str = Field(
        default="", description="PostgreSQL database URL (direct connection for migrations)"
    )

    # Redis (for rate limiting, caching, and background jobs)
    REDIS_URL: str = Field(
        default="", description="Redis connection URL (e.g., redis://localhost:6379/0)"
    )

    # Security
    JWT_SECRET: str = Field(..., description="Secret key for JWT token signing")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token expiration in minutes"
    )

    # CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:3001",
        description="Comma-separated list of allowed CORS origins",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # AI Configuration
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API key for Claude")
    CLAUDE_MODEL: str = Field(
        default="claude-3-5-sonnet-20241022", description="Claude model to use"
    )
    MAX_AI_RETRIES: int = Field(default=3, description="Max retries for AI API calls")

    class Config:
        # Load .env from project root
        env_file = str(PROJECT_ROOT / ".env")
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Create global settings instance
settings = Settings()
