"""
main.py
-------
Entry point for the Axiom Knowledge Governance Engine.
Initializes the FastAPI application and defines global middleware/events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.api.routes import router as api_router

# Initialize the application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Green AI knowledge pipeline for high-fidelity RAG retrieval.",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, allow all. In prod, list specific domains.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "active",
        "system": "Axiom Knowledge Engine",
        "version": "0.1.0"
    }

@app.get("/")
async def root():
    return {"message": "Welcome to Axiom - UPM's Knowledge Governance Layer"}