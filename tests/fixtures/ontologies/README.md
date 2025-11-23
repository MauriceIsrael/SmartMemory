# Test Ontology Fixtures

This directory contains minimal test fixtures for standard ontologies.

## Files

- **foaf_minimal.rdf**: Minimal FOAF ontology with Person, Agent, knows, name
- **schema_minimal.rdf**: Minimal Schema.org with Person, Organization, Place, Event and common properties

## Purpose

These fixtures are used for:

1. **Unit testing**: Test inference without downloading full ontologies
2. **Fast tests**: Minimal ontologies load quickly
3. **Offline development**: No internet required for testing
4. **Controlled environment**: Known ontology content for predictable test results

## Full Ontologies

For production use, the system downloads and caches full ontologies from:

- **FOAF**: http://xmlns.com/foaf/0.1/
- **Schema.org**: https://schema.org/version/latest/schemaorg-current-https.rdf
- **SKOS**: http://www.w3.org/2009/08/skos-reference/skos.rdf
- **RDFS**: http://www.w3.org/2000/01/rdf-schema#

## Usage in Tests

```python
from pathlib import Path
from semantic_memory.knowledge import ProvenanceGraph

fixtures_dir = Path(__file__).parent / "fixtures" / "ontologies"

graph = ProvenanceGraph()
graph.parse(fixtures_dir / "foaf_minimal.rdf", format="xml")
graph.parse(fixtures_dir / "schema_minimal.rdf", format="xml")
```
