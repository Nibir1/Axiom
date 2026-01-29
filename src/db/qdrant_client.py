"""
qdrant_client.py
----------------
The Database Abstraction Layer.
Manages Vector Storage and executes 'Time-Aware' retrieval.
"""

from qdrant_client import QdrantClient
from qdrant_client.http import models
from src.config import settings
from typing import List, Dict, Any, Optional
import uuid
import time
from datetime import datetime, timezone

class VectorDB:
    """
    Wrapper around QdrantClient to enforce Axiom's governance patterns.
    """
    
    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        self.collection = settings.QDRANT_COLLECTION_NAME
        self._ensure_collection()

    def _ensure_collection(self):
        """
        Idempotent setup of the vector collection.
        Uses Cosine similarity (standard for text).
        """
        try:
            self.client.get_collection(self.collection)
        except Exception:
            # Collection does not exist, create it.
            # Vector size 384 is standard for 'all-MiniLM-L6-v2' (fast, light model).
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=models.VectorParams(
                    size=384, 
                    distance=models.Distance.COSINE
                )
            )

    def upsert_document(self, 
                        text: str, 
                        vector: List[float], 
                        metadata: Dict[str, Any]) -> str:
        """
        Insert or Update a document with Governance Metadata.
        """
        doc_id = str(uuid.uuid4())
        
        # We store the payload. 
        # Note: 'valid_until' should be stored as timestamp (int) for efficient range filtering in Qdrant
        if "valid_until" in metadata and isinstance(metadata["valid_until"], datetime):
             metadata["valid_until_ts"] = int(metadata["valid_until"].timestamp())
        
        self.client.upsert(
            collection_name=self.collection,
            points=[
                models.PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload={
                        "text": text,
                        **metadata
                    }
                )
            ]
        )
        return doc_id

    def search(self, query_vector: List[float], limit: int = 5) -> List[Dict]:
        """
        Lifecycle-Aware Search.
        
        Automatically filters out documents where 'valid_until' < current_time.
        This prevents the AI from reading expired policies.
        """
        current_ts = int(time.time())
        
        # Define the Filter: 
        # 1. Must NOT be expired (valid_until_ts > current_ts OR valid_until_ts is null)
        # Note: In a strict system, we might mandate expiry. Here we allow null (no expiry).
        
        expiry_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="valid_until_ts",
                    range=models.Range(
                        gt=current_ts # Greater than now = in the future = valid
                    )
                )
            ]
        )

        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            query_filter=expiry_filter, 
            limit=limit
        )

        return [
            {
                "id": hit.id,
                "score": hit.score,
                "text": hit.payload.get("text"),
                "metadata": hit.payload
            }
            for hit in results
        ]

# Global instance
vector_db = VectorDB()