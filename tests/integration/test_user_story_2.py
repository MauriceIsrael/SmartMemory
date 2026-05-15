import pytest
import asyncio
from pathlib import Path
from smart_memory.server import SemanticMemoryServer
from smart_memory.config import SemanticMemoryConfig
from rdflib import Namespace
from smart_memory.tools.add_memory import add_memory
from smart_memory.tools.load_custom_rule import load_custom_rule
from smart_memory.tools.query_memory import query_memory

@pytest.fixture
def temp_config(tmp_path):
    """Fixture to create a temporary configuration for testing."""
    # Create temporary directories for rules
    user_rules_dir = tmp_path / "user_rules"
    user_rules_dir.mkdir()
    
    # Create a temporary file for persistence
    persistence_path = tmp_path / "knowledge_graph.ttl"

    # Return a new config object
    return SemanticMemoryConfig(
        user_rules_dir=user_rules_dir,
        persistence_path=persistence_path,
        log_level="DEBUG"
    )

@pytest.mark.asyncio
async def test_user_story_2_integration(temp_config, monkeypatch):
    """
    Integration test for User Story 2:
    - Load a custom rule.
    - Add facts that trigger the rule.
    - Verify that the inferred facts are in the graph.
    """
    # Patch the global config object so all modules use the temp config
    monkeypatch.setattr("smart_memory.config.config", temp_config)
    monkeypatch.setattr("smart_memory.server.config", temp_config)
    monkeypatch.setattr("smart_memory.knowledge.persistence.config", temp_config)

    server = SemanticMemoryServer()
    await server.startup()

    EX = Namespace("http://example.org/")
    USER_NS = Namespace("http://semanticmemory.org/user#")
    SCHEMA = Namespace("https://schema.org/")

    # 1. Load a custom rule
    rule_id = "test_rule"
    rule_content = f"""
        PREFIX schema: <{SCHEMA}>
        PREFIX ex: <{EX}>
        CONSTRUCT {{ ?person ex:isHappy "true"^^xsd:boolean . }}
        WHERE {{
            ?person schema:worksFor ex:HappyCompany .
        }}
    """
    await load_custom_rule(
        {"rule_id": rule_id, "rule_content": rule_content, "description": "A rule to infer happiness."},
        server.rule_engine, server.graph
    )

    # 2. Add facts
    await add_memory(
        {"input": f":Alice <https://schema.org/worksFor> <{EX}HappyCompany> .", "format": "triple_notation"},
        server.graph, server.reasoner, server.triple_extractor, server.rule_engine,
        inference_manager=server.inference_manager
    )
    
    # Wait for inference
    await asyncio.wait_for(server.inference_manager.wait_until_idle(), timeout=5.0)

    # 3. Query for the inferred fact directly on the graph
    # Note: :Alice maps to USER_NS.Alice
    sparql_query = f"""
        PREFIX ex: <{EX}>
        ASK WHERE {{ <{USER_NS}Alice> ex:isHappy true . }}
    """
    is_happy = bool(server.graph.graph.query(sparql_query))
    assert is_happy, "The custom rule should have inferred that Alice is happy."

    await server.shutdown()

