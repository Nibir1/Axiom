"""
embedder.py
-----------
Converts text into vector representations.
Uses a quantized, local model to ensure low latency and zero data leakage.
"""

from sentence_transformers import SentenceTransformer
from typing import List

class GreenEmbedder:
    """
    Lightweight embedding wrapper.
    Model: all-MiniLM-L6-v2 (384 dimensions).
    Why: It's fast, small (80MB), and accurate enough for internal docs.
    """
    
    def __init__(self):
        # Load model once at startup
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def embed(self, text: str) -> List[float]:
        """
        Generates a vector embedding for the given text.
        """
        if not text:
            return []
        
        # Helper to convert numpy array to standard list
        embedding = self.model.encode(text)
        return embedding.tolist()

# Singleton instance
embedder = GreenEmbedder()