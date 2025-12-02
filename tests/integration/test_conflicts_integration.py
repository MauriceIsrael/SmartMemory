import pytest
import asyncio
from semantic_memory.server import SemanticMemoryServer
from semantic_memory.config import SemanticMemoryConfig
from semantic_memory.tools.add_memory import add_memory
from semantic_memory.tools.get_graph_stats import get_graph_stats

@pytest.fixture
def temp_config(tmp_path):
    return SemanticMemoryConfig(
        persistence_path=tmp_path / "knowledge_graph.ttl",
        log_level="DEBUG",
        force_offline=True
    )

@pytest.mark.asyncio
async def test_conflict_detection_integration(temp_config, monkeypatch):
    """
    Integration test for conflict detection:
    - Add conflicting data via add_memory.
    - Verify that the response warns about conflicts.
    - Verify that get_graph_stats reports conflicts.
    """
    monkeypatch.setattr("semantic_memory.config.config", temp_config)

    server = SemanticMemoryServer()
    await server.startup()

    # 1. Add a fact
    await add_memory(
        {"input": ":Alice :hasAge 30 .", "format": "triple_notation"},
        server.graph, server.reasoner, server.triple_extractor, server.rule_engine
    )

    # 2. Add a conflicting fact (same subject/predicate, different literal)
    result = await add_memory(
        {"input": ":Alice :hasAge 31 .", "format": "triple_notation"},
        server.graph, server.reasoner, server.triple_extractor, server.rule_engine
    )
    
    # Check response for warning
    response_text = result[0].text
    assert "Found" in response_text and "conflicts" in response_text
    assert "contradictory_literal" in response_text

    # 3. Check stats
    stats_result = await get_graph_stats({}, server.graph, server.rule_engine)
    stats_text = stats_result[0].text
    assert "Conflicts Detected: 1" in stats_text

    await server.shutdown()
