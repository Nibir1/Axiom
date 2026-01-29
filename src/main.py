"""
main.py
-------
Entry point for the Axiom Knowledge Governance Engine.
Initializes the FastAPI application and defines global middleware/events.
"""

from fastapi import FastAPI
from src.config import settings

# Initialize the application with metadata
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Green AI knowledge pipeline for high-fidelity RAG retrieval.",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.get("/health", tags=["System"])
async def health_check():
    """
    Basic Health Check Endpoint.
    
    Used by container orchestrators (K8s/Docker) to verify the service is alive.
    Returns:
        dict: Status message indicating the API is operational.
    """
    return {
        "status": "active",
        "system": "Axiom Knowledge Engine",
        "version": "0.1.0"
    }

@app.get("/")
async def root():
    """
    Root endpoint redirect or welcome message.
    """
    return {"message": "Welcome to Axiom - UPM's Knowledge Governance Layer"}

# Note: In a real deployment, Uvicorn runs this app.
# Example: uvicorn src.main:app --reload