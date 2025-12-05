import pytest
import asyncio
from pathlib import Path
from smart_memory.server import SemanticMemoryServer
from smart_memory.config import SemanticMemoryConfig
from rdflib import Namespace, Literal, XSD, RDF
from smart_memory.tools.add_memory import add_memory
from smart_memory.tools.load_custom_rule import load_custom_rule
from smart_memory.tools.verify_inference import verify_inference

@pytest.fixture
def temp_config(tmp_path):
    """Fixture to create a temporary configuration for testing."""
    user_rules_dir = tmp_path / "user_rules"
    user_rules_dir.mkdir()
    persistence_path = tmp_path / "knowledge_graph.ttl"
    return SemanticMemoryConfig(
        user_rules_dir=user_rules_dir,
        persistence_path=persistence_path,
        log_level="DEBUG"
    )

@pytest.mark.asyncio
async def test_user_story_3_integration(temp_config, monkeypatch):
    """
    Integration test for User Story 3:
    - An uncertain rule is triggered.
    - The inferred triple goes to the pending graph.
    - The user verifies the triple, and it moves to the main graph.
    - The user rejects another triple, and it moves to the rejected graph.
    """
    monkeypatch.setattr("smart_memory.config.config", temp_config)

    server = SemanticMemoryServer()
    await server.startup() # register_tools is called in startup

    EX = Namespace("http://example.org/")
    SCHEMA = Namespace("https://schema.org/")
    SEM = Namespace("http://semanticmemory.org/sem#")

    # 1. Load a custom rule that generates an uncertain inference
    rule_id = "uncertain_rule"
    # This rule states that if someone lives in a city, they *might* be a citizen of the country.
    # The sem:uncertain predicate is used to mark the inference as uncertain.
    rule_content = f"""
        PREFIX schema: <{SCHEMA}>
        PREFIX ex: <{EX}>
        PREFIX sem: <{SEM}>
        CONSTRUCT {{ 
            ?person ex:isCitizenOf ?country .
            ?person sem:uncertainPredicate ex:isCitizenOf . # Marks the predicate as uncertain
        }}
        WHERE {{
            ?person schema:homeLocation ?city .
            ?city schema:containedInPlace ?country .
        }}
    """
    await load_custom_rule(
        {"rule_id": rule_id, "rule_content": rule_content},
        server.rule_engine, server.graph
    )

    # 2. Add facts
    await add_memory(
        {"input": f":Paris schema:containedInPlace <{EX}France> .", "format": "triple_notation"},
        server.graph, server.reasoner, server.triple_extractor, server.rule_engine
    )
    await add_memory(
        {"input": f":John schema:homeLocation <{EX}Paris> .", "format": "triple_notation"},
        server.graph, server.reasoner, server.triple_extractor, server.rule_engine
    )
    
    # 3. Check that the uncertain triple is in the pending graph
    # We need to check for the reified statement, not just the triple
    pending_triple = (EX.John, EX.isCitizenOf, EX.France)
    
    stmt_found = False
    for stmt in server.graph.pending_verifications_graph.subjects(RDF.type, RDF.Statement):
        if (server.graph.pending_verifications_graph.value(stmt, RDF.subject) == pending_triple[0] and
            server.graph.pending_verifications_graph.value(stmt, RDF.predicate) == pending_triple[1] and
            server.graph.pending_verifications_graph.value(stmt, RDF.object) == pending_triple[2]):
            stmt_found = True
            break
    assert stmt_found
    assert pending_triple not in server.graph.graph

    # 4. Verify the inference
    await verify_inference(
        {"triple": f":John <{EX}isCitizenOf> <{EX}France>", "action": "accept"},
        server.graph
    )
    
    # 5. Check that the triple is now in the main graph
    assert pending_triple in server.graph.graph
    assert len(server.graph.pending_verifications_graph) == 0

    # 6. Test rejection
    await add_memory(
        {"input": f":Jane schema:homeLocation <{EX}Paris> .", "format": "triple_notation"},
        server.graph, server.reasoner, server.triple_extractor, server.rule_engine
    )
    rejected_triple = (EX.Jane, EX.isCitizenOf, EX.France)
    await verify_inference(
        {"triple": f":Jane <{EX}isCitizenOf> <{EX}France>", "action": "reject"},
        server.graph
    )
    
    assert rejected_triple not in server.graph.graph
    assert rejected_triple in server.graph.rejected_verifications_graph

    await server.shutdown()
