# Changelog

All notable changes to SmartMemory will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-02

### Added - Initial Release 🎉

**Core Features:**
- RDF knowledge graph with provenance tracking
- 12 MCP tools for AI assistants (Claude, Gemini)
- SPARQL inference rule engine
- Human-in-the-loop verification workflow
- Conversational rule learning (LLM proposes → user approves)

**MCP Tools:**
- `add_memory`: Store facts from natural language
- `query_memory`: SPARQL queries
- `verify_inference`: Verify formal proofs
- `suggest_rule`: LLM proposes SPARQL rules
- `approve_rule`/`reject_rule`: Rule approval workflow
- `get_pending_rules`: List pending approvals
- `get_pending_verifications`: Review uncertain facts
- `list_rules`: Show active inference rules
- `load_custom_rule`: Add custom SPARQL rules
- `search_entity`: Full-text entity search
- `get_graph_stats`: Knowledge graph statistics

**Documentation:**
- Getting started guide with MCP setup
- Architecture overview
- Custom rules examples
- Standalone demo script

**Infrastructure:**
- MIT License
- Python 3.11+ support
- RDFLib + OWL-RL reasoning
- Turtle persistence format

### Known Limitations

- No web UI (terminal/MCP only)
- SPARQL rule syntax required for custom rules
- English language and other biases in NLP extraction
- No distributed graph support

---

## [Unreleased]

Ideas for future releases:
- [ ] Web dashboard for graph visualization
- [ ] Natural language → SPARQL compiler
- [ ] Multi-language support
- [ ] GraphQL API
- [ ] Rule templates library
- [ ] Confidence score learning
