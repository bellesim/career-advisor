"""
Application Configuration

Manages environment variables and application settings using Pydantic.
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via environment variables.
    For example, PROJECT_NAME can be set via the PROJECT_NAME env var.
    """
    
    # Project metadata
    PROJECT_NAME: str = "Career Advisor API"
    PROJECT_DESCRIPTION: str = "AI-powered career gap analysis and improvement planning"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=True, description="Debug mode")
    
    # API configuration
    API_V1_STR: str = "/api/v1"
    
    # CORS configuration
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
        ],
        description="Allowed CORS origins"
    )
    
    # Supabase configuration
    SUPABASE_URL: str = Field(default="", description="Supabase project URL")
    SUPABASE_KEY: str = Field(default="", description="Supabase anon key (browser/public)")
    SUPABASE_SERVICE_KEY: str = Field(default="", description="Supabase service role key (server-side, bypasses RLS)")
    SUPABASE_JWT_SECRET: str = Field(default="", description="Supabase JWT secret for token verification")
    
    # OpenRouter configuration
    OPENROUTER_API_KEY: str = Field(default="", description="OpenRouter API key")
    OPENROUTER_MODEL: str = Field(default="anthropic/claude-sonnet-4-5", description="Model to use via OpenRouter")
    
    # Brave Search MCP configuration
    BRAVE_SEARCH_API_KEY: Optional[str] = Field(default=None, description="Brave Search API key")
    
    # File upload configuration
    MAX_UPLOAD_SIZE_MB: int = Field(default=10, description="Maximum file upload size in MB")
    ALLOWED_RESUME_FORMATS: List[str] = Field(
        default=["pdf", "docx"],
        description="Allowed resume file formats"
    )
    
    # Session configuration
    GUEST_SESSION_EXPIRY_HOURS: int = Field(default=24, description="Guest session expiry in hours")
    AUTH_SESSION_EXPIRY_DAYS: int = Field(default=7, description="Authenticated session expiry in days")
    
    # Rate limiting configuration
    RATE_LIMIT_UPLOADS_PER_HOUR: int = Field(default=10, description="Max uploads per hour per IP")
    RATE_LIMIT_ANALYSIS_PER_HOUR: int = Field(default=5, description="Max analysis requests per hour per user")
    RATE_LIMIT_API_PER_MINUTE: int = Field(default=100, description="Max API requests per minute per user")
    
    # Cache configuration
    CACHE_PDF_TTL_SECONDS: int = Field(default=3600, description="PDF cache TTL in seconds (1 hour)")
    CACHE_SEARCH_TTL_SECONDS: int = Field(default=86400, description="Search results cache TTL in seconds (24 hours)")
    
    # Performance configuration
    ANALYSIS_TIMEOUT_SECONDS: int = Field(default=60, description="Analysis timeout in seconds")
    QUESTIONS_TIMEOUT_SECONDS: int = Field(default=10, description="Question generation timeout in seconds")
    PDF_GENERATION_TIMEOUT_SECONDS: int = Field(default=10, description="PDF generation timeout in seconds")
    
    # Retry configuration
    BRAVE_SEARCH_MAX_RETRIES: int = Field(default=3, description="Max retries for Brave Search API")
    DATABASE_MAX_RETRIES: int = Field(default=2, description="Max retries for database queries")
    STORAGE_MAX_RETRIES: int = Field(default=2, description="Max retries for file uploads")
    
    # Security configuration
    PASSWORD_MIN_LENGTH: int = Field(default=8, description="Minimum password length")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


# Create global settings instance
settings = Settings()
