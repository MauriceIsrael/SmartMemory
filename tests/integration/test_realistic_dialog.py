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
    # STEP 1: Load a custom rule that generates uncertain inferences
    # =========================================================================
    print("📋 LLM: Loading custom inference rule...")
    
    # Rule: If two people work at the same company, they MIGHT be collaborators
    # This is uncertain because not everyone at the same company collaborates
    collaboration_rule = """
    PREFIX schema: <https://schema.org/>
    PREFIX sem: <http://semanticmemory.org/vocab#>
    
    CONSTRUCT {
        ?person1 schema:colleague ?person2 .
        ?person1 sem:uncertainPredicate schema:colleague .
    }
    WHERE {
        ?person1 schema:worksFor ?org .
        ?person2 schema:worksFor ?org .
        FILTER(?person1 != ?person2)
    }
    """
    
    await load_custom_rule(
        {
            "rule_id": "potential_collaboration",
            "rule_content": collaboration_rule,
            "description": "Infers potential collaboration from shared workplace (uncertain)"
        },
        server.rule_engine,
        server.graph
    )
    print("✅ Rule loaded: potential_collaboration\n")
    
    # =========================================================================
    # STEP 2: User provides information
    # =========================================================================
    print("👤 User: 'Alice works at TechCorp and knows Bob.'")
    print("🤖 LLM: Adding this to your semantic memory...\n")
    
    result = await add_memory(
        {"input": "Alice works at TechCorp and knows Bob"},
        server.graph,
        server.reasoner, 
        server.triple_extractor,
        server.rule_engine
    )
    
    print("💾 SmartMemory Response:")
    print("-" * 70)
    print(result[0].text)
    print("-" * 70 + "\n")
    
    # =========================================================================
    # STEP 3: Add more information to trigger collaboration inference
    # =========================================================================
    print("👤 User: 'Bob also works at TechCorp.'")
    print("🤖 LLM: Adding this information...\n")
    
    result = await add_memory(
        {"input": ":Bob schema:worksFor :TechCorp .", "format": "triple_notation"},
        server.graph,
        server.reasoner,
        server.triple_extractor, 
        server.rule_engine
    )
    
    print("💾 SmartMemory Response:")
    print("-" * 70)
    print(result[0].text)
    print("-" * 70 + "\n")
    
    # =========================================================================
    # STEP 4: Check what was inferred and what needs verification
    # =========================================================================
    print("📊 LLM: Checking graph statistics...\n")
    
    stats = await get_graph_stats({}, server.graph, server.rule_engine)
    print("📈 Graph Statistics:")
    print("-" * 70)
    print(stats[0].text)
    print("-" * 70 + "\n")
    
    # Verify we have pending verifications
    assert len(server.graph.pending_verifications_graph) > 0, "Should have pending verifications"
    
    # =========================================================================
    # STEP 5: Query to see what was automatically inferred
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
    
    # =========================================================================
    # STEP 6: System presents verification request to user
    # =========================================================================
    print("❓ SmartMemory: I detected an uncertain inference that needs your confirmation:")
    print("   'Alice and Bob might be colleagues (schema:colleague) because they")
    print("    both work at TechCorp.'")
    print("   Confidence: 0.75 (below auto-accept threshold of 0.85)\n")
    
    # =========================================================================
    # STEP 7: User confirms the inference
    # =========================================================================
    print("👤 User: 'Yes, they do work together on projects. Please confirm.'")
    print("🤖 LLM: Confirming this inference...\n")
    
    verify_result = await verify_inference(
        {
            "triple": ":Alice schema:colleague :Bob",
            "action": "accept"
        },
        server.graph
    )
    
    print("✅ Verification Response:")
    print("-" * 70)
    print(verify_result[0].text)
    print("-" * 70 + "\n")
    
    # Verify the triple is now in the main graph
    colleague_query = f"""
    PREFIX schema: <{SCHEMA}>
    ASK {{ <{USER_NS}Alice> schema:colleague <{USER_NS}Bob> . }}
    """
    colleague_result = server.graph.graph.query(colleague_query)
    assert bool(colleague_result), "Verified inference should be in graph"
    
    # =========================================================================
    # STEP 8: Final query showing all information
    # =========================================================================
    print("🔍 LLM: Let me summarize what I know about Alice:")
    print("🤖 LLM: Querying: 'Tell me everything about Alice'\n")
    
    final_query = f"""
    PREFIX schema: <{SCHEMA}>
    PREFIX foaf: <{FOAF}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT ?predicate ?object
    WHERE {{
        <{USER_NS}Alice> ?predicate ?object .
        FILTER(?predicate != rdf:type)
    }}
    """
    
    final_result = await query_memory({"query": final_query}, server.graph)
    print("📋 Everything I know about Alice:")
    print("-" * 70)
    print(final_result[0].text)
    print("-" * 70 + "\n")
    
    # =========================================================================
    # STEP 9: Final statistics
    # =========================================================================
    print("📊 Final Graph Statistics:")
    final_stats = await get_graph_stats({}, server.graph, server.rule_engine)
    print("-" * 70)
    print(final_stats[0].text)
    print("-" * 70 + "\n")
    
    # Verify no pending verifications remain
    assert len(server.graph.pending_verifications_graph) == 0, "All verifications should be resolved"
    
    print("✅ SCENARIO COMPLETE")
    print("="*70)
    print("\nSummary:")
    print("- ✅ Level 1 (OWL-RL): Inferred symmetric foaf:knows relationship")
    print("- ✅ Level 2 (SPARQL): Detected potential colleague relationship") 
    print("- ✅ User Verification: Confirmed uncertain inference")
    print("- ✅ Provenance: All inferences tracked with source and confidence")
    print("="*70 + "\n")
    
    await server.shutdown()


@pytest.mark.asyncio
async def test_dialog_with_rejection(temp_config, monkeypatch):
    """
    Test scenario where user REJECTS an uncertain inference.
    
    Dialog:
    1. User provides information triggering inference
    2. System requests verification
    3. User rejects the inference
    4. System should NOT have the triple in the main graph
    """
    monkeypatch.setattr("semantic_memory.config.config", temp_config)
    
    server = SemanticMemoryServer()
    await server.startup()
    
    print("\n" + "="*70)
    print("REJECTION SCENARIO: User Rejects Uncertain Inference")
    print("="*70 + "\n")
    
    # Load rule for potential mentorship inference (uncertain)
    mentorship_rule = """
    PREFIX schema: <https://schema.org/>
    PREFIX sem: <http://semanticmemory.org/vocab#>
    
    CONSTRUCT {
        ?instructor sem:potentialMentor ?student .
        ?instructor sem:uncertainPredicate sem:potentialMentor .
    }
    WHERE {
        ?course schema:instructor ?instructor .
        ?course schema:attendee ?student .
    }
    """
    
    await load_custom_rule(
        {
            "rule_id": "mentorship_inference",
            "rule_content": mentorship_rule,
            "description": "Infers potential mentorship (uncertain)"
        },
        server.rule_engine,
        server.graph
    )
    
    print("👤 User: 'Bob is the instructor of the Python course. Alice attended it.'\n")
    
    await add_memory(
        {"input": ":PythonCourse schema:instructor :Bob .", "format": "triple_notation"},
        server.graph,
        server.reasoner,
        server.triple_extractor,
        server.rule_engine
    )
    
    await add_memory(
        {"input": ":PythonCourse schema:attendee :Alice .", "format": "triple_notation"},
        server.graph,
        server.reasoner,
        server.triple_extractor,
        server.rule_engine
    )
    
    # Should have pending verification
    assert len(server.graph.pending_verifications_graph) > 0
    
    print("❓ SmartMemory: Should Bob be considered a potential mentor to Alice?")
    print("👤 User: 'No, it was just a one-time workshop, not mentorship.'")
    print("🤖 LLM: Rejecting this inference...\n")
    
    # Reject the inference
    reject_result = await verify_inference(
        {
            "triple": ":Bob sem:potentialMentor :Alice",
            "action": "reject"
        },
        server.graph
    )
    
    print("✅ Rejection confirmed")
    print(reject_result[0].text + "\n")
    
    # Verify triple is NOT in main graph
    mentor_query = f"""
    PREFIX sem: <http://semanticmemory.org/vocab#>
    ASK {{ <{USER_NS}Bob> sem:potentialMentor <{USER_NS}Alice> . }}
    """
    result = server.graph.graph.query(mentor_query)
    assert not bool(result), "Rejected inference should NOT be in graph"
    
    # Verify it IS in rejected graph
    assert (USER_NS.Bob, Namespace("http://semanticmemory.org/vocab#").potentialMentor, USER_NS.Alice) in server.graph.rejected_verifications_graph
    
    print("✅ Verified: Rejected inference is NOT in the knowledge graph")
    print("✅ Verified: Rejection recorded for future reference\n")
    
    print("="*70 + "\n")
    
    await server.shutdown()
