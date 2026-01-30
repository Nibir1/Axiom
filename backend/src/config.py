"""
config.py
---------
Centralized configuration management for the Axiom engine.
Updated for Pydantic V2 and robust testing support.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Axiom Knowledge Engine"
    API_V1_STR: str = "/api/v1"
    
    DEBUG_MODE: bool = False 
    SECRET_KEY: str = "super-secret-key" 

    # Vector DB Config
    # Default to localhost so local 'pytest' runs work without Docker networking
    QDRANT_HOST: str = "localhost" 
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "upm_knowledge_base"

    # LLM Config
    # Default to a placeholder so 'import app' doesn't crash during tests
    OPENAI_API_KEY: str = "sk-placeholder-key-for-tests"

    # Modern Pydantic V2 Configuration
    model_config = SettingsConfigDict(
        # Look for .env in the current dir OR in the backend/ dir
        env_file=[".env", "backend/.env"], 
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=True
    )

settings = Settings()