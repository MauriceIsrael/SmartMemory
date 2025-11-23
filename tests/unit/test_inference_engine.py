import pytest
from unittest.mock import MagicMock
from src.services.inference_engine import InferenceEngine
from src.models.inference_rule import InferenceRule
from src.models.triple import Triple
from src.models.knowledge_graph import KnowledgeGraph
from src.services.verification_service import VerificationService
from rdflib import URIRef

def test_infer_returns_triples():
    # Setup rule: if (?s p1 ?o) -> (?s p2 ?o)
    condition = Triple(subject="?s", predicate="p1", object="?o")
    conclusion = Triple(subject="?s", predicate="p2", object="?o")
    rule = InferenceRule(name="test_rule", conditions=[condition], conclusion=conclusion)
    
    mock_verification_service = MagicMock(spec=VerificationService)
    engine = InferenceEngine(rules=[rule], verification_service=mock_verification_service, certainty_threshold=0.5)
    
    # Setup KnowledgeGraph with one matching triple
    kg = KnowledgeGraph()
    # We need to manually add to explicit_graph because add_explicit might trigger inference loop if we are not careful, 
    # but here we are testing engine.infer isolated.
    kg.explicit_graph.add((URIRef("s1"), URIRef("p1"), URIRef("o1")))
    
    inferred = engine.infer(kg)
    
    assert len(inferred) == 1
    assert inferred[0].subject == "s1"
    assert inferred[0].predicate == "p2"
    assert inferred[0].object == "o1"

def test_infer_triggers_verification():
    # Setup rule
    condition = Triple(subject="?s", predicate="p1", object="?o")
    conclusion = Triple(subject="?s", predicate="p2", object="?o")
    rule = InferenceRule(name="test_rule", conditions=[condition], conclusion=conclusion)
    
    mock_verification_service = MagicMock(spec=VerificationService)
    # Set threshold higher than the mock score (0.7)
    engine = InferenceEngine(rules=[rule], verification_service=mock_verification_service, certainty_threshold=0.8)
    
    kg = KnowledgeGraph()
    kg.explicit_graph.add((URIRef("s1"), URIRef("p1"), URIRef("o1")))
    
    inferred = engine.infer(kg)
    
    # Should not return triple, but call verification service
    assert len(inferred) == 0
    mock_verification_service.add.assert_called_once()
