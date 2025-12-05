import pytest
from pathlib import Path
from smart_memory.inference.rule_engine import load_rules, RuleEngine, InferenceRule
from smart_memory.knowledge.graph import ProvenanceGraph
from rdflib import Namespace, Literal

EX = Namespace("http://example.org/")

@pytest.fixture
def test_rules_dir():
    return Path(__file__).parent.parent / "fixtures" / "test_rules"

def test_load_rules(test_rules_dir):
    rules = load_rules([test_rules_dir])
    assert len(rules) == 5

    valid_rule = next((r for r in rules if r.id == "valid_rule"), None)
    assert valid_rule is not None
    assert valid_rule.is_active
    assert valid_rule.validation_error is None
    assert valid_rule.description == "This is a valid rule to find coworkers."

    invalid_rule = next((r for r in rules if r.id == "invalid_syntax_rule"), None)
    assert invalid_rule is not None
    assert not invalid_rule.is_active
    assert invalid_rule.validation_error is not None

    rule_with_desc = next((r for r in rules if r.id == "rule_with_description"), None)
    assert rule_with_desc is not None
    assert rule_with_desc.description == "This is a test description."

def test_cycle_detection(test_rules_dir):
    rules = load_rules([test_rules_dir])
    cycle_rules = [r for r in rules if r.id in ["cycle_a", "cycle_b"]]
    
    engine = RuleEngine(cycle_rules)
    graph = ProvenanceGraph()
    graph.add_triple_with_provenance(EX.a, EX.relatesTo, EX.b, "user")

    # The cycle should be handled by the max_depth limit in execute_rules
    # and the fact that we don't add triples that already exist.
    engine.execute_rules(graph, max_depth=2)

    # We expect the rule to be executed, but not to cause an infinite loop.
    # The exact number of executions depends on the implementation details,
    # but it should be a finite number.
    for rule in cycle_rules:
        assert rule.execution_count > 0
        assert rule.execution_count < 10

    # The graph should contain both triples
    assert (EX.a, EX.relatesTo, EX.b) in graph.graph
    assert (EX.b, EX.relatesTo, EX.a) in graph.graph

def test_rule_engine_execution():
    rule_content = """
    PREFIX schema: <https://schema.org/>
    CONSTRUCT { ?p1 schema:colleague ?p2 . }
    WHERE {
        ?p1 schema:worksFor ?org .
        ?p2 schema:worksFor ?org .
        FILTER(?p1 != ?p2)
    }
    """
    rule = InferenceRule(id="test", file_path=Path("test.rq"), sparql_query=rule_content, source="custom")
    engine = RuleEngine([rule])
    graph = ProvenanceGraph()

    SCHEMA = Namespace("https://schema.org/")
    p1 = EX.p1
    p2 = EX.p2
    org = EX.org

    graph.add_triple_with_provenance(p1, SCHEMA.worksFor, org, "user")
    graph.add_triple_with_provenance(p2, SCHEMA.worksFor, org, "user")

    engine.execute_rules(graph)

    assert (p1, SCHEMA.colleague, p2) in graph.graph
