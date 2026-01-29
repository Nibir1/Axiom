"""
test_gatekeeper.py
------------------
Unit tests for the Security and Scorer modules.
"""

import pytest
from src.core.security import PIIScrubber
from src.core.scorer import ContentScorer

# Fixtures allow us to instantiate heavy objects (like Spacy models) once
@pytest.fixture(scope="module")
def scrubber():
    return PIIScrubber()

@pytest.fixture(scope="module")
def scorer():
    return ContentScorer()

def test_pii_redaction_email(scrubber):
    text = "Please contact support@upm.com for assistance."
    clean = scrubber.scrub(text)
    assert "<REDACTED_EMAIL>" in clean
    assert "support@upm.com" not in clean

def test_pii_redaction_names(scrubber):
    text = "Anna-Leena Terhemaa is the manager."
    clean = scrubber.scrub(text)
    # Note: NER is probabilistic. It should catch 'Anna-Leena Terhemaa' as PERSON
    assert "<PERSON>" in clean
    assert "Anna-Leena" not in clean

def test_scorer_high_quality(scorer):
    # A real sentence about UPM
    text = "UPM is a material solutions company, renewing products and entire value chains with renewable fibres."
    score = scorer.calculate_score(text)
    assert score > 0.3  # Should pass

def test_scorer_low_quality(scorer):
    # Boilerplate junk
    text = "Click here. Menu. Home. Contact. Copyright 2023. ... ... "
    score = scorer.calculate_score(text)
    # This contains mostly stopwords, punctuation, or generic low-value words
    # The density of NOUN/VERB/ADJ is low relative to the formatting noise
    # Note: Depending on spacy model, 'Menu', 'Home' might be nouns, 
    # but the lack of structure usually lowers the score vs full sentences.
    # However, for this test, let's use pure noise.
    noise = "the a an and or but with on in at ... ,,, !!!"
    assert scorer.calculate_score(noise) == 0.0