"""
config.py
---------
Centralized configuration management for the Axiom Knowledge Engine.
Uses Pydantic BaseSettings (v2) to validate environment variables on startup.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration settings.
    """

    # --- Core App Settings ---
    PROJECT_NAME: str = "Axiom Knowledge Engine"
    API_V1_STR: str = "/api/v1"

    DEBUG_MODE: bool = False
    SECRET_KEY: str = "super-secret-key"

    # --- Vector Database (Qdrant) ---
    # In Docker, this should match the service name
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "upm_knowledge_base"

    # --- LLM / OpenAI Configuration ---
    # Required: must be provided via .env
    OPENAI_API_KEY: str

    class Config:
        # Read environment variables from .env
        env_file = ".env"
        case_sensitive = True
        # Allow extra .env fields without raising errors
        extra = "ignore"


# Global settings instance
settings = Settings()
