"""
routes.py
---------
The Axiom API: Now with RAG (Retrieval Augmented Generation).
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from openai import AsyncOpenAI # <--- NEW
from src.config import settings
from src.models.schemas import IngestionRequest, SearchRequest, DocumentResponse
from src.core.security import PIIScrubber
from src.core.scorer import ContentScorer
from src.core.embedder import embedder
from src.core.parser import parse_pdf
from src.db.vector_store import vector_db 
from datetime import datetime, timezone, timedelta

router = APIRouter()

# Initialize Helpers
scrubber = PIIScrubber()
scorer = ContentScorer()
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# New Schema for Chat
class ChatRequest(BaseModel):
    query: str
    limit: int = 3

@router.post("/ingest/file", summary="Upload and Process PDF")
async def ingest_file(
    file: UploadFile = File(...),
    owner: str = Form(...),
    tags: str = Form("")
):
    # 1. Parse
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files are supported.")
    
    raw_text = await parse_pdf(file)
    
    # 2. Green AI Filter (UPDATED THRESHOLD)
    quality_score = scorer.calculate_score(raw_text)
    
    # RAISED TO 0.40 to ensure your 33% document fails!
    if quality_score < 0.40: 
        raise HTTPException(
            status_code=400, 
            detail=f"Governance Reject: Density {quality_score:.1%} is below the 40% threshold. Content contains too much boilerplate."
        )

    # 3. Security
    cleaned_text = scrubber.scrub(raw_text)
    
    # 4. Vectorize
    vector = embedder.embed(cleaned_text)
    
    # 5. Metadata
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    expiry = datetime.now(timezone.utc) + timedelta(days=365)
    
    metadata = {
        "owner": owner,
        "filename": file.filename,
        "tags": tag_list,
        "quality_score": quality_score,
        "valid_until": expiry,
        "cleaned_length": len(cleaned_text),
        "source_type": "file_pdf"
    }

    doc_id = vector_db.upsert_document(cleaned_text, vector, metadata)

    return {
        "status": "ingested",
        "id": doc_id,
        "quality_score": quality_score,
        "filename": file.filename,
        "pii_redacted": cleaned_text != raw_text
    }

@router.post("/chat", summary="RAG Chat with GPT-4o-mini")
async def chat_with_knowledge(payload: ChatRequest):
    """
    1. Embed query
    2. Retrieve Context
    3. Generate Answer
    """
    # 1. Retrieve
    query_vector = embedder.embed(payload.query)
    results = vector_db.search(query_vector=query_vector, limit=payload.limit)
    
    if not results:
        return {"answer": "I couldn't find any internal documents matching your query.", "context": []}

    # 2. Construct Prompt
    context_text = "\n\n".join([f"Source ({r['metadata'].get('filename', 'Doc')}): {r['text']}" for r in results])
    
    system_prompt = """You are Axiom, UPM's AI Assistant. 
    Answer the user query using ONLY the provided context. 
    If the answer is not in the context, say you don't know. 
    Keep answers professional and concise."""

    user_prompt = f"Context:\n{context_text}\n\nQuestion: {payload.query}"

    # 3. Call OpenAI (GPT-4o-mini)
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1 # Low temperature for factual accuracy
    )
    
    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "context": results # Return sources for citation
    }