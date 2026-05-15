import pytest
from rdflib import Namespace, RDF
from smart_memory.knowledge.graph import ProvenanceGraph
from smart_memory.tools.forget_memory import forget_memory
from smart_memory.nlp.triple_extractor import TripleExtractor

EX = Namespace("http://semanticmemory.org/user#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

@pytest.fixture
def graph_with_provenance():
    g = ProvenanceGraph()
    # Add a triple with provenance
    g.add_triple_with_provenance(EX.Alice, FOAF.knows, EX.Bob, source="user")
    return g

@pytest.mark.asyncio
async def test_forget_memory_removes_triple_and_provenance(graph_with_provenance):
    extractor = TripleExtractor()
    # Initial state
    assert (EX.Alice, FOAF.knows, EX.Bob) in graph_with_provenance.graph
    assert graph_with_provenance.get_triple_count() == 1
    
    # Check that provenance exists (rdf:Statement)
    statements = list(graph_with_provenance.graph.subjects(RDF.type, RDF.Statement))
    assert len(statements) == 1
    
    # Forget the fact
    arguments = {"input": ":Alice foaf:knows :Bob"}
    result = await forget_memory(arguments, graph_with_provenance, extractor)
    
    # Check triple removed
    assert (EX.Alice, FOAF.knows, EX.Bob) not in graph_with_provenance.graph
    assert graph_with_provenance.get_triple_count() == 0
    
    # Check provenance removed
    statements_after = list(graph_with_provenance.graph.subjects(RDF.type, RDF.Statement))
    assert len(statements_after) == 0
    
    # Result should be a success message
    assert "Forgotten" in result[0].text

@pytest.mark.asyncio
async def test_forget_memory_non_existent(graph_with_provenance):
    extractor = TripleExtractor()
    arguments = {"input": ":Charlie foaf:knows :Bob"}
    result = await forget_memory(arguments, graph_with_provenance, extractor)
    
    assert "Fact not found" in result[0].text
    assert graph_with_provenance.get_triple_count() == 1
