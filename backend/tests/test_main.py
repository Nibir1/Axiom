"""
test_main.py
------------
Comprehensive Integration Tests for Axiom Backend.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.core.security import PIIScrubber
from src.core.scorer import ContentScorer

# ------------------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client():
    """
    Creates an AsyncClient for the FastAPI app.
    We use ASGITransport to test the app directly without a running server.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

# ------------------------------------------------------------------------------
# Integration Tests (API Endpoints)
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health_check(client):
    """Verify system heartbeat."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "active"

@pytest.mark.asyncio
async def test_ingest_text_valid(client):
    """Test Happy Path: High-quality text ingestion."""
    payload = {
        "text": "UPM Biofore is leading the forest-based bioindustry into a sustainable, innovation-driven future.",
        "owner": "test_user@upm.com",
        "tags": ["strategy", "unit_test"]
    }
    response = await client.post("/api/v1/ingest", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ingested"
    assert "id" in data
    assert data["quality_score"] >= 0.1 

@pytest.mark.asyncio
async def test_ingest_text_governance_rejection(client):
    """Test Green AI Path: Low-quality boilerplate should be rejected."""
    
    # <--- CRITICAL CHANGE IS HERE --->
    # We use purely stopwords (the, a, and) and punctuation.
    # This guarantees a Density Score of 0.0, which forces a 400 Bad Request.
    # CHANGED: Added more dots/commas to exceed min_length=50 constraint
    payload = {
        "text": "the a an and or but if with at from ... ,,, ;;; ... ... ... ... ... ...", 
        "owner": "spambot",
        "tags": []
    }
    # <--- END CRITICAL CHANGE --->
    
    response = await client.post("/api/v1/ingest", json=payload)
    
    # Assertions
    assert response.status_code == 400
    assert "Document rejected" in response.json()["detail"]

# ------------------------------------------------------------------------------
# Unit Tests (Core Logic)
# ------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pii_scrubber_allowlist():
    """Unit Test: Verify 'UPM' is preserved while other PII is removed."""
    scrubber = PIIScrubber()
    text = "Contact John Doe at UPM Biofuels regarding the project."
    
    clean_text = scrubber.scrub(text)
    
    # Assertions
    assert "<PERSON>" in clean_text  # John Doe should be gone
    assert "UPM Biofuels" in clean_text  # Internal unit should stay (Allow List)

@pytest.mark.asyncio
async def test_content_scorer_logic():
    """Unit Test: Verify scoring algorithm."""
    scorer = ContentScorer()
    
    good_text = "The renewable diesel market is growing rapidly due to decarbonization targets."
    bad_text = "1. 2. 3. ... ,,, !!!"
    
    assert scorer.calculate_score(good_text) > scorer.calculate_score(bad_text)