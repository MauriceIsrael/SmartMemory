# SmartMemory Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-22

## Active Technologies
- Turtle (.ttl) files (001-semantic-memory-mcp)
- Python 3.11+ + `rdflib`, `httpx` (for async HTTP with caching headers), `aiofiles` (for async file I/O) (002-ontology-cache)
- Local cache directory for ontology files (.ttl, .rdf), SQLite for cache metadata (ETag, Last-Modified, timestamps) (002-ontology-cache)
- Python 3.11+ + `rdflib`, `requests` (for HTTP HEAD/GET with caching headers) (002-ontology-cache)
- Local cache directory `./cache/ontologies/` for ontology files (.ttl, .rdf), `cache_manifest.json` for metadata (ETag, Last-Modified, timestamps) (002-ontology-cache)
- Backend: Python 3.11+; Frontend: TypeScript/Svelte + Backend: FastAPI, rdflib; Frontend: SvelteKit (006-toggle-inference-filters)
- File-based RDF graph (persisted via `rdflib` store) (006-toggle-inference-filters)

- Python 3.11+ + `mcp-sdk`, `rdflib` (001-semantic-memory-mcp)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes
- 006-toggle-inference-filters: Added Backend: Python 3.11+; Frontend: TypeScript/Svelte + Backend: FastAPI, rdflib; Frontend: SvelteKit
- 005-inference-supervision-dashboard: Added [if applicable, e.g., PostgreSQL, CoreData, files or N/A]


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
