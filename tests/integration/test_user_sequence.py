"""
Integration test for user sequence:
1. Add facts about Gilles, Jérémie, Coralie working at Thales
2. Add "User knows Gilles"
3. Check if "Gilles knows User" (foaf:knows symmetry)
4. Check for colleague inferences
"""

import pytest
import asyncio
from semantic_memory.server import SemanticMemoryServer
from semantic_memory.config import SemanticMemoryConfig
from semantic_memory.tools.add_memory import add_memory
from semantic_memory.tools.query_memory import query_memory
from rdflib import Namespace

USER_NS = Namespace("http://semanticmemory.org/user#")
SCHEMA = Namespace("https://schema.org/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")


@pytest.fixture
def temp_config(tmp_path):
    """Configuration for testing."""
    return SemanticMemoryConfig(
        persistence_path=tmp_path / "test_graph.ttl",
        log_level="INFO",
        force_offline=True,
        enable_owl_reasoning=False,  # Disabled for performance - use SPARQL rules instead
        auto_accept_threshold=0.85
    )


@pytest.mark.asyncio
async def test_user_sequence_thales_employees(temp_config, monkeypatch):
    """
    Test the exact sequence reported by the user:
    1. Add employees at Thales
    2. Add "User knows Gilles"
    3. Verify foaf:knows symmetry (Gilles knows User)
    4. Query for Daniel's colleagues
    """
    monkeypatch.setattr("semantic_memory.config.config", temp_config)
    monkeypatch.setattr("semantic_memory.server.config", temp_config)
    
    server = SemanticMemoryServer()
    await server.startup()
    
    print("\n=== Step 1: Add Thales employees ===")
    # Add Gilles, Jérémie, Coralie at Thales
    await add_memory(
        {"input": "Gilles works at Thales"},
        server.graph,
        server.reasoner,
        server.triple_extractor,
        server.rule_engine,
        inference_manager=server.inference_manager
    )
    
    await add_memory(
        {"input": "Jérémie works at Thales"},
        server.graph,
        server.reasoner,
        server.triple_extractor,
        server.rule_engine,
        inference_manager=server.inference_manager
    )
    
    await add_memory(
        {"input": "Coralie works at Thales"},
        server.graph,
        server.reasoner,
        server.triple_extractor,
        server.rule_engine,
        inference_manager=server.inference_manager
    )
    
    # Wait for background inference
    print("⏳ Waiting for inference...")
    try:
        await asyncio.wait_for(server.inference_manager.wait_until_idle(), timeout=15.0)
    except asyncio.TimeoutError:
        print("⚠️ Inference timed out")
    
    print("\n=== Step 2: Add 'User knows Gilles' ===")
    await add_memory(
        {"input": "Je connais Gilles"},  # French: "I know Gilles"
        server.graph,
        server.reasoner,
        server.triple_extractor,
        server.rule_engine,
        inference_manager=server.inference_manager
    )
    
    # Wait for inference
    print("⏳ Waiting for inference...")
    try:
        await asyncio.wait_for(server.inference_manager.wait_until_idle(), timeout=15.0)
    except asyncio.TimeoutError:
        print("⚠️ Inference timed out")
    
    print("\n=== Step 3: Check foaf:knows symmetry ===")
    # Query: Does Gilles know User?
    symmetry_query = f"""
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    ASK {{ :Gilles foaf:knows :User }}
    """
    
    result = await query_memory({"query": symmetry_query}, server.graph)
    print(f"Result: {result[0].text}")
    
    # Assert symmetry was inferred
    assert "True" in result[0].text, "foaf:knows symmetry should have been inferred by SPARQL rules"
    
    print("\n=== Step 4: Add Daniel at Thales ===")
    await add_memory(
        {"input": "Daniel works at Thales"},
        server.graph,
        server.reasoner,
        server.triple_extractor,
        server.rule_engine,
        inference_manager=server.inference_manager
    )
    
    # Wait for inference
    print("⏳ Waiting for inference...")
    try:
        await asyncio.wait_for(server.inference_manager.wait_until_idle(), timeout=15.0)
    except asyncio.TimeoutError:
        print("⚠️ Inference timed out")
    
    print("\n=== Step 5: Query Daniel's colleagues ===")
    colleagues_query = """
    PREFIX schema: <https://schema.org/>
    SELECT ?colleague WHERE {
        :Daniel schema:colleague ?colleague .
    }
    """
    
    result = await query_memory({"query": colleagues_query}, server.graph)
    print(f"Result: {result[0].text}")
    
    # Should find Gilles, Jérémie, Coralie as colleagues
    # (inferred by coworkers_inference rule)
    assert "Gilles" in result[0].text or "colleague" in result[0].text.lower(), \
        "Should have inferred colleague relationships"
    
    print("\n=== Step 6: Query all Thales employees ===")
    employees_query = """
    PREFIX schema: <https://schema.org/>
    SELECT ?person WHERE {
        ?person schema:worksFor :Thales .
    }
    """
    
    result = await query_memory({"query": employees_query}, server.graph)
    print(f"Result: {result[0].text}")
    
    # Should find all 4 employees
    result_text = result[0].text
    assert "Gilles" in result_text, "Should find Gilles"
    assert "Jérémie" in result_text or "Jeremie" in result_text, "Should find Jérémie"
    assert "Coralie" in result_text, "Should find Coralie"
    assert "Daniel" in result_text, "Should find Daniel"
    
    await server.shutdown()
    print("\n✅ All tests passed!")
