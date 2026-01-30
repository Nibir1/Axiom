"""
security.py
-----------
Handles the redaction of Personally Identifiable Information (PII).
Updated with an ALLOW_LIST to prevent redacting UPM's own business units.
"""

import spacy
import re
from typing import List, Tuple

class PIIScrubber:
    """
    Sanitizes text by detecting and redacting sensitive information.
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            # Fallback if not downloaded (though Dockerfile handles this)
            raise RuntimeError(f"Spacy model '{model_name}' not found.")
        
        # Regex for structural PII
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\b\+?[0-9]{10,15}\b') 

        # <--- NEW: Internal terms to NEVER redact --->
        self.allow_list = ["UPM", "Raflatac", "Biofuels", "Biofore"]

    def scrub(self, text: str) -> str:
        """
        Redacts PII but preserves Allow-Listed terms.
        """
        if not text:
            return ""

        # 1. Regex Redactions (Emails/Phones are always PII)
        text = self.email_pattern.sub("<REDACTED_EMAIL>", text)
        text = self.phone_pattern.sub("<REDACTED_PHONE>", text)

        # 2. NLP Entity Redactions
        doc = self.nlp(text)
        
        entities_to_redact = []
        for ent in doc.ents:
            # Check if this entity is in our Allow List
            # If "UPM" is in the entity text (e.g. "UPM Biofuels"), SKIP redaction.
            if any(allowed in ent.text for allowed in self.allow_list):
                continue

            if ent.label_ in ["PERSON", "ORG", "GPE"]: # GPE = Geopolitical Entity (Countries/Cities)
                entities_to_redact.append((ent.start_char, ent.end_char, ent.label_))

        # Apply redactions in reverse order
        entities_to_redact.sort(key=lambda x: x[0], reverse=True)

        for start, end, label in entities_to_redact:
            replacement = f"<{label}>"
            text = text[:start] + replacement + text[end:]

        return text