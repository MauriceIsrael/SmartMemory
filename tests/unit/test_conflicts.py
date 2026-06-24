import pytest
from rdflib import Namespace, Literal, OWL, RDF
from smart_memory.knowledge.graph import ProvenanceGraph
from smart_memory.knowledge.conflicts import (
    ContradictoryLiteralDetector,
    DisjointClassDetector,
    FunctionalPropertyDetector,
)

EX = Namespace("http://semanticmemory.org/user#")
SCHEMA = Namespace("https://schema.org/")

@pytest.fixture
def empty_graph():
    return ProvenanceGraph()

@pytest.fixture
def populated_graph():
    g = ProvenanceGraph()
    # Contradictory literal
    g.add_triple_with_provenance(EX.person1, EX.hasAge, Literal("30"), source="user")
    g.add_triple_with_provenance(EX.person1, EX.hasAge, Literal("31"), source="user")
    
    # Disjoint classes
    g.add_triple_with_provenance(EX.Human, OWL.disjointWith, EX.Robot, source="ontology")
    g.add_triple_with_provenance(EX.robot1, RDF.type, EX.Human, source="user")
    g.add_triple_with_provenance(EX.robot1, RDF.type, EX.Robot, source="user")

    # Functional property
    g.add_triple_with_provenance(SCHEMA.email, RDF.type, OWL.FunctionalProperty, source="ontology")
    g.add_triple_with_provenance(EX.person2, SCHEMA.email, Literal("a@b.com"), source="user")
    g.add_triple_with_provenance(EX.person2, SCHEMA.email, Literal("x@y.com"), source="user")
    
    return g

def test_contradictory_literal_detector(populated_graph):
    detector = ContradictoryLiteralDetector()
    conflicts = detector.detect_conflicts(populated_graph)
    
    # Should detect both age and email conflicts
    assert len(conflicts) == 2
    conflict_subjects = {c.triples[0][0] for c in conflicts}
    assert EX.person1 in conflict_subjects
    assert EX.person2 in conflict_subjects
    
    # Check that conflicts contain the expected triples (without strict datatype check)
    age_conflict = [c for c in conflicts if c.triples[0][1] == EX.hasAge][0]
    assert len(age_conflict.triples) == 2
    # Just check values are present, not exact literal types
    age_values = {str(t[2]) for t in age_conflict.triples}
    assert '30' in age_values
    assert '31' in age_values

def test_disjoint_class_detector(populated_graph):
    detector = DisjointClassDetector()
    conflicts = detector.detect_conflicts(populated_graph)
    assert len(conflicts) == 1
    assert conflicts[0].type == "disjoint_class"
    assert (EX.robot1, RDF.type, EX.Human) in conflicts[0].triples
    assert (EX.robot1, RDF.type, EX.Robot) in conflicts[0].triples

def test_functional_property_detector(populated_graph):
    detector = FunctionalPropertyDetector()
    conflicts = detector.detect_conflicts(populated_graph)
    assert len(conflicts) == 1
    assert conflicts[0].type == "functional_property"
    assert (EX.person2, SCHEMA.email, Literal("a@b.com")) in conflicts[0].triples
    assert (EX.person2, SCHEMA.email, Literal("x@y.com")) in conflicts[0].triples

def test_no_conflicts(empty_graph):
    detector = ContradictoryLiteralDetector()
    assert len(detector.detect_conflicts(empty_graph)) == 0

    detector = DisjointClassDetector()
    assert len(detector.detect_conflicts(empty_graph)) == 0

    detector = FunctionalPropertyDetector()
    assert len(detector.detect_conflicts(empty_graph)) == 0
