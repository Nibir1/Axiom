"""
vector_store.py
---------------
The Database Abstraction Layer.
Manages Vector Storage and executes 'Time-Aware' retrieval.
"""

from qdrant_client import QdrantClient
from qdrant_client.http import models
from src.config import settings
from typing import List, Dict, Any
import uuid
import time
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger("axiom.vector_store")

class VectorDB:
    """
    Wrapper around QdrantClient to enforce Axiom's governance patterns.
    Updated for Qdrant Client v1.10+
    """
    
    def __init__(self):
        # Initialize connection to the Qdrant Container
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )
        self.collection = settings.QDRANT_COLLECTION_NAME
        self._ensure_collection()

    def _ensure_collection(self):
        """
        Idempotent setup of the vector collection.
        """
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=models.VectorParams(
                    size=384, # Matches 'all-MiniLM-L6-v2'
                    distance=models.Distance.COSINE
                )
            )

    def upsert_document(self, text: str, vector: List[float], metadata: Dict[str, Any]) -> str:
        """
        Insert or Update a document with Governance Metadata.
        """
        doc_id = str(uuid.uuid4())
        
        # Add timestamp for filtering
        if "valid_until" in metadata and isinstance(metadata["valid_until"], datetime):
             metadata["valid_until_ts"] = int(metadata["valid_until"].timestamp())
        
        try:
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
        except Exception as e:
            logger.error(f"Failed to upsert document: {e}")
            raise e

    def search(self, query_vector: List[float], limit: int = 5) -> List[Dict]:
        """
        Lifecycle-Aware Search.
        uses client.query_points() instead of deprecated client.search()
        """
        current_ts = int(time.time())
        
        # Governance Filter: valid_until_ts > current_time
        expiry_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="valid_until_ts",
                    range=models.Range(
                        gt=current_ts
                    )
                )
            ]
        )

        try:
            # NEW SYNTAX for Qdrant v1.10+
            results = self.client.query_points(
                collection_name=self.collection,
                query=query_vector,
                query_filter=expiry_filter, 
                limit=limit
            ).points
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise e

        return [
            {
                "id": hit.id,
                "score": hit.score,
                "text": hit.payload.get("text") if hit.payload else None,
                "metadata": hit.payload or {}
            }
            for hit in results
        ]

# Global instance
vector_db = VectorDB()