import pytest
from src.models.triple import Triple

def test_triple_creation():
    triple = Triple(subject="s", predicate="p", object="o")
    assert triple.subject == "s"
    assert triple.predicate == "p"
    assert triple.object == "o"

def test_triple_str():
    triple = Triple(subject="s", predicate="p", object="o")
    assert str(triple) == "(s, p, o)"
