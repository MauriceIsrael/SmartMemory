import pytest
import asyncio
from pathlib import Path
from semantic_memory.server import SemanticMemoryServer
from semantic_memory.config import SemanticMemoryConfig
from rdflib import Namespace
from semantic_memory.tools.add_memory import add_memory
from semantic_memory.tools.load_custom_rule import load_custom_rule
from semantic_memory.tools.query_memory import query_memory

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
    monkeypatch.setattr("semantic_memory.config.config", temp_config)

    server = SemanticMemoryServer()
    await server.startup() # register_tools is called in startup

    EX = Namespace("http://example.org/")
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
        {"input": f":Alice schema:worksFor <{EX}HappyCompany> .", "format": "triple_notation"},
        server.graph, server.reasoner, server.triple_extractor, server.rule_engine
    )

    # 3. Query for the inferred fact directly on the graph
    sparql_query = f"""
        PREFIX ex: <{EX}>
        ASK WHERE {{ <{EX}Alice> ex:isHappy true . }}
    """
    is_happy = bool(server.graph.graph.query(sparql_query))
    assert is_happy, "The custom rule should have inferred that Alice is happy."

    await server.shutdown()
