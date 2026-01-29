"""
config.py
---------
Centralized configuration management for the Axiom engine.
Uses Pydantic BaseSettings to validate environment variables on startup.
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application configuration settings.
    """
    PROJECT_NAME: str = "Axiom Knowledge Engine"
    API_V1_STR: str = "/api/v1"
    
    # --- ADDED THESE TWO FIELDS ---
    # They act as placeholders for the values coming from your .env file
    DEBUG_MODE: bool = False 
    SECRET_KEY: str = "super-secret-key" 
    # ------------------------------

    # Vector DB Config
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "upm_knowledge_base"

    class Config:
        # Pydantic V2 config to read from .env file
        env_file = ".env"
        case_sensitive = True
        # Optional: If you want to allow extra fields in .env without errors, uncomment below:
        # extra = "ignore" 

# Global instance to be imported across the app
settings = Settings()