import pytest
from src.services.verification_service import VerificationService
from src.models.verification_request import VerificationRequest
from src.models.triple import Triple

def test_add_verification():
    service = VerificationService()
    triple = Triple(subject="s", predicate="p", object="o")
    request = VerificationRequest(id="1", triple=triple, certainty_score=0.5)
    
    service.add(request)
    assert len(service.get_pending()) == 1
    assert service.get_pending()[0] == request

def test_resolve_verification():
    service = VerificationService()
    triple = Triple(subject="s", predicate="p", object="o")
    request = VerificationRequest(id="1", triple=triple, certainty_score=0.5)
    service.add(request)
    
    service.resolve("1", approved=True)
    assert len(service.get_pending()) == 0
