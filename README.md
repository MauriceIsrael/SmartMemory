# Semantic Memory MCP Server

A Model Context Protocol (MCP) server that provides semantic memory capabilities using a Knowledge Graph. It allows AI agents to store, infer, and verify facts using a persistent RDF store with **dual-level inference** (OWL-RL + custom SPARQL rules).

## Features

- ✅ **Semantic Ingestion**: Convert natural language statements into RDF triples
- ✅ **Dual-Level Inference**: 
  - Level 1: OWL-RL ontological reasoning (automatic, high confidence)
  - Level 2: Custom SPARQL CONSTRUCT rules (may require verification)
- ✅ **Smart Ontology Caching**: HTTP conditional GET for FOAF, Schema.org, SKOS, RDFS
- ✅ **Verification Loop**: Request user verification for uncertain inferences
- ✅ **Custom Rules**: Load user-defined SPARQL inference rules at runtime
- ✅ **Provenance Tracking**: Track origin, confidence, and timestamps for all facts
- ✅ **Conflict Detection**: Detect contradictory literals, disjoint classes, functional property violations
- ✅ **Persistence**: Multiple backends (Turtle, SQLite) with automatic save/load

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd SmartMemory

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Configuration for MCP Clients

**For detailed setup instructions**, see [`docs/mcp-client-setup.md`](docs/mcp-client-setup.md)

#### Claude Desktop (Quick Setup)

**macOS**: Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

**Linux**: Edit `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "semantic-memory": {
      "command": "/absolute/path/to/SmartMemory/venv/bin/python",
      "args": ["-m", "semantic_memory.server"],
      "env": {
        "SEMMEM_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

Replace `/absolute/path/to/SmartMemory` with your actual path.

**Restart Claude Desktop** to load the server.

---

## How It Works: Dual-Level Inference

SmartMemory uses a **two-level inference architecture** to automatically deduce new facts while maintaining accuracy:

```
User Input → add_memory → Storage → Level 1 (OWL-RL) → Level 2 (SPARQL) → Confidence Check → Verification (if needed)
```

### Level 1: Ontological Inference (OWL-RL)
- Automatic reasoning using FOAF, Schema.org, SKOS, RDFS ontologies
- Handles: `rdfs:subClassOf`, `rdfs:domain`, `rdfs:range`, `owl:TransitiveProperty`, `owl:SymmetricProperty`
- **Confidence**: 1.0 (ontological truth) → **Auto-accepted**

**Example**:
```
Input: "Alice knows Bob"
Level 1 Infers: "Bob knows Alice" (foaf:knows is symmetric)
```

### Level 2: Custom SPARQL Rules
- 5 default rules + user-defined rules via `load_custom_rule`
- Variable confidence (0.5-0.95 depending on rule)
- **Confidence < 0.85**: Requests user verification

**Example**:
```
Input: "Alice works at Google" + "Bob works at Google"
Level 2 Infers: "Alice colleague Bob" (confidence: 0.75)
→ Requires user confirmation
```

### Default Inference Rules

| Rule | Description | Confidence |
|------|-------------|------------|
| **spatial_transitivity** | If A in B and B in C, then A in C | 0.85 |
| **social_symmetry** | If A knows B, then B knows A | 0.90 |
| **coworkers_inference** | Same workplace → colleagues | 0.75 |
| **interest_discovery** | Created/attended topic → interest | 0.80 |
| **event_location_inheritance** | Sub-event inherits parent location | 0.85 |

See [`src/rules/defaults/`](src/rules/defaults/) for the full rule definitions.

---

## MCP Tools (7 Total)

The server exposes 7 tools for AI agents:

| Tool | Description | Use Case |
|------|-------------|----------|
| **add_memory** | Add natural language or RDF triple to knowledge graph | "Remember that Alice works at Google" |
| **query_memory** | Execute SPARQL query against the graph | "Who works at Google?" |
| **search_entity** | Full-text search for entities by name/label | "Find all people named Alice" |
| **verify_inference** | Confirm or reject uncertain inferences | Approve/reject colleague relationship |
| **load_custom_rule** | Load user-defined SPARQL CONSTRUCT rule | Add domain-specific inference logic |
| **list_rules** | List all active inference rules (default + custom) | View what rules are currently active |
| **get_graph_stats** | Get statistics (triple count, provenance, conflicts) | "How many facts do you know?" |

## MCP Prompts (5 Total)

The server also provides pre-defined **prompts** that appear in your LLM client as conversation starters:

| Prompt | Description |
|--------|-------------|
| **remember-fact** | Store a new fact (e.g., "Alice works at Google") |
| **query-knowledge** | Search for information (e.g., "Who works at Google?") |
| **add-custom-rule** | Create a custom inference rule |
| **show-stats** | Show knowledge graph statistics |
| **verify-inferences** | Review pending verifications |

In Claude Desktop, these appear as `/remember-fact`, `/query-knowledge`, etc.

---

## Usage Examples

### Example 1: Basic Memory Storage

**User**: "Alice works at Google and knows Bob"

**LLM** (uses `add_memory`):
```json
{
  "tool": "add_memory",
  "input": "Alice works at Google and knows Bob"
}
```

**Response**:
```
✓ Added 6 explicit triple(s) from your input.
✓ Inferred 2 additional triple(s) via OWL-RL reasoning.
  - Bob knows Alice (symmetric foaf:knows)

Total triples in knowledge graph: 8
```

### Example 2: Querying Knowledge

**User**: "Who do I know that works at tech companies?"

**LLM** (uses `query_memory`):
```json
{
  "tool": "query_memory",
  "query": "SELECT ?person ?company WHERE { ?person schema:worksFor ?company . ?company a schema:Organization }"
}
```

**Response**:
```
Found 1 result in 12.34 ms:

--- Result 1 ---
  person: Alice
  company: Google
```

### Example 3: Verification Workflow

**User**: "Bob also works at Google"

**LLM** (uses `add_memory`):
```
✓ Added 1 explicit triple(s)
⚠ 1 inference(s) need verification:
   - "Alice might be colleagues with Bob" (confidence: 0.75)
   Use verify_inference to confirm or reject.
```

**User**: "Yes, they work together on projects"

**LLM** (uses `verify_inference`):
```json
{
  "tool": "verify_inference",
  "triple": ":Alice schema:colleague :Bob",
  "action": "accept"
}
```

**Response**:
```
✓ Inference accepted and added to the knowledge graph.
```

### Example 4: Custom Rules

**User**: "Create a rule that infers mentorship from teaching"

**LLM** (uses `load_custom_rule`):
```json
{
  "tool": "load_custom_rule",
  "rule_id": "mentorship_inference",
  "rule_content": "PREFIX schema: <https://schema.org/>\nCONSTRUCT { ?teacher schema:mentor ?student }\nWHERE { ?course schema:instructor ?teacher . ?course schema:attendee ?student }",
  "description": "Infers mentorship from course teaching"
}
```

See [`user_rules/README.md`](user_rules/README.md) for more examples.

---

## Architecture

### Technology Stack
- **RDF Library**: `rdflib` for graph operations
- **Reasoning**: `owlrl` for OWL-RL deductive closure  
- **Protocol**: MCP Python SDK for tool exposure
- **Persistence**: Turtle (.ttl) files or SQLite
- **NLP**: Pattern matching for natural language extraction
- **Ontologies**: FOAF, Schema.org, SKOS, RDFS (cached with HTTP conditional GET)

### Project Structure

```
src/semantic_memory/
├── server.py              # MCP server entry point
├── config.py              # Configuration (env variables)
├── vocabulary.py          # Custom RDF namespace (sem:)
├── inference/
│   ├── ontology_loader.py # Smart HTTP caching
│   ├── reasoner.py        # OWL-RL reasoning
│   └── rule_engine.py     # SPARQL rule execution
├── knowledge/
│   ├── graph.py           # Provenance-aware RDF graph
│   ├── persistence.py     # Turtle/SQLite backends
│   ├── verification.py    # Verification model
│   └── conflicts.py       # Conflict detection
├── tools/                 # MCP tools (7 total)
│   ├── add_memory.py
│   ├── query_memory.py
│   ├── search_entity.py
│   ├── verify_inference.py
│   ├── load_custom_rule.py
│   ├── list_rules.py
│   └── get_graph_stats.py
└── nlp/
    └── triple_extractor.py # Natural language → RDF

src/rules/defaults/        # 5 default SPARQL rules
user_rules/                # Your custom rules
```

---

## Configuration

Configure via environment variables (prefix: `SEMMEM_`):

```bash
# Logging
export SEMMEM_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# Persistence
export SEMMEM_PERSISTENCE_PATH=~/.smartmemory/knowledge_graph.ttl
export SEMMEM_PERSISTENCE_BACKEND=turtle  # turtle, sqlite

# Caching
export SEMMEM_CACHE_DIR=~/.smartmemory/cache
export SEMMEM_CACHE_TTL_HOURS=24
export SEMMEM_FORCE_OFFLINE=false  # Use cached ontologies only

# Inference
export SEMMEM_MAX_INFERENCE_DEPTH=10  # Prevent loops
export SEMMEM_AUTO_ACCEPT_THRESHOLD=0.85  # Auto-accept if confidence ≥ 0.85

# Rules
export SEMMEM_USER_RULES_DIR=~/.smartmemory/rules
```

See [`docs/mcp-client-setup.md`](docs/mcp-client-setup.md) for full configuration examples.

---

## Provenance Tracking

Every triple has metadata:

```turtle
:Alice schema:colleague :Bob .

# Provenance metadata (RDF reification)
_:stmt1 a rdf:Statement ;
        rdf:subject :Alice ;
        rdf:predicate schema:colleague ;
        rdf:object :Bob ;
        sem:source "user-verified" ;
        sem:sourceRule <file:///rules/defaults/coworkers_inference.rq> ;
        sem:confidence 1.0 ;
        sem:timestamp "2025-11-25T14:00:00Z" ;
        sem:uncertain false .
```

Query provenance:
```sparql
SELECT ?s ?p ?o ?source ?confidence
WHERE {
  ?s ?p ?o .
  ?stmt a rdf:Statement ;
        rdf:subject ?s ; rdf:predicate ?p ; rdf:object ?o ;
        sem:source ?source ;
        sem:confidence ?confidence .
}
```

---

## Development

### Running Tests

```bash
# Run all tests
./venv/bin/pytest

# Run specific test file
./venv/bin/pytest tests/unit/test_rule_engine.py -v

# Run with coverage
./venv/bin/pytest --cov=src/semantic_memory
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

**Example**: `user_rules/collaboration_inference.rq`
```sparql
# Infers collaboration from co-authorship
PREFIX schema: <https://schema.org/>

CONSTRUCT {
    ?author1 schema:collaboratesWith ?author2 .
}
WHERE {
    ?article schema:author ?author1 .
    ?article schema:author ?author2 .
    FILTER(?author1 != ?author2)
    FILTER NOT EXISTS { ?author1 schema:collaboratesWith ?author2 }
}
```

Load at runtime:
```json
{
  "tool": "load_custom_rule",
  "rule_id": "collaboration",
  "rule_content": "<rule content>",
  "confidence": 0.80
}
```

---

## Documentation

- **[MCP Client Setup Guide](docs/mcp-client-setup.md)**: Detailed configuration for Claude, Continue.dev, Cline, Zed
- **[Realistic Dialog Scenario](docs/realistic-dialog-scenario.md)**: Example conversation with dual-level inference
- **[Error Handling](docs/error-handling.md)**: Common errors and recovery strategies
- **[Custom Rules Guide](user_rules/README.md)**: How to write SPARQL inference rules
- **[Contributing](CONTRIBUTING.md)**: Development setup and guidelines

### Specification Documents

Complete technical specifications in [`specs/003-semantic-memory-server/`](specs/003-semantic-memory-server/):
- **[spec.md](specs/003-semantic-memory-server/spec.md)**: Feature specification with 5 user stories
- **[plan.md](specs/003-semantic-memory-server/plan.md)**: Technical architecture and approach
- **[research.md](specs/003-semantic-memory-server/research.md)**: Technical decisions and rationale
- **[data-model.md](specs/003-semantic-memory-server/data-model.md)**: RDF schema and ontology mappings
- **[tasks.md](specs/003-semantic-memory-server/tasks.md)**: 96-task implementation plan (all complete)

---

## Troubleshooting

### Server won't start
```bash
# Test manually
/path/to/venv/bin/python -m semantic_memory.server

# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list | grep rdflib
```

### Tools not showing up
1. Restart MCP client completely
2. Check JSON syntax in config file
3. Verify absolute paths are correct

### Persistence errors
```bash
# Create directory
mkdir -p ~/.smartmemory
chmod 755 ~/.smartmemory

# Test write permissions
touch ~/.smartmemory/test.txt
```

See [`docs/mcp-client-setup.md#troubleshooting`](docs/mcp-client-setup.md#troubleshooting) for more solutions.

---

## License

[Specify your license here]

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code style guidelines, and how to submit pull requests.

---

## Contact & Support

- **Issues**: Report bugs via GitHub Issues
- **Discussions**: For questions and feature requests

---

**Built with ❤️ using W3C RDF standards**
