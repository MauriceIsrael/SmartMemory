"""
Integration tests for verify_inference tool.
"""

import pytest
import pytest_asyncio
from semantic_memory.config import SemanticMemoryConfig
from semantic_memory.knowledge.graph import ProvenanceGraph
from semantic_memory.tools.verify_inference import verify_inference
from semantic_memory.tools.add_memory import add_memory
from semantic_memory.nlp import TripleExtractor


@pytest.fixture
def temp_config(tmp_path):
    """Test configuration."""
    return SemanticMemoryConfig(
        persistence_path=tmp_path / "test_graph.ttl",
        log_level="INFO",
        force_offline=True,
        enable_owl_reasoning=False,
        load_ontologies=False,
    )


@pytest_asyncio.fixture
async def graph_with_facts(temp_config, monkeypatch):
    """Graph with some test facts."""
    monkeypatch.setattr("semantic_memory.config.config", temp_config)
    
    graph = ProvenanceGraph()
    extractor = TripleExtractor()
    
    # Add explicit fact
    graph.add_triple_with_provenance(
        subject="http://semanticmemory.org/user#User",
        predicate="http://xmlns.com/foaf/0.1/knows",
        obj="http://semanticmemory.org/user#Daniel",
        source="user",
        confidence=1.0,
    )
    
    return graph


@pytest.mark.asyncio
async def test_verify_explicit_fact(graph_with_facts):
    """Test verifying an explicitly added fact."""
    result = await verify_inference(
        {
            "subject": ":User",
            "predicate": "foaf:knows",
            "object": ":Daniel"
        },
        graph_with_facts
    )
    
    assert len(result) == 1
    text = result[0].text
    assert "✓ Formally proven" in text
    assert "Explicitly added by user" in text


@pytest.mark.asyncio
async def test_verify_nonexistent_fact(graph_with_facts):
    """Test verifying a fact that doesn't exist."""
    result = await verify_inference(
        {
            "subject": ":User",
            "predicate": "foaf:knows",
            "object": ":Claire"
        },
        graph_with_facts
    )
    
    assert len(result) == 1
    text = result[0].text
    assert "No formal proof found" in text
    assert "suggestion" in text.lower() or "consider" in text.lower()


@pytest.mark.asyncio
async def test_verify_inferred_fact(temp_config, monkeypatch):
    """Test verifying a fact that was inferred by a rule."""
    monkeypatch.setattr("semantic_memory.config.config", temp_config)
    
    from semantic_memory.inference.rule_engine import RuleEngine
    import os
    
    graph = ProvenanceGraph()
    extractor = TripleExtractor()
    
    # Initialize rule engine with default rules
    rules_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "src", "rules", "defaults"
    )
    rule_engine = RuleEngine(graph)
    await rule_engine.load_rules_from_directory(rules_dir)
    
    # Add fact that will trigger inference
    await add_memory(
        {"input": ":User foaf:knows :Claire"},
        graph,
        None,
        extractor,
        rule_engine,
        None,
    )
    
    # Execute rules to infer symmetry
    await rule_engine.execute_all_rules()
    
    # Verify the inferred fact
    result = await verify_inference(
        {
            "subject": ":Claire",
            "predicate": "foaf:knows",
            "object": ":User"
        },
        graph
    )
    
    assert len(result) == 1
    text = result[0].text
    assert "✓ Formally proven" in text
    assert "Inferred by rule" in text
    assert "social_symmetry" in text.lower() or "symmetry" in text.lower()
