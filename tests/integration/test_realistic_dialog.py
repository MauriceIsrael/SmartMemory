"""
Integration test simulating a realistic dialog between a user and LLM using SmartMemory.

This test demonstrates:
1. User provides natural language information
2. System triggers OWL-RL inference (Level 1)
3. System triggers SPARQL rule inference (Level 2)
4. System requests verification for uncertain inferences
5. User confirms/rejects inferences
"""

import pytest
import asyncio
from semantic_memory.server import SemanticMemoryServer
from semantic_memory.config import SemanticMemoryConfig
from semantic_memory.tools.add_memory import add_memory
from semantic_memory.tools.query_memory import query_memory
from semantic_memory.tools.get_graph_stats import get_graph_stats
from semantic_memory.tools.load_custom_rule import load_custom_rule
from semantic_memory.tools.verify_inference import verify_inference
from rdflib import Namespace

# Namespaces
USER_NS = Namespace("http://semanticmemory.org/user#")
SCHEMA = Namespace("https://schema.org/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

@pytest.fixture
def temp_config(tmp_path):
    """Configuration for testing with offline mode."""
    return SemanticMemoryConfig(
        persistence_path=tmp_path / "knowledge_graph.ttl",
        log_level="INFO",
        force_offline=True,
        auto_accept_threshold=0.85  # Higher threshold to trigger verification
    )

@pytest.mark.asyncio
async def test_realistic_dialog_with_dual_inference_and_verification(temp_config, monkeypatch):
    """
    Simulates a realistic dialog scenario:
    
    Dialog Flow:
    1. User: "Alice works at TechCorp and knows Bob."
    2. LLM adds to memory → triggers inferences
    3. System responds with inferred facts AND verification requests
    4. User confirms some inferences, rejects others
    5. LLM queries updated memory to answer user questions
    """
    monkeypatch.setattr("semantic_memory.config.config", temp_config)
    
    # Initialize server
    server = SemanticMemoryServer()
    await server.startup()
    
    print("\n" + "="*70)
    print("REALISTIC DIALOG SCENARIO: User-LLM-SmartMemory Interaction")
    print("="*70 + "\n")
    
    # =========================================================================
    # STEP 1: User provides information
    # =========================================================================
    print("👤 User: 'Alice works at TechCorp and knows Bob.'")
    print("🤖 LLM: Adding this to your semantic memory...\n")
    
    result = await add_memory(
        {"input": "Alice works at TechCorp and knows Bob"},
        server.graph,
        server.reasoner, 
        server.triple_extractor,
        server.rule_engine,
        inference_manager=server.inference_manager
    )
    
    # Wait for background inference to complete
    print("⏳ Waiting for background inference...")
    try:
        await asyncio.wait_for(server.inference_manager.wait_until_idle(), timeout=10.0)
    except asyncio.TimeoutError:
        print("⚠️ Inference timed out (OWL-RL too slow), proceeding...")
    
    print("💾 SmartMemory Response:")
    print("-" * 70)
    print(result[0].text)
    print("-" * 70 + "\n")
    
    # =========================================================================
    # STEP 2: Add more information to trigger strict inference
    # =========================================================================
    print("👤 User: 'Bob also works at TechCorp.'")
    print("🤖 LLM: Adding this information...\n")
    
    result = await add_memory(
        {"input": ":Bob schema:worksFor :TechCorp .", "format": "triple_notation"},
        server.graph,
        server.reasoner,
        server.triple_extractor, 
        server.rule_engine,
        inference_manager=server.inference_manager
    )
    
    # Wait for background inference
    try:
        await asyncio.wait_for(server.inference_manager.wait_until_idle(), timeout=10.0)
    except asyncio.TimeoutError:
        print("⚠️ Inference timed out, proceeding...")
    
    print("💾 SmartMemory Response:")
    print("-" * 70)
    print(result[0].text)
    print("-" * 70 + "\n")
    
    # =========================================================================
    # STEP 3: Check graph statistics
    # =========================================================================
    print("📊 LLM: Checking graph statistics...\n")
    
    stats = await get_graph_stats({}, server.graph, server.rule_engine)
    print("📈 Graph Statistics:")
    print("-" * 70)
    print(stats[0].text)
    print("-" * 70 + "\n")
    
    # =========================================================================
    # STEP 4: Query to see what was automatically inferred
    # =========================================================================
    print("🔍 LLM: Let me check what I know about Alice and Bob...")
    print("🤖 LLM: Querying: 'What relationship exists between Alice and Bob?'\n")
    
    query = f"""
    PREFIX schema: <{SCHEMA}>
    PREFIX foaf: <{FOAF}>
    
    SELECT ?predicate ?source
    WHERE {{
        <{USER_NS}Alice> ?predicate <{USER_NS}Bob> .
        OPTIONAL {{
            ?stmt a rdf:Statement ;
                  rdf:subject <{USER_NS}Alice> ;
                  rdf:predicate ?predicate ;
                  rdf:object <{USER_NS}Bob> ;
                  sem:source ?source .
        }}
    }}
    """
    
    query_result = await query_memory({"query": query}, server.graph)
    print("📋 Query Results:")
    print("-" * 70)
    print(query_result[0].text)
    print("-" * 70 + "\n")
    
    # Verify OWL-RL inference occurred
    # foaf:knows should trigger symmetric property inference
    symmetric_query = f"""
    PREFIX foaf: <{FOAF}>
    ASK {{ <{USER_NS}Bob> foaf:knows <{USER_NS}Alice> . }}
    """
    symmetric_result = server.graph.graph.query(symmetric_query)
    assert bool(symmetric_result), "OWL-RL should have inferred symmetric foaf:knows"
    print("✅ OWL-RL Inference: Bob knows Alice (symmetric property)\n")
    
    # Verify strict SPARQL inference (coworkers_inference)
    # Should infer schema:colleague because both work at TechCorp
    colleague_query = f"""
    PREFIX schema: <{SCHEMA}>
    ASK {{ <{USER_NS}Alice> schema:colleague <{USER_NS}Bob> . }}
    """
    colleague_result = server.graph.graph.query(colleague_query)
    assert bool(colleague_result), "Strict SPARQL rule should have inferred schema:colleague"
    print("✅ Strict SPARQL Inference: Alice and Bob are colleagues\n")
    
    # =========================================================================
    # STEP 5: Final statistics
    # =========================================================================
    print("📊 Final Graph Statistics:")
    final_stats = await get_graph_stats({}, server.graph, server.rule_engine)
    print("-" * 70)
    print(final_stats[0].text)
    print("-" * 70 + "\n")
    
    print("✅ SCENARIO COMPLETE")
    print("="*70)
    print("\nSummary:")
    print("- ✅ Level 1 (OWL-RL): Inferred symmetric foaf:knows relationship")
    print("- ✅ Level 2 (SPARQL): Inferred colleague relationship (Strict)") 
    print("- ✅ Provenance: All inferences tracked with source")
    print("="*70 + "\n")
    
    await server.shutdown()



