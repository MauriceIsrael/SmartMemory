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
    # Patch the global config object so all modules use the temp config
    monkeypatch.setattr("smart_memory.config.config", temp_config)
    monkeypatch.setattr("smart_memory.server.config", temp_config)
    monkeypatch.setattr("smart_memory.knowledge.persistence.config", temp_config)

    server = SemanticMemoryServer()
    await server.startup()

    EX = Namespace("http://example.org/")
    USER_NS = Namespace("http://semanticmemory.org/user#")
    SCHEMA = Namespace("https://schema.org/")
    SEM = Namespace("http://semanticmemory.org/vocab#")

    # 1. Load a custom rule that generates an uncertain inference
    rule_id = "uncertain_rule"
    rule_content = f"""
        PREFIX schema: <{SCHEMA}>
        PREFIX ex: <{EX}>
        PREFIX sem: <{SEM}>
        CONSTRUCT {{ 
            ?person ex:isCitizenOf ?country .
            ?person sem:uncertainPredicate ex:isCitizenOf .
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
        {"input": f":Paris <https://schema.org/containedInPlace> <{EX}France> .", "format": "triple_notation"},
        server.graph, server.reasoner, server.triple_extractor, server.rule_engine,
        inference_manager=server.inference_manager
    )
    await add_memory(
        {"input": f":John <https://schema.org/homeLocation> :Paris .", "format": "triple_notation"},
        server.graph, server.reasoner, server.triple_extractor, server.rule_engine,
        inference_manager=server.inference_manager
    )
    
    # Wait for inference
    await asyncio.wait_for(server.inference_manager.wait_until_idle(), timeout=5.0)
    
    # 3. Check that the uncertain triple is in the pending graph
    # Note: :John maps to USER_NS.John, :Paris to USER_NS.Paris
    pending_triple = (USER_NS.John, EX.isCitizenOf, EX.France)
    
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
        {"input": f":Jane <https://schema.org/homeLocation> :Paris .", "format": "triple_notation"},
        server.graph, server.reasoner, server.triple_extractor, server.rule_engine,
        inference_manager=server.inference_manager
    )
    
    # Wait for inference
    await asyncio.wait_for(server.inference_manager.wait_until_idle(), timeout=5.0)

    rejected_triple = (USER_NS.Jane, EX.isCitizenOf, EX.France)
    await verify_inference(
        {"triple": f":Jane <{EX}isCitizenOf> <{EX}France>", "action": "reject"},
        server.graph
    )
    
    assert rejected_triple not in server.graph.graph
    assert rejected_triple in server.graph.rejected_verifications_graph

    await server.shutdown()

