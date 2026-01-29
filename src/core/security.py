"""
security.py
-----------
Handles the redaction of Personally Identifiable Information (PII) 
from text before it enters the storage layer.

Uses a hybrid approach:
1. Spacy NER for semantic entities (Names, Organizations).
2. Regex for structural entities (Emails, Phone Numbers).
"""

import spacy
import re
from typing import List, Tuple

class PIIScrubber:
    """
    Sanitizes text by detecting and redacting sensitive information.
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the NLP engine.
        
        Args:
            model_name: The Spacy model to load. defaults to 'en_core_web_sm'.
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            raise RuntimeError(
                f"Spacy model '{model_name}' not found. "
                f"Please run: python -m spacy download {model_name}"
            )
        
        # Pre-compile regex for performance (Sustainability: efficient compute)
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\b\+?[0-9]{10,15}\b') # Simple international format

    def scrub(self, text: str) -> str:
        """
        Main entry point. Redacts PII from the input text.
        
        Returns:
            str: The sanitized text with PII replaced by <REDACTED_TYPE>.
        """
        if not text:
            return ""

        # 1. Regex Redactions (Fastest first)
        text = self.email_pattern.sub("<REDACTED_EMAIL>", text)
        text = self.phone_pattern.sub("<REDACTED_PHONE>", text)

        # 2. NLP Entity Redactions (Context aware)
        doc = self.nlp(text)
        
        # We collect replacements to apply. 
        # Strategy: Identify spans to redact.
        entities_to_redact = []
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG"]:
                entities_to_redact.append((ent.start_char, ent.end_char, ent.label_))

        # Apply redactions in reverse order to preserve indices
        # (If we replace from start, subsequent indices shift)
        entities_to_redact.sort(key=lambda x: x[0], reverse=True)

        for start, end, label in entities_to_redact:
            replacement = f"<{label}>"
            text = text[:start] + replacement + text[end:]

        return text