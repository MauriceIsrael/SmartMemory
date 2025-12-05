"""
Regression test for production inference failure.

This test reproduces the bug where inference_manager wasn't passed to add_memory,
preventing SPARQL rules from running in production.
"""

import pytest
import asyncio
from smart_memory.server import SemanticMemoryServer
from smart_memory.config import SemanticMemoryConfig
from smart_memory.tools.query_memory import query_memory

@pytest.fixture
def temp_config(tmp_path):
    """Configuration for testing."""
    return SemanticMemoryConfig(
        persistence_path=tmp_path / "test_graph.ttl",
        log_level="INFO",
        force_offline=True,
        enable_owl_reasoning=False,
        auto_accept_threshold=0.85
    )

@pytest.mark.asyncio
async def test_foaf_knows_symmetry_via_mcp(temp_config, monkeypatch):
    """
    Test that foaf:knows symmetry works when called via MCP server 
    (simulating real LLM interaction).
    """
    monkeypatch.setattr("smart_memory.config.config", temp_config)
    monkeypatch.setattr("smart_memory.server.config", temp_config)
    
    server = SemanticMemoryServer()
    await server.startup()
    
    # Register tools to access handle_call_tool
    server.register_tools()
    
    # Get the actual handler function
    # We need to find it in the server's registered handlers
    handler = None
    for callback in server.server._request_handlers.get("tools/call", []):
        handler = callback
        break
    
    assert handler is not None, "Tool handler not registered"
    
    # 1. Add "User knows Annie" via MCP tool call
    print("\n=== Step 1: Add 'User knows Annie' ===")
    result = await handler("add_memory", {"input": "Je connais Annie"})
    print(f"Add result: {result[0].text if result else 'None'}")
    
    # 2. Wait for inference
    print("\n=== Step 2: Wait for inference ===")
    try:
        await asyncio.wait_for(server.inference_manager.wait_until_idle(), timeout=10.0)
        print("Inference completed")
    except asyncio.TimeoutError:
        print("WARNING: Inference timed out")
    
    # 3. Query if Annie knows User (should be inferred by social_symmetry rule)
    print("\n=== Step 3: Query 'Annie knows User' ===")
    result = await handler("query_memory", {"query": "ASK { :Annie foaf:knows :User }"})
    print(f"Query result: {result[0].text}")
    
    # Assertion
    assert "True" in result[0].text, (
        "foaf:knows symmetry should be inferred by SPARQL rules. "
        "If this fails, check that add_memory receives inference_manager parameter."
    )
    
    await server.shutdown()
    print("\n✅ Test passed: Inference works correctly via MCP")
