import pytest
import requests
import requests_mock
from pathlib import Path
from datetime import datetime, timedelta, timezone
from semantic_memory.inference.ontology_loader import fetch_with_cache, OntologyCacheMetadata, OntologyLoader
from semantic_memory.config import SemanticMemoryConfig
from rdflib import Graph

@pytest.fixture
def temp_config(tmp_path):
    return SemanticMemoryConfig(cache_dir=tmp_path, cache_ttl_hours=1)

@pytest.fixture
def ontology_loader(temp_config):
    return OntologyLoader(cache_dir=temp_config.cache_dir)

def test_cache_freshness_check(ontology_loader, temp_config):
    url = "http://example.com/ontology.rdf"
    metadata = OntologyCacheMetadata(
        url=url,
        cached_at=(datetime(2000, 1, 1, tzinfo=timezone.utc)).isoformat(), # Very old date
        etag="old-etag",
        file_path=str(temp_config.cache_dir / "ontology.rdf")
    )
    assert metadata.is_expired()

    metadata.cached_at = datetime.now(timezone.utc).isoformat()
    assert not metadata.is_expired()

def test_offline_fallback(ontology_loader, temp_config, requests_mock):
    url = "http://example.com/ontology.rdf"
    cached_content = """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about="http://example.com/item1">
        <rdf:label>Cached Item</rdf:label>
    </rdf:Description>
</rdf:RDF>"""
    
    # Create a cached file
    cached_file = temp_config.cache_dir / "ontology.rdf"
    with open(cached_file, "w") as f:
        f.write(cached_content)

    metadata = OntologyCacheMetadata(
        url=url,
        cached_at=datetime.now(timezone.utc).isoformat(),
        file_path=str(cached_file)
    )
    ontology_loader.metadata[url] = metadata
    
    # Mock network to be down
    requests_mock.get(url, exc=requests.exceptions.ConnectionError)
    
    # Set force_offline to true
    temp_config.force_offline = True
    
    # The loader should use the cache
    g = Graph()
    ontology_loader.load_ontology(url, g)
    assert len(g) > 0 # Some triples should be parsed

    # Now test without force_offline, but with network error
    temp_config.force_offline = False
    g2 = Graph()
    ontology_loader.load_ontology(url, g2)
    assert len(g2) > 0

def test_conditional_get(ontology_loader, temp_config, requests_mock):
    url = "http://example.com/ontology.rdf"
    metadata = OntologyCacheMetadata(
        url=url,
        cached_at=datetime.now(timezone.utc).isoformat(),
        etag="etag-123",
        file_path=str(temp_config.cache_dir / "ontology.rdf")
    )
    
    # Mock a 304 Not Modified response
    requests_mock.get(url, status_code=304)
    
    content, new_meta = fetch_with_cache(url, temp_config.cache_dir, metadata)
    assert content is None # No new content
    assert new_meta.etag == "etag-123"

    # Mock a 200 OK response with new content
    requests_mock.get(url, status_code=200, text="<rdf:RDF>new</rdf:RDF>", headers={"ETag": "etag-456"})
    content, new_meta = fetch_with_cache(url, temp_config.cache_dir, metadata)
    assert content is not None
    assert new_meta.etag == "etag-456"
