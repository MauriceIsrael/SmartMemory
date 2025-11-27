import pytest
from pathlib import Path
from rdflib import Namespace, Literal, Graph
from semantic_memory.knowledge.graph import ProvenanceGraph
from semantic_memory.knowledge.persistence import TurtlePersistence, SQLitePersistence

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

def test_sqlite_persistence(tmp_path, populated_graph):
    db_file = tmp_path / "test.db"
    persistence = SQLitePersistence(db_file)
    
    # The rdflib-sqlalchemy store works directly on the graph object
    # So we need to create a graph with the store
    store = persistence.store
    g_to_save = Graph(store=store, identifier="test")
    g_to_save.open(str(db_file), create=True)
    for t in populated_graph.graph:
        g_to_save.add(t)
    g_to_save.close()

    # Now load it into a new graph
    new_persistence = SQLitePersistence(db_file)
    new_graph_wrapper = ProvenanceGraph()
    new_persistence.load(new_graph_wrapper)
    
    assert len(new_graph_wrapper.graph) == len(populated_graph.graph)
    assert (EX.s1, EX.p1, EX.o1) in new_graph_wrapper.graph
