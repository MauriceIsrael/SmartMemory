# Semantic Memory MCP Server

A Model Context Protocol (MCP) server that provides semantic memory capabilities using a Knowledge Graph. It allows AI agents to store, infer, and verify facts using a persistent RDF store.

## Features

- **Semantic Ingestion**: Convert natural language statements into RDF triples
- **Hybrid Inference Engine**: Two-level reasoning (OWL-RL ontologies + SPARQL CONSTRUCT rules)
- **Smart Ontology Caching**: HTTP conditional GET for FOAF, Schema.org, SKOS, RDFS
- **Verification Loop**: Request user verification for uncertain inferences
- **Custom Rules**: Load user-defined SPARQL inference rules at runtime
- **Provenance Tracking**: Track origin and confidence of all facts
- **Persistence**: Multiple backends (Turtle, SQLite, Oxigraph)

## Installation

1.  **Prerequisites**: Python 3.11 or higher.
2.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd SmartMemory
    ```
3.  **Set up a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  **Install dependencies**:
    ```bash
    # For production use
    pip install -e .

    # For development (includes pytest, mypy, black, ruff)
    pip install -e .[dev]
    ```

## Usage

### Running the Server

The MCP server is designed to be launched by MCP-compatible clients (Claude Desktop, IDEs, etc.):

```bash
python -m semantic_memory.server
```

### MCP Tools

The server exposes 8 tools for AI agents:

| Tool | Description |
|------|-------------|
| **add_memory** | Add natural language statement or RDF triple to knowledge graph |
| **query_memory** | Execute SPARQL query against the graph |
| **search_entity** | Full-text search for entities by name/label |
| **verify_inference** | Confirm or reject uncertain inferences |
| **load_custom_rule** | Load user-defined SPARQL CONSTRUCT rule |
| **list_rules** | List all active inference rules (default + custom) |
| **get_graph_stats** | Get statistics (triple count, provenance breakdown) |

### Quick Examples

**Add a memory from natural language:**
```json
{
  "tool": "add_memory",
  "input": "Alice works at Google and knows Bob"
}
```

**Query the graph:**
```json
{
  "tool": "query_memory",
  "query": "SELECT ?person WHERE { ?person schema:worksFor ?company }"
}
```

**Search for an entity:**
```json
{
  "tool": "search_entity",
  "search_term": "Alice"
}
```

## MCP Client Configuration

To use this MCP server with Claude Desktop or other MCP clients, add to your MCP settings file:

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):
```json
{
  "mcpServers": {
    "semantic-memory": {
      "command": "/absolute/path/to/SmartMemory/venv/bin/python",
      "args": ["-m", "semantic_memory.server"]
    }
  }
}
```

**Other MCP Clients:**
```json
{
  "mcpServers": {
    "semantic-memory": {
      "command": "python",
      "args": ["-m", "semantic_memory.server"],
      "cwd": "/absolute/path/to/SmartMemory"
    }
  }
}
```

*Note: Replace `/absolute/path/to/SmartMemory` with the actual path to your project directory.*

## How It Works: Hybrid Inference Architecture

SmartMemory uses a two-level inference approach to automatically deduce new facts while maintaining accuracy.

### Two-Level Inference

```
User Input → add_memory → Storage → Level 1 (OWL-RL) → Level 2 (SPARQL) → Confidence Check → Verification (if needed)
```

**Level 1: Ontological Inference (OWL-RL)**
- Automatic reasoning using FOAF, Schema.org, SKOS, RDFS ontologies
- Handles: rdfs:subClassOf, rdfs:domain, rdfs:range, owl:TransitiveProperty, owl:SymmetricProperty
- High confidence (automatically accepted)

**Level 2: Custom SPARQL Rules**
- 5 default rules: spatial transitivity, social symmetry, coworkers, interests, event locations
- User-defined rules loaded via `load_custom_rule` tool
- Variable confidence (may require verification)

### Example Inference Flow

**1. User adds a memory:**
> "Alice works at Google. Bob works at Google."

**2. System stores RDF triples:**
```turtle
:Alice schema:worksFor :Google .
:Bob schema:worksFor :Google .
```

**3. Level 1 (OWL-RL)**: No immediate inferences

**4. Level 2 (SPARQL)**: Coworkers rule fires
```sparql
# coworkers_inference.rq
CONSTRUCT { ?person1 schema:colleague ?person2 }
WHERE {
  ?person1 schema:worksFor ?org .
  ?person2 schema:worksFor ?org .
  FILTER(?person1 != ?person2)
}
```

**5. System infers:**
```turtle
:Alice schema:colleague :Bob .
:Bob schema:colleague :Alice .
```

**6. Confidence check:**
- Default rule confidence: 0.85 (auto-accept threshold: 0.80)
- Triples automatically added with provenance:
```turtle
:Alice schema:colleague :Bob .
  sem:source "sparql-rule" ;
  sem:sourceRule <file:///src/rules/defaults/coworkers_inference.rq> ;
  sem:confidence 0.85 ;
  sem:timestamp "2025-11-23T10:30:00Z" .
```

### Default Inference Rules

| Rule | Description | Example |
|------|-------------|---------|
| **spatial_transitivity.rq** | If A in B and B in C, then A in C | Room → Building → City |
| **social_symmetry.rq** | If A knows B, then B knows A | foaf:knows symmetry |
| **coworkers_inference.rq** | Same workplace → colleagues | Both at Google → coworkers |
| **interest_discovery.rq** | Created/attended topic → interest | Created AI article → interested in AI |
| **event_location_inheritance.rq** | Sub-event inherits parent location | Workshop at Conference venue |

### Verification for Uncertain Inferences

When confidence < 0.80, the system asks for verification:

```json
{
  "tool": "verify_inference",
  "verification_id": "inf_12345",
  "confirmed": true,
  "feedback": "Yes, they are colleagues"
}
```

### Benefits

✅ **Automatic**: High-confidence inferences happen without user intervention
✅ **Transparent**: All inferences tracked with provenance metadata
✅ **Extensible**: Users can add custom SPARQL rules at runtime
✅ **Accurate**: Low-confidence inferences require verification

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/semantic_memory --cov-report=html

# Run specific test file
pytest tests/unit/test_inference_engine.py
```

### Code Quality

```bash
# Type checking
mypy src/

# Code formatting
black src/ tests/

# Linting
ruff check src/ tests/
```

### Adding Custom Inference Rules

Create a SPARQL CONSTRUCT query in `user_rules/`:

**Example: `user_rules/mentor_relationship.rq`**
```sparql
# Infers mentorship from teaching relationship
PREFIX schema: <https://schema.org/>

CONSTRUCT {
    ?teacher schema:mentor ?student .
}
WHERE {
    ?course schema:instructor ?teacher .
    ?course schema:attendee ?student .
    FILTER NOT EXISTS { ?teacher schema:mentor ?student }
}
```

Load at runtime via MCP tool:
```json
{
  "tool": "load_custom_rule",
  "rule_name": "mentor_relationship",
  "sparql_construct": "...",
  "confidence": 0.75
}
```

## Documentation

Comprehensive documentation is available in `specs/003-semantic-memory-server/`:

- **spec.md**: Feature specification with 5 user stories
- **plan.md**: Technical architecture and implementation approach
- **research.md**: Technical decisions and rationale
- **data-model.md**: RDF schema and ontology mappings
- **contracts/mcp-tools.yaml**: Complete MCP tool API reference
- **quickstart.md**: Test scenarios and usage examples
- **tasks.md**: 96-task implementation plan

## License

[Specify your license here]

## Contributing

[Specify contribution guidelines here]
