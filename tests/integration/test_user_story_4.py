import pytest
import asyncio
from pathlib import Path
import requests_mock
from smart_memory.server import SemanticMemoryServer
from smart_memory.config import SemanticMemoryConfig

@pytest.fixture
def temp_config(tmp_path):
    return SemanticMemoryConfig(
        cache_dir=tmp_path / "cache",
        persistence_path=tmp_path / "knowledge_graph.ttl",
        log_level="DEBUG",
        load_ontologies=True
    )


@pytest.mark.asyncio
async def test_user_story_4_integration(temp_config, monkeypatch, requests_mock):
    """
    Integration test for User Story 4: Offline startup.
    """
    # Patch the global config object so all modules use the temp config
    monkeypatch.setattr("smart_memory.config.config", temp_config)
    monkeypatch.setattr("smart_memory.server.config", temp_config)
    monkeypatch.setattr("smart_memory.knowledge.persistence.config", temp_config)
    
    # --- Online phase: populate the cache ---
    temp_config.force_offline = False
    
    # Mock ontology endpoints
    # Use first URL in list if multiple
    for url_name, urls in temp_config.ontology_urls.items():
        url_value = urls[0] if isinstance(urls, list) else urls
        # Provide a minimal but valid RDF/XML content for each ontology
        mock_content = f"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
         xml:base="{url_value}">
    <rdfs:Class rdf:about="{url_value}TestClass">
        <rdfs:label>{url_name} Test Class</rdfs:label>
    </rdfs:Class>
</rdf:RDF>"""
        requests_mock.get(url_value, text=mock_content, headers={"ETag": f"etag-{url_name}"})

    server_online = SemanticMemoryServer()
    await server_online.startup()
    await server_online.shutdown()

    # Verify that cache files were created
    assert len(list(temp_config.cache_dir.glob("*.rdf"))) > 0
    assert (temp_config.cache_dir / "metadata.json").exists()

    # --- Offline phase: start server without network ---
    temp_config.force_offline = True
    
    # The requests_mock from the online phase is still active,
    # but force_offline should prevent any calls from being made.
    import re
    requests_mock.get(re.compile('.*'), real_http=False)

    
    server_offline = SemanticMemoryServer()
    
    # This should not raise any network-related exceptions
    await server_offline.startup()
    
    # Check that ontologies were loaded (from cache)
    assert len(server_offline.graph.graph) > 0, "Graph should have loaded ontologies from cache"

    await server_offline.shutdown()

