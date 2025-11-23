import pytest
from src.models.verification_request import VerificationRequest
from src.models.triple import Triple

def test_verification_request_creation():
    triple = Triple(subject="s", predicate="p", object="o")
    request = VerificationRequest(id="123", triple=triple, certainty_score=0.5)
    
    assert request.id == "123"
    assert request.triple == triple
    assert request.certainty_score == 0.5
