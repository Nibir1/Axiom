"""
scorer.py
---------
Evaluates the 'Information Density' of a text document.
Used to implement "Green AI" governance: we do not waste energy 
indexing low-value content (headers, footers, boilerplate).
"""

import spacy
from typing import Dict

class ContentScorer:
    """
    Calculates a utility score for text content.
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            raise RuntimeError(f"Spacy model '{model_name}' not found.")

    def calculate_score(self, text: str) -> float:
        """
        Computes the Information Density Score (0.0 to 1.0).
        
        Algorithm:
        1. Tokenize text.
        2. Count 'Content Tokens' (Nouns, Verbs, Adjectives) vs Total Tokens.
        3. Penalize extremely short texts.
        """
        if not text or len(text.strip()) < 50:
            return 0.0  # Reject empty or tiny snippets

        doc = self.nlp(text)
        
        total_tokens = len(doc)
        if total_tokens == 0:
            return 0.0

        content_tokens = 0
        for token in doc:
            # We value semantically rich words
            if not token.is_stop and not token.is_punct and not token.is_space:
                if token.pos_ in ["NOUN", "VERB", "ADJ", "PROPN"]:
                    content_tokens += 1

        # Calculate density ratio
        density = content_tokens / total_tokens

        # Normalization: Pure lists of keywords might have density 1.0, 
        # but regular sentences usually hover around 0.4 - 0.6.
        # We cap the score at 1.0.
        
        return round(density, 4)

    def is_passable(self, text: str, threshold: float = 0.3) -> bool:
        """
        Boolean helper to accept/reject content based on config threshold.
        """
        return self.calculate_score(text) >= threshold