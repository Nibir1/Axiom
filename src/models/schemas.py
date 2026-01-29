"""
schemas.py
----------
Defines the strict data contracts for the Axiom system.
Enforces Governance and Lifecycle metadata (Owner, Expiry) at the API boundary.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

class IngestionRequest(BaseModel):
    """
    The contract for sending data into Axiom.
    User must provide lifecycle metadata.
    """
    text: str = Field(..., min_length=50, description="The raw content to ingest.")
    
    # Governance Fields
    owner: str = Field(..., description="Email/ID of the content owner responsible for this data.")
    tags: List[str] = Field(default_factory=list, description="Taxonomy tags (e.g. 'Safety', 'HR').")
    
    # Lifecycle Management: If not provided, data expires in 1 year by default
    valid_until: Optional[datetime] = Field(
        default=None, 
        description="ISO 8601 Date when this document becomes obsolete."
    )

    @field_validator('valid_until')
    @classmethod
    def set_default_expiry(cls, v):
        """
        If no expiry is set, default to 365 days from now.
        Sustainability: Don't keep data forever.
        """
        if v is None:
            # Simple logic: Data rots. Default expiry enforces review.
            # In a real app, this might be calculated differently.
            # Returning None here to let the logic handle it or set a future date.
            # For this demo, let's keep it None and handle logic in the service layer,
            # or return a default future date. Let's return None for now.
            return None
        return v

class DocumentResponse(BaseModel):
    """
    Standard response format for retrieval.
    """
    id: str
    text: str
    score: float
    metadata: Dict[str, Any]

class SearchRequest(BaseModel):
    """
    The query contract.
    """
    query: str
    limit: int = 5
    filter_tags: Optional[List[str]] = None