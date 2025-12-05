"""
Integration tests for Core SPARQL Inference Rules.

Verifies that generic rules (Symmetry, Transitivity, Inverse, Hierarchy)
work correctly based on ontology definitions.
"""

import pytest
import asyncio
from smart_memory.server import SemanticMemoryServer
from smart_memory.config import SemanticMemoryConfig
from smart_memory.tools.add_memory import add_memory
from smart_memory.tools.query_memory import query_memory
from rdflib import Namespace

USER_NS = Namespace("http://semanticmemory.org/user#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

@pytest.fixture
def temp_config(tmp_path):
    """Configuration for testing with OWL disabled."""
    return SemanticMemoryConfig(
        persistence_path=tmp_path / "test_graph.ttl",
        log_level="INFO",
        force_offline=True,
        enable_owl_reasoning=False,
        auto_accept_threshold=0.85
    )

@pytest.mark.asyncio
async def test_core_inference_rules(temp_config, monkeypatch):
    """Test the 4 core generic rules."""
    monkeypatch.setattr("smart_memory.config.config", temp_config)
    monkeypatch.setattr("smart_memory.server.config", temp_config)
    
    server = SemanticMemoryServer()
    await server.startup()
    
    # Helper to run inference
    async def run_inference():
        try:
            await asyncio.wait_for(server.inference_manager.wait_until_idle(), timeout=5.0)
        except asyncio.TimeoutError:
            pass

    print("\n=== Test 1: Generic Symmetry ===")
    # Define a custom symmetric property
    await add_memory(
        {"input": "Define :partner as a symmetric property."},
        server.graph, server.reasoner, server.triple_extractor, server.rule_engine,
        inference_manager=server.inference_manager
    )
    # Manually add the OWL definition since NLP might not extract "SymmetricProperty" correctly
    from rdflib.namespace import RDF
    server.graph.add_triple(USER_NS.partner, RDF.type, OWL.SymmetricProperty)
    
    # Add fact: Alice partner Bob
    server.graph.add_triple(USER_NS.Alice, USER_NS.partner, USER_NS.Bob)
    
    # Trigger inference
    server.inference_manager.trigger_inference()
    await run_inference()
    
    # Check if Bob partner Alice exists
    res = await query_memory({"query": "ASK { :Bob :partner :Alice }"}, server.graph)
    assert "True" in res[0].text, "Symmetry should be inferred"

    print("\n=== Test 2: Generic Transitivity ===")
    # Define transitive property
    server.graph.add_triple(USER_NS.ancestorOf, RDF.type, OWL.TransitiveProperty)
    
    # Add chain: A -> B -> C
    server.graph.add_triple(USER_NS.Grandpa, USER_NS.ancestorOf, USER_NS.Dad)
    server.graph.add_triple(USER_NS.Dad, USER_NS.ancestorOf, USER_NS.Son)
    
    # Trigger inference
    server.inference_manager.trigger_inference()
    await run_inference()
    
    # Check A -> C
    res = await query_memory({"query": "ASK { :Grandpa :ancestorOf :Son }"}, server.graph)
    assert "True" in res[0].text, "Transitivity should be inferred"

    print("\n=== Test 3: Generic Inverse ===")
    # Define inverse properties
    server.graph.add_triple(USER_NS.parentOf, OWL.inverseOf, USER_NS.childOf)
    
    # Add: Mom parentOf Kid
    server.graph.add_triple(USER_NS.Mom, USER_NS.parentOf, USER_NS.Kid)
    
    # Trigger inference
    server.inference_manager.trigger_inference()
    await run_inference()
    
    # Check: Kid childOf Mom
    res = await query_memory({"query": "ASK { :Kid :childOf :Mom }"}, server.graph)
    assert "True" in res[0].text, "Inverse should be inferred"

    print("\n=== Test 4: Generic Hierarchy (SubClass) ===")
    # Define hierarchy: Dog subClassOf Animal
    server.graph.add_triple(USER_NS.Dog, RDFS.subClassOf, USER_NS.Animal)
    
    # Add: Rex is a Dog
    server.graph.add_triple(USER_NS.Rex, OWL.type, USER_NS.Dog) # using owl:type/rdf:type
    # Note: rdflib might use rdf:type. Let's ensure we use the right URI.
    from rdflib.namespace import RDF
    server.graph.add_triple(USER_NS.Rex, RDF.type, USER_NS.Dog)
    
    # Trigger inference
    server.inference_manager.trigger_inference()
    await run_inference()
    
    # Check: Rex is an Animal
    res = await query_memory({"query": "ASK { :Rex a :Animal }"}, server.graph)
    assert "True" in res[0].text, "Hierarchy should be inferred"

    await server.shutdown()
