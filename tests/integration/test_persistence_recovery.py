import pytest
import asyncio
from pathlib import Path
from semantic_memory.server import SemanticMemoryServer
from semantic_memory.config import SemanticMemoryConfig
from rdflib import Namespace, Literal
from semantic_memory.tools.add_memory import add_memory

@pytest.fixture
def temp_config(tmp_path):
    return SemanticMemoryConfig(
        persistence_path=tmp_path / "knowledge_graph.ttl",
        log_level="DEBUG"
    )

@pytest.mark.asyncio
async def test_persistence_recovery_integration(temp_config, monkeypatch):
    """
    Integration test for persistence:
    - Add data to a server.
    - Shut down the server.
    - Start a new server.
    - Verify the data is still there.
    """
    monkeypatch.setattr("semantic_memory.config.config", temp_config)
    EX = Namespace("http://example.org/")

    # --- First session: add data and shut down ---
    server1 = SemanticMemoryServer()
    await server1.startup() # register_tools is called in startup
    
    await add_memory(
        {"input": ":person1 ex:likes :pizza .", "format": "triple_notation"},
        server1.graph, server1.reasoner, server1.triple_extractor, server1.rule_engine
    )
    
    await server1.shutdown()

    # --- Second session: start up and verify ---
    server2 = SemanticMemoryServer()
    await server2.startup() # register_tools is called in startup

    # Verify that the data from the first session is present
    query = f"ASK {{ <{EX}person1> <{EX}likes> <{EX}pizza> . }}"
    is_present = bool(server2.graph.graph.query(query))
    assert is_present, "Data from previous session should be loaded on startup"

    await server2.shutdown()
