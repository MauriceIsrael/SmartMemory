# Implementation Plan: Semantic Memory MCP Server

**Branch**: `003-semantic-memory-server` | **Date**: 2025-11-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-semantic-memory-server/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

The Semantic Memory MCP Server is an active knowledge graph system that stores information as RDF triples and automatically infers new facts through a hybrid inference architecture. Unlike passive memory systems, it combines ontological reasoning (Level 1) with custom SPARQL rules (Level 2) to deduce implicit knowledge, while supporting uncertainty handling through an elicitation loop that requests user verification for ambiguous inferences.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- `rdflib` (RDF graph manipulation and querying)
- `owlrl` (OWL-RL reasoning and deductive closure)
- `mcp` (Model Context Protocol SDK for Python)
- `requests` (HTTP client for ontology downloading)
- `pydantic` (data validation and settings management)

**Storage**:
- In-memory RDF graph during runtime (rdflib.Graph)
- Persistent storage: Turtle (.ttl) files by default, with optional SQLite or Oxigraph backends

**Testing**: pytest with pytest-asyncio for async MCP tool testing
**Target Platform**: Linux/macOS/Windows server (Python cross-platform)
**Project Type**: Single MCP server application
**Performance Goals**:
- Query response time < 500ms for graphs up to 10,000 triples
- Inference completion < 5 seconds on startup for 10,000 triples
- Rule validation feedback < 1 second

**Constraints**:
- Must adhere to W3C RDF/RDFS/OWL standards
- Must implement MCP protocol for tool exposure
- Cycle detection required to prevent infinite inference loops
- Offline operation with cached ontologies

**Scale/Scope**:
- Support 10,000+ triples in knowledge graph
- Handle 5-20 SPARQL rules (default + custom)
- Support 4 standard ontologies (FOAF, SKOS, RDFS, Schema.org Lite)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ **No "Flat" Data:** Yes - all data stored as RDF triples (subject-predicate-object)
- ✅ **Active, Not Passive:** Yes - automatic inference through OWL-RL + SPARQL rules
- ✅ **Trust but Verify:** Yes - uncertainty handling with verification requests (FR-006)
- ✅ **Language:** Yes - Python 3.11+ using RDFLib ecosystem
- ✅ **Standards:** Yes - strict W3C RDF/RDFS/OWL compliance
- ✅ **Protocol:** Yes - implements MCP for tool exposure (`add_memory`, query tools)
- ✅ **Type Safety:** Yes - full typing with mypy strict mode
- ✅ **Ontology First:** Yes - uses FOAF, SKOS, RDFS, Schema.org (no ad-hoc predicates)
- ✅ **Immutability:** Yes - provenance tracking distinguishes stated vs inferred facts (FR-015)
- ✅ **Interaction Model:** Yes - "Gardener" model with automatic inference, conflict detection, and consistency checking

**Gate Status**: ✅ PASS - All constitution principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/003-semantic-memory-server/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── mcp-tools.yaml   # MCP tool definitions
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── semantic_memory/
│   ├── __init__.py
│   ├── server.py              # MCP server entry point
│   ├── inference/
│   │   ├── __init__.py
│   │   ├── ontology_loader.py # Load and cache FOAF, SKOS, RDFS, Schema.org
│   │   ├── reasoner.py         # OWL-RL deductive closure (Level 1)
│   │   └── rule_engine.py      # SPARQL CONSTRUCT executor (Level 2)
│   ├── knowledge/
│   │   ├── __init__.py
│   │   ├── graph.py            # RDF graph wrapper with provenance
│   │   └── persistence.py      # Save/load graph (Turtle/SQLite/Oxigraph)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── add_memory.py       # MCP tool: NL -> RDF conversion
│   │   ├── query_memory.py     # MCP tool: SPARQL query interface
│   │   └── verify_inference.py # MCP tool: confirm/reject uncertain inferences
│   ├── nlp/
│   │   ├── __init__.py
│   │   └── triple_extractor.py # Convert natural language to triples
│   └── config.py               # Settings (cache dir, persistence format, etc.)
├── rules/
│   └── defaults/               # Default SPARQL .rq files
│       ├── spatial_transitivity.rq
│       ├── social_symmetry.rq
│       ├── coworkers_inference.rq
│       ├── interest_discovery.rq
│       └── event_location_inheritance.rq
└── user_rules/                 # User-defined custom rules (empty by default)

tests/
├── unit/
│   ├── test_ontology_loader.py
│   ├── test_reasoner.py
│   ├── test_rule_engine.py
│   ├── test_graph.py
│   ├── test_persistence.py
│   └── test_triple_extractor.py
├── integration/
│   ├── test_inference_pipeline.py
│   ├── test_mcp_tools.py
│   └── test_persistence_recovery.py
└── fixtures/
    ├── ontologies/             # Cached test ontologies
    └── test_rules/             # Test SPARQL rules

pyproject.toml                  # Poetry or setuptools config
README.md
.gitignore
```

**Structure Decision**: Single project structure selected because:
- MCP server is a standalone Python application
- No frontend/backend split (backend only)
- All components tightly integrated around RDF graph
- Rules directory at root level for easy user access to custom rules

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - all constitution principles are satisfied by the design.
