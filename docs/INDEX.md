# SmartMemory Documentation Index

Complete guide to SmartMemory documentation.

## For New Users

### Start Here 👈

1. **[README.md](../README.md)** - Project overview, features, and basic setup
2. **[Quick Start Guide](quick-start.md)** - Step-by-step tutorial (15 minutes)
3. **[MCP Client Setup](mcp-client-setup.md)** - Configure Claude, Continue.dev, Cline, etc.

## User Guides

### Basic Usage

- **[Quick Start Guide](quick-start.md)**
  - Installation steps
  - First-time setup
  - Basic operations tutorial
  - Common use cases
  - Troubleshooting basics

- **[Realistic Dialog Scenario](realistic-dialog-scenario.md)**
  - Example conversation with full context
  - Dual-level inference demonstration
  - Verification workflow walkthrough
  - Provenance tracking explained

### Configuration

- **[MCP Client Setup](mcp-client-setup.md)**
  - Claude Desktop (macOS, Linux, Windows)
  - Continue.dev (VS Code)
  - Cline (VS Code)
  - Zed Editor
  - Custom MCP clients
  - Environment variables reference
  - Complete troubleshooting guide

### Advanced Topics

- **[Custom Rules Guide](../user_rules/README.md)**
  - SPARQL CONSTRUCT syntax
  - Rule examples (5 patterns)
  - Best practices
  - Debugging rules

- **[Error Handling](error-handling.md)**
  - Common error scenarios
  - Network failures
  - Persistence errors
  - SPARQL query errors
  - Recovery strategies

## Developer Resources

### Getting Started

- **[CONTRIBUTING.md](../CONTRIBUTING.md)**
  - Development setup
  - Running tests
  - Code style (black, ruff, mypy)
  - Pull request process

### Technical Specifications

Located in [`specs/003-semantic-memory-server/`](../specs/003-semantic-memory-server/):

1. **[spec.md](../specs/003-semantic-memory-server/spec.md)**
   - 5 user stories
   - Acceptance criteria
   - Success metrics

2. **[plan.md](../specs/003-semantic-memory-server/plan.md)**
   - Architecture overview
   - Technology stack
   - Project structure
   - Testing strategy

3. **[research.md](../specs/003-semantic-memory-server/research.md)**
   - Design decisions
   - Alternative approaches
   - Trade-offs

4. **[data-model.md](../specs/003-semantic-memory-server/data-model.md)**
   - RDF schema
   - Ontology mappings
   - Namespace definitions
   - Provenance model

5. **[tasks.md](../specs/003-semantic-memory-server/tasks.md)**
   - 96 implementation tasks
   - All marked complete
   - Grouped by phase

## Quick Reference

### I want to...

**...get started quickly** → [Quick Start Guide](quick-start.md)

**...configure Claude Desktop** → [MCP Client Setup § Claude Desktop](mcp-client-setup.md#claude-desktop)

**...configure Continue.dev** → [MCP Client Setup § Continue.dev](mcp-client-setup.md#continuedev-vs-code)

**...see a real example** → [Realistic Dialog Scenario](realistic-dialog-scenario.md)

**...create custom rules** → [Custom Rules Guide](../user_rules/README.md)

**...understand the architecture** → [README.md § Architecture](../README.md#architecture)

**...troubleshoot errors** → [MCP Client Setup § Troubleshooting](mcp-client-setup.md#troubleshooting)

**...understand inference** → [README.md § Dual-Level Inference](../README.md#how-it-works-dual-level-inference)

**...contribute code** → [CONTRIBUTING.md](../CONTRIBUTING.md)

**...understand provenance** → [README.md § Provenance Tracking](../README.md#provenance-tracking)

### By Tool

- **add_memory**: [README § Example 1](../README.md#example-1-basic-memory-storage), [Quick Start § Storing](quick-start.md#a-storing-information)
- **query_memory**: [README § Example 2](../README.md#example-2-querying-knowledge), [Quick Start § Querying](quick-start.md#b-querying-information)
- **verify_inference**: [README § Example 3](../README.md#example-3-verification-workflow), [Dialog Scenario](realistic-dialog-scenario.md#3-verification-request)
- **load_custom_rule**: [README § Example 4](../README.md#example-4-custom-rules), [Custom Rules Guide](../user_rules/README.md)
- **list_rules**: [Quick Start § Viewing Stats](quick-start.md#c-viewing-statistics)
- **get_graph_stats**: [Quick Start § Viewing Stats](quick-start.md#c-viewing-statistics)
- **search_entity**: [Quick Start § Simple Search](quick-start.md#b-querying-information)

## Documentation Roadmap

### ✅ Complete

- Installation and setup guides
- MCP client configuration for all major clients
- Usage examples and tutorials
- Custom rule writing guide
- Error handling and troubleshooting
- Technical specifications

### 🚧 Planned

- Video tutorials
- Graph visualization how-to
- Migration guides (from other knowledge bases)
- API reference (auto-generated from code)
- Performance optimization guide
- Production deployment best practices

## Contributing to Docs

See [CONTRIBUTING.md § Documentation](../CONTRIBUTING.md) for:
- Documentation style guide
- How to add examples
- How to update specs

---

**Last Updated**: 2025-11-25
