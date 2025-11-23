import pytest
from unittest.mock import MagicMock
from src.models.knowledge_graph import KnowledgeGraph
from src.models.triple import Triple
from src.services.inference_engine import InferenceEngine

def test_add_explicit_adds_triple():
    kg = KnowledgeGraph()
    triple = Triple(subject=":s", predicate=":p", object=":o")
    kg.add_explicit(triple)
    
    assert len(kg.explicit_graph) == 1
    assert (None, None, None) in kg.explicit_graph

def test_add_explicit_triggers_inference():
    mock_inference_engine = MagicMock(spec=InferenceEngine)
    mock_inference_engine.infer.return_value = [Triple(subject=":s", predicate=":p2", object=":o")]
    
    kg = KnowledgeGraph(inference_engine=mock_inference_engine)
    triple = Triple(subject=":s", predicate=":p", object=":o")
    kg.add_explicit(triple)
    
    mock_inference_engine.infer.assert_called_once_with(kg)
    assert len(kg.inferred_graph) == 1

def test_add_inferred_adds_triple():
    kg = KnowledgeGraph()
    triple = Triple(subject=":s", predicate=":p", object=":o")
    kg.add_inferred(triple)
    
    assert len(kg.inferred_graph) == 1
