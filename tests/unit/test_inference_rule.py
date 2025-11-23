import pytest
from src.models.inference_rule import InferenceRule
from src.models.triple import Triple

def test_inference_rule_creation():
    condition = Triple(subject="?s", predicate="p1", object="?o")
    conclusion = Triple(subject="?s", predicate="p2", object="?o")
    rule = InferenceRule(name="test_rule", conditions=[condition], conclusion=conclusion)
    
    assert rule.name == "test_rule"
    assert len(rule.conditions) == 1
    assert rule.conditions[0] == condition
    assert rule.conclusion == conclusion
