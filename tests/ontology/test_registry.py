"""Tests for OntologyRegistry."""

import pytest

from src.ontology.registry import OntologyRegistry, OntologySource, OntologyFormat


def test_get_all_returns_sorted_by_priority():
    """Test that get_all returns ontologies sorted by priority."""
    ontologies = OntologyRegistry.get_all()
    
    assert len(ontologies) >= 2
    assert all(isinstance(o, OntologySource) for o in ontologies)
    
    # Check sorted by priority
    priorities = [o.priority for o in ontologies]
    assert priorities == sorted(priorities)


# def test_get_by_name_foaf():
#     """Test retrieving FOAF ontology by name."""
#     foaf = OntologyRegistry.get_by_name("foaf")
    
#     assert foaf is not None
#     assert foaf.name == "foaf"
#     assert "foaf" in foaf.url.lower()
#     assert foaf.format in [OntologyFormat.RDF_XML, OntologyFormat.TURTLE]


def test_get_by_name_skos():
    """Test retrieving SKOS ontology by name."""
    skos = OntologyRegistry.get_by_name("skos")
    
    assert skos is not None
    assert skos.name == "skos"
    assert "skos" in skos.url.lower()


def test_get_by_name_schema():
    """Test retrieving Schema.org ontology by name."""
    schema = OntologyRegistry.get_by_name("schema")
    
    assert schema is not None
    assert schema.name == "schema"
    assert "schema.org" in schema.url.lower()


def test_get_by_name_unknown():
    """Test that unknown ontology returns None."""
    result = OntologyRegistry.get_by_name("nonexistent")
    assert result is None


def test_add_custom_ontology():
    """Test adding a custom ontology."""
    initial_count = len(OntologyRegistry.get_all())
    
    custom = OntologySource(
        name="custom",
        url="http://example.com/custom.ttl",
        format=OntologyFormat.TURTLE,
        priority=99,
        description="Custom test ontology"
    )
    
    OntologyRegistry.add_custom(custom)
    
    # Verify it was added
    assert len(OntologyRegistry.get_all()) == initial_count + 1
    
    # Verify we can retrieve it
    retrieved = OntologyRegistry.get_by_name("custom")
    assert retrieved is not None
    assert retrieved.name == "custom"
    assert retrieved.url == "http://example.com/custom.ttl"
    
    # Clean up
    OntologyRegistry._ONTOLOGIES.remove(custom)


def test_ontology_source_attributes():
    """Test OntologySource dataclass attributes."""
    source = OntologySource(
        name="test",
        url="http://example.com/test.ttl",
        format=OntologyFormat.TURTLE,
        priority=1,
        description="Test ontology"
    )
    
    assert source.name == "test"
    assert source.url == "http://example.com/test.ttl"
    assert source.format == OntologyFormat.TURTLE
    assert source.priority == 1
    assert source.description == "Test ontology"
