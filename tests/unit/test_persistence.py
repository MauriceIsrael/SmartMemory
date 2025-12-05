import pytest
from pathlib import Path
from rdflib import Namespace, Literal, Graph
from smart_memory.knowledge.graph import ProvenanceGraph
from smart_memory.knowledge.persistence import TurtlePersistence, SQLitePersistence

EX = Namespace("http://example.org/")

@pytest.fixture
def populated_graph():
    g = ProvenanceGraph()
    g.add_triple_with_provenance(EX.s1, EX.p1, EX.o1, source="user")
    g.add_triple_with_provenance(EX.s2, EX.p2, Literal("test"), source="user")
    return g

def test_turtle_persistence(tmp_path, populated_graph):
    ttl_file = tmp_path / "test.ttl"
    persistence = TurtlePersistence(ttl_file)
    
    # Save and reload
    persistence.save(populated_graph)
    new_graph = ProvenanceGraph()
    persistence.load(new_graph)
    
    assert len(new_graph.graph) == len(populated_graph.graph)
    assert (EX.s1, EX.p1, EX.o1) in new_graph.graph

def test_sqlite_persistence(tmp_path):
    """Test SQLite persistence backend"""
    db_file = tmp_path / "test.db"
    identifier = "test_graph"
    
    # Create and save
    g_to_save = Graph(store="SQLAlchemy", identifier=identifier)
    g_to_save.open(f"sqlite:///{db_file}", create=True)
    
    # Add some triples
    g_to_save.add((EX.subject, EX.predicate, EX.object))
    g_to_save.commit()
    g_to_save.close()
    
    # Load in new graph with same identifier
    g_loaded = Graph(store="SQLAlchemy", identifier=identifier)
    g_loaded.open(f"sqlite:///{db_file}", create=False)
    
    assert len(g_loaded) == 1
    assert (EX.subject, EX.predicate, EX.object) in g_loaded
    
    g_loaded.close()

