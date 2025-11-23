# SmartMemory Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-22

## Active Technologies

- Python 3.11+ (003-semantic-memory-server)
- RDFLib for RDF graph manipulation (003-semantic-memory-server)
- owlrl for OWL-RL reasoning and deductive closure (003-semantic-memory-server)
- MCP Python SDK for Model Context Protocol (003-semantic-memory-server)
- requests for HTTP client with caching headers (ETag, Last-Modified) (003-semantic-memory-server)
- pydantic for data validation and settings management (003-semantic-memory-server)
- Turtle (.ttl) files for RDF serialization (001-semantic-memory-mcp, 003-semantic-memory-server)
- SQLite for optional persistence backend (003-semantic-memory-server)
- pytest with pytest-asyncio for testing (003-semantic-memory-server)

## Project Structure

```text
src/
├── semantic_memory/      # Main MCP server package
│   ├── server.py        # MCP server entry point
│   ├── inference/       # OWL-RL reasoner & SPARQL rule engine
│   ├── knowledge/       # RDF graph with provenance tracking
│   ├── tools/           # MCP tools (add_memory, query_memory, etc.)
│   ├── nlp/             # Natural language to RDF conversion
│   └── config.py        # Configuration management
├── rules/
│   └── defaults/        # Default SPARQL inference rules (.rq files)
└── user_rules/          # User-defined custom SPARQL rules

tests/
├── unit/                # Unit tests
├── integration/         # Integration tests
└── fixtures/            # Test data (ontologies, rules)
```

## Commands

```bash
# Development
cd src
python -m semantic_memory.server  # Start MCP server
pytest                            # Run tests
mypy --strict .                   # Type checking
black .                           # Format code
ruff check .                      # Lint code

# Testing specific features
pytest tests/unit/                # Unit tests only
pytest tests/integration/         # Integration tests only
pytest -k "test_ontology"         # Run specific test pattern
```

## Code Style

- Python 3.11+: Follow PEP 8 conventions
- Type hints required: Use mypy strict mode
- Async/await: Use for MCP tools and I/O operations
- RDF URIs: Use standard ontology namespaces (FOAF, Schema.org, RDFS, SKOS)
- SPARQL rules: Include PREFIX declarations, use FILTER NOT EXISTS to prevent duplicates
- Provenance: Always track source of triples (user/owlrl/sparql-rule)

## Recent Changes

- 003-semantic-memory-server: Added Python 3.11+, RDFLib, owlrl, MCP SDK, requests, pydantic
- 003-semantic-memory-server: Defined project structure with semantic_memory package
- 003-semantic-memory-server: Specified 5 default SPARQL rules and custom rule support
- 002-ontology-cache: Added ontology caching with HTTP conditional GET
- 001-semantic-memory-mcp: Initial MCP server structure with RDF support

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
