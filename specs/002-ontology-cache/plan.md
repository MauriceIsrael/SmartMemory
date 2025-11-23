# Implementation Plan: Ontology Loader with Intelligent Caching

**Branch**: `002-ontology-cache` | **Date**: 2025-11-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-ontology-cache/spec.md`

## Summary

Build an autonomous ontology management system that loads standard ontologies (FOAF, SKOS, Schema.org subset) at startup with intelligent HTTP caching. The system will verify local copies, check for updates using HTTP ETag/Last-Modified headers, and gracefully degrade to cached versions when offline. This provides the MCP server with foundational "general knowledge" before user interaction begins.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: `rdflib`, `requests` (for HTTP HEAD/GET with caching headers)  
**Storage**: Local cache directory `./cache/ontologies/` for ontology files (.ttl, .rdf), `cache_manifest.json` for metadata (ETag, Last-Modified, timestamps)  
**Testing**: pytest with `responses` library for HTTP mocking  
**Target Platform**: Linux server (compatible with existing MCP server)  
**Project Type**: single project  
**Performance Goals**: Ontology loading < 2s on cold start, < 100ms on warm start with valid cache  
**Constraints**: Must work offline (fail-safe mode), cache validation should not block server startup  
**Scale/Scope**: ~3-5 standard ontologies initially (FOAF, SKOS, Schema.org subset), extensible architecture

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

*   **No "Flat" Data:** Is all knowledge structured as triples or quads?
*   **Active, Not Passive:** Does the design include inference capabilities?
*   **Trust but Verify:** Is there a mechanism for user confirmation of inferences?
*   **Language:** Is the implementation using Python 3.11+ or TypeScript?
*   **Standards:** Does the design adhere to RDF, RDFS, OWL, SHACL?
*   **Protocol:** Is the MCP implemented?
*   **Type Safety:** Is the code fully typed?
*   **Ontology First:** Are standard or pre-defined ontologies used?
*   **Immutability:** Are stated and inferred facts kept separate?
*   **Interaction Model:** Does the system act as a "Gardener"?

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── ontology/                    # NEW: Ontology management module
│   ├── __init__.py
│   ├── loader.py               # Ontology loading orchestration
│   ├── cache.py                # Cache management (ETag, Last-Modified)
│   ├── fetcher.py              # HTTP fetching with header validation
│   └── registry.py             # Ontology registry (FOAF, SKOS, Schema.org)
├── models/                      # Existing
├── services/                    # Existing
├── cli/                         # Existing
└── lib/                         # Existing

tests/
├── ontology/                    # NEW: Tests for ontology module
│   ├── test_loader.py
│   ├── test_cache.py
│   ├── test_fetcher.py
│   └── fixtures/                # Mock ontology files
├── contract/                    # Existing
├── integration/                 # Existing
└── unit/                        # Existing

cache/                           # NEW: Local cache directory (gitignored)
├── ontologies/                  # Cached .ttl/.rdf files
└── metadata.db                  # SQLite cache metadata
```

**Structure Decision**: Single project structure extended with new `src/ontology/` module for ontology management. The cache directory will be created at runtime and excluded from version control.

## OntologyManager Architecture

### Core Components

1. **OntologyRegistry** (`src/ontology/registry.py`)
   - Maintains hardcoded list of ontology URLs to load:
     - FOAF: `http://xmlns.com/foaf/0.1/`
     - SKOS: `http://www.w3.org/2004/02/skos/core#`
     - Schema.org: Curated subset (to be defined)
   - Each entry includes: URL, preferred format (turtle/rdf-xml), priority/load order

2. **CacheManager** (`src/ontology/cache.py`)
   - Manages `./cache/ontologies/` directory
   - Reads/writes `cache_manifest.json` with structure:
     ```json
     {
       "ontologies": {
         "foaf": {
           "url": "http://xmlns.com/foaf/0.1/",
           "local_path": "./cache/ontologies/foaf.ttl",
           "etag": "\"abc123\"",
           "last_modified": "Wed, 21 Oct 2025 07:28:00 GMT",
           "downloaded_at": "2025-11-22T16:00:00Z",
           "file_hash": "sha256:..."
         }
       }
     }
     ```
   - Validates file integrity using stored hash

3. **OntologyFetcher** (`src/ontology/fetcher.py`)
   - Performs HTTP HEAD requests to check Last-Modified/ETag
   - Downloads ontologies via GET when needed
   - Validates downloaded RDF using `rdflib.Graph().parse()`
   - Uses atomic file writes (temp file + rename) to prevent corruption

4. **OntologyLoader** (`src/ontology/loader.py`)
   - Orchestrates the boot sequence (see below)
   - Loads all cached ontologies into the in-memory RDF graph
   - Provides interface for manual cache refresh

### Boot Sequence Logic

```python
# Pseudocode for OntologyLoader.load_all()
for ontology in OntologyRegistry.get_all():
    cache_entry = CacheManager.get_entry(ontology.name)
    
    # Step 1: Check if local file exists
    if cache_entry and cache_entry.local_path.exists():
        try:
            # Step 2: Validate with remote (HEAD request)
            remote_headers = OntologyFetcher.get_headers(ontology.url)
            
            # Step 3: Compare metadata
            if needs_update(cache_entry, remote_headers):
                # Remote is newer, download
                download_and_cache(ontology)
            else:
                # Local is current, use cache
                log.info(f"{ontology.name}: Using cached version")
        except NetworkError:
            # Step 4: Fail-safe - use cached version
            log.warning(f"{ontology.name}: Network unavailable, using cache")
    else:
        # No local file, must download
        try:
            download_and_cache(ontology)
        except NetworkError:
            log.error(f"{ontology.name}: Cannot download, no cache available")
            continue  # Skip this ontology
    
    # Step 5: Load into in-memory graph
    load_into_graph(cache_entry.local_path)

def download_and_cache(ontology):
    # Download to temp file
    temp_file = OntologyFetcher.download(ontology.url)
    
    # Validate RDF integrity
    try:
        graph = rdflib.Graph()
        graph.parse(temp_file, format=ontology.format)
    except Exception as e:
        raise ValidationError(f"Invalid RDF: {e}")
    
    # Calculate hash
    file_hash = calculate_sha256(temp_file)
    
    # Atomic move to cache
    final_path = f"./cache/ontologies/{ontology.name}.ttl"
    temp_file.rename(final_path)
    
    # Update manifest
    CacheManager.update_entry(ontology.name, {
        "url": ontology.url,
        "local_path": final_path,
        "etag": response.headers.get("ETag"),
        "last_modified": response.headers.get("Last-Modified"),
        "downloaded_at": datetime.utcnow().isoformat(),
        "file_hash": file_hash
    })
```

### Integration with Inference Engine

Once all ontologies are loaded into the in-memory graph:

1. **Initialize SPARQL Engine**: The loaded ontologies provide the foundational vocabulary (classes, properties, relationships)
2. **Load Inference Rules**: SPARQL CONSTRUCT rules can reference ontology terms (e.g., `foaf:knows`, `skos:broader`)
3. **Execute Inferences**: The inference engine can now make deductions based on both:
   - User-provided data (from MCP interactions)
   - Ontology definitions (RDFS/OWL semantics)

**Example**: If user states "Alice knows Bob", and FOAF ontology defines `foaf:knows` as symmetric, the inference engine can deduce "Bob knows Alice".

## Implementation Phases

### Phase 0: Research & Design
- [ ] Research FOAF, SKOS, Schema.org ontology URLs and formats
- [ ] Design `cache_manifest.json` schema
- [ ] Define error handling strategy (network failures, parse errors, etc.)
- [ ] Document integration points with existing MCP server

### Phase 1: Core Implementation
- [ ] Implement `OntologyRegistry` with hardcoded ontology list
- [ ] Implement `CacheManager` with JSON manifest read/write
- [ ] Implement `OntologyFetcher` with HEAD/GET requests and validation
- [ ] Implement `OntologyLoader` with boot sequence logic
- [ ] Add cache directory initialization and `.gitignore` entry

### Phase 2: Integration & Testing
- [ ] Integrate `OntologyLoader` into MCP server startup
- [ ] Write unit tests for each component (with mocked HTTP)
- [ ] Write integration tests for boot sequence scenarios
- [ ] Test offline fail-safe mode
- [ ] Performance testing (cold/warm start times)

### Phase 3: Inference Engine Connection
- [ ] Verify loaded ontologies are accessible to SPARQL engine
- [ ] Create example inference rules using ontology terms
- [ ] Test end-to-end: ontology load → user input → inference → result

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
