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
    # SQLitePersistence needs to be instantiated to use its internal logic
    from smart_memory.knowledge.persistence import SQLitePersistence
    db_file = tmp_path / "test.db"
    
    # Check if rdflib-sqlalchemy is available
    try:
        persistence = SQLitePersistence(db_file)
    except ImportError:
        pytest.skip("rdflib-sqlalchemy not installed")
    
    g = ProvenanceGraph()
    g.add_triple_with_provenance(EX.s1, EX.p1, EX.o1, source="user")
    
    # Save (no-op for SQLite as it auto-commits)
    persistence.save(g)
    
    # Load into new graph
    new_graph = ProvenanceGraph()
    persistence.load(new_graph)
    
    assert (EX.s1, EX.p1, EX.o1) in new_graph.graph
    assert new_graph.get_triple_count() == 1

def test_oxigraph_persistence(tmp_path):
    """Test Oxigraph persistence backend"""
    from smart_memory.knowledge.persistence import OxigraphPersistence
    db_dir = tmp_path / "oxigraph_db"
    
    try:
        persistence = OxigraphPersistence(db_dir)
    except ImportError:
        pytest.skip("pyoxigraph not installed")
        
    g = ProvenanceGraph()
    g.add_triple_with_provenance(EX.s1, EX.p1, EX.o1, source="user")
    g.add_triple_with_provenance(EX.s2, EX.p2, Literal("test", lang="en"), source="user")
    
    # Save
    persistence.save(g)
    
    # Load into new graph
    new_graph = ProvenanceGraph()
    persistence.load(new_graph)
    
    assert len(new_graph.graph) == len(g.graph)
    assert (EX.s1, EX.p1, EX.o1) in new_graph.graph
    assert (EX.s2, EX.p2, Literal("test", lang="en")) in new_graph.graph
    assert new_graph.get_triple_count() == 2


