"""
Integration tests specifically for Uncertain Inference workflows.
Separated from strict inference tests to avoid rule conflicts.
"""

import pytest
from smart_memory.server import SemanticMemoryServer
from smart_memory.config import SemanticMemoryConfig
from smart_memory.tools.add_memory import add_memory
from smart_memory.tools.load_custom_rule import load_custom_rule
from smart_memory.tools.verify_inference import verify_inference
from smart_memory.tools.get_graph_stats import get_graph_stats
from rdflib import Namespace

# Namespaces
USER_NS = Namespace("http://semanticmemory.org/user#")
SCHEMA = Namespace("https://schema.org/")
SEM = Namespace("http://semanticmemory.org/vocab#")

@pytest.fixture
def test_config(tmp_path):
    """Configuration for testing."""
    return SemanticMemoryConfig(
        persistence_path=tmp_path / "knowledge_graph.ttl",
        log_level="INFO",
        force_offline=True,
        auto_accept_threshold=0.85,
        enable_owl_reasoning=False  # Disable slow OWL-RL reasoning for these tests
    )

@pytest.mark.asyncio
async def test_uncertainty_acceptance_workflow(test_config, monkeypatch):
    """
    Test the workflow of:
    1. Loading an uncertain rule
    2. Triggering it
    3. Verifying the uncertainty is detected
    4. Accepting the inference
    """
    monkeypatch.setattr("smart_memory.config.config", test_config)
    
    server = SemanticMemoryServer()
    await server.startup()
    
    # Disable conflicting default rules
    # 'coworkers_inference' generates the same triples as our test rule but strictly
    for rule in server.rule_engine.rules:
        if rule.id == "coworkers_inference":
            rule.is_active = False
            
    print("\n" + "="*70)
    print("UNCERTAINTY WORKFLOW: Acceptance")
    print("="*70 + "\n")
    
    # 1. Load uncertain rule
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
            "description": "Infers potential collaboration (uncertain)"
        },
        server.rule_engine,
        server.graph
    )
    
    # 2. Trigger rule
    await add_memory(
        {"input": "Alice works at TechCorp"},
        server.graph, server.reasoner, server.triple_extractor, server.rule_engine
    )
    result = await add_memory(
        {"input": "Bob works at TechCorp"},
        server.graph, server.reasoner, server.triple_extractor, server.rule_engine
    )
    
    print("Add Memory Result:", result[0].text)
    
    # 3. Verify detection
    pending_count = len(server.graph.pending_verifications_graph)
    assert pending_count > 0, "Should have pending verifications"
    
    # 4. Accept inference
    print("Accepting inference...")
    verify_result = await verify_inference(
        {
            "triple": ":Alice schema:colleague :Bob",
            "action": "accept"
        },
        server.graph
    )
    print("Verification Result:", verify_result[0].text)
    
    # Verify it's in the main graph
    query = f"ASK {{ <{USER_NS}Alice> <{SCHEMA}colleague> <{USER_NS}Bob> }}"
    assert bool(server.graph.graph.query(query)), "Triple should be in main graph after acceptance"
    
    await server.shutdown()

@pytest.mark.asyncio
async def test_uncertainty_rejection_workflow(test_config, monkeypatch):
    """
    Test the workflow of:
    1. Loading an uncertain rule
    2. Triggering it
    3. Rejecting the inference
    """
    monkeypatch.setattr("smart_memory.config.config", test_config)
    
    server = SemanticMemoryServer()
    await server.startup()
    
    print("\n" + "="*70)
    print("UNCERTAINTY WORKFLOW: Rejection")
    print("="*70 + "\n")
    
    # 1. Load uncertain rule
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
    
    # 2. Trigger rule
    await add_memory(
        {"input": ":PythonCourse schema:instructor :Bob .", "format": "triple_notation"},
        server.graph, server.reasoner, server.triple_extractor, server.rule_engine
    )
    await add_memory(
        {"input": ":PythonCourse schema:attendee :Alice .", "format": "triple_notation"},
        server.graph, server.reasoner, server.triple_extractor, server.rule_engine
    )
    
    # 3. Reject inference
    print("Rejecting inference...")
    verify_result = await verify_inference(
        {
            "triple": ":Bob sem:potentialMentor :Alice",
            "action": "reject"
        },
        server.graph
    )
    print("Verification Result:", verify_result[0].text)
    
    # Verify NOT in main graph
    query = f"ASK {{ <{USER_NS}Bob> <{SEM}potentialMentor> <{USER_NS}Alice> }}"
    assert not bool(server.graph.graph.query(query)), "Rejected triple should NOT be in main graph"
    
    # Verify IN rejected graph
    assert (USER_NS.Bob, SEM.potentialMentor, USER_NS.Alice) in server.graph.rejected_verifications_graph
    
    await server.shutdown()
