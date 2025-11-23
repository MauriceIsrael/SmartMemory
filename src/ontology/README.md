# Ontology Manager

Intelligent ontology loading system with HTTP-based caching for SmartMemory MCP server.

## Features

- **Automatic Loading**: Loads standard ontologies (FOAF, SKOS, Schema.org) at startup
- **HTTP Caching**: Uses ETag and Last-Modified headers to minimize downloads
- **Offline Mode**: Gracefully degrades to cached versions when network is unavailable
- **Integrity Validation**: Validates RDF syntax and file integrity using SHA-256 hashes
- **Atomic Operations**: Uses atomic file writes to prevent cache corruption

## Architecture

### Components

1. **OntologyRegistry** (`registry.py`)
   - Maintains list of ontologies to load
   - Hardcoded URLs for FOAF, SKOS, Schema.org
   - Extensible for custom ontologies

2. **CacheManager** (`cache.py`)
   - Manages `./cache/ontologies/` directory
   - Maintains `cache_manifest.json` with metadata
   - Validates file integrity with SHA-256 hashes

3. **OntologyFetcher** (`fetcher.py`)
   - HTTP HEAD/GET requests with conditional headers
   - RDF validation using rdflib
   - Atomic file downloads

4. **OntologyLoader** (`loader.py`)
   - Orchestrates the boot sequence
   - Loads ontologies into RDF graph
   - Provides cache management interface

## Usage

### Basic Usage

```python
from rdflib import Graph
from src.ontology import OntologyLoader

# Create RDF graph
graph = Graph()

# Initialize loader
loader = OntologyLoader(graph=graph)

# Load all ontologies
results = loader.load_all()

# Check results
for name, success in results.items():
    print(f"{name}: {'✓' if success else '✗'}")
```

### Offline Mode

```python
# Skip remote validation, use cache only
loader = OntologyLoader(graph=graph, offline_mode=True)
loader.load_all()
```

### Cache Management

```python
# Get cache status
status = loader.get_cache_status()
for name, info in status.items():
    if info['cached']:
        print(f"{name}: {info['local_path']}")

# Refresh specific ontology
loader.refresh_ontology('foaf')

# Clear cache
loader.cache_manager.clear_all()
```

### Custom Ontologies

```python
from src.ontology import OntologyRegistry, OntologySource, OntologyFormat

# Add custom ontology
custom = OntologySource(
    name="myonto",
    url="http://example.com/myonto.ttl",
    format=OntologyFormat.TURTLE,
    priority=10,
    description="My custom ontology"
)

OntologyRegistry.add_custom(custom)
```

## Boot Sequence

For each ontology:

1. **Check local cache**: Does `cache/ontologies/{name}.{ext}` exist?
2. **Validate with remote**: Send HTTP HEAD request for ETag/Last-Modified
3. **Compare metadata**: Is remote newer than cached version?
4. **Download if needed**: GET request + RDF validation + atomic write
5. **Load into graph**: Parse cached file into RDF graph

## Cache Structure

```
cache/
├── ontologies/
│   ├── foaf.rdf          # Cached FOAF ontology
│   ├── skos.rdf          # Cached SKOS ontology
│   └── schema.turtle     # Cached Schema.org ontology
└── cache_manifest.json   # Metadata (ETag, Last-Modified, hashes)
```

### Manifest Format

```json
{
  "ontologies": {
    "foaf": {
      "url": "http://xmlns.com/foaf/0.1/",
      "local_path": "cache/ontologies/foaf.rdf",
      "etag": "\"abc123\"",
      "last_modified": "Wed, 21 Oct 2025 07:28:00 GMT",
      "downloaded_at": "2025-11-22T16:00:00Z",
      "file_hash": "sha256:..."
    }
  }
}
```

## Error Handling

- **Network failures**: Falls back to cached version (fail-safe mode)
- **Invalid RDF**: Logs error and skips ontology
- **Corrupted cache**: Re-downloads ontology
- **Missing cache**: Downloads fresh copy

## Performance

- **Cold start** (first run): < 2 seconds (depends on network)
- **Warm start** (with cache): < 100ms
- **Cache validation**: ~500ms (HTTP HEAD requests)

## Testing

```bash
# Run unit tests
pytest tests/ontology/ -v

# Run example
PYTHONPATH=. python examples/ontology_loader_example.py
```

## Integration with MCP Server

```python
from rdflib import Graph
from src.ontology import OntologyLoader

# In server startup
graph = Graph()
loader = OntologyLoader(graph=graph)
loader.load_all()

# Graph now contains FOAF, SKOS, Schema.org ontologies
# Ready for inference engine
```

## Loaded Ontologies

| Name | Description | Triples | Format |
|------|-------------|---------|--------|
| FOAF | Friend of a Friend - people and relationships | ~600 | RDF/XML |
| SKOS | Simple Knowledge Organization System | ~250 | RDF/XML |
| Schema.org | Structured data vocabulary | ~17,000 | Turtle |

## Dependencies

- `rdflib`: RDF parsing and graph operations
- `requests`: HTTP client with caching support
