"""
routes.py
---------
The primary API endpoints for the Axiom engine.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from src.models.schemas import IngestionRequest, SearchRequest, DocumentResponse
from src.core.security import PIIScrubber
from src.core.scorer import ContentScorer
from src.core.embedder import embedder
from src.db.vector_store import vector_db  # <--- Ensure this imports from vector_store
from datetime import datetime, timezone, timedelta

router = APIRouter()

# Initialize Helpers
scrubber = PIIScrubber()
scorer = ContentScorer()

@router.post("/ingest", summary="Ingest and Secure a Document")
async def ingest_document(payload: IngestionRequest):
    # 1. Green AI Filter
    quality_score = scorer.calculate_score(payload.text)
    
    if quality_score < 0.1: # Threshold 0.1 for demo
        raise HTTPException(
            status_code=400, 
            detail=f"Document rejected. Low information density score: {quality_score}."
        )

    # 2. Security Layer
    cleaned_text = scrubber.scrub(payload.text)
    
    # 3. Vectorization
    vector = embedder.embed(cleaned_text)
    
    # 4. Lifecycle Management
    expiry = payload.valid_until
    if not expiry:
        expiry = datetime.now(timezone.utc) + timedelta(days=365)

    metadata = {
        "owner": payload.owner,
        "tags": payload.tags,
        "quality_score": quality_score,
        "valid_until": expiry,
        "original_length": len(payload.text),
        "cleaned_length": len(cleaned_text)
    }

    # 5. Storage
    doc_id = vector_db.upsert_document(
        text=cleaned_text,
        vector=vector,
        metadata=metadata
    )

    return {
        "status": "ingested",
        "id": doc_id,
        "quality_score": quality_score,
        "pii_redacted": cleaned_text != payload.text
    }


@router.post("/search", response_model=List[DocumentResponse], summary="Semantic Search")
async def search_documents(payload: SearchRequest):
    # 1. Embed Query
    query_vector = embedder.embed(payload.query)
    
    # 2. Search DB
    results = vector_db.search(query_vector=query_vector, limit=payload.limit)
    
    # 3. Explicit conversion (optional, but good for debugging)
    return [
        DocumentResponse(
            id=str(r["id"]),
            score=r["score"],
            text=r["text"],
            metadata=r["metadata"]
        ) for r in results
    ]