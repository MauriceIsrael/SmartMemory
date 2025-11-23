# Feature Specification: Semantic Memory MCP Server

**Feature Branch**: `003-semantic-memory-server`
**Created**: 2025-11-22
**Status**: Draft
**Input**: User description: "Je souhaite spécifier et développer un serveur MCP (Model Context Protocol) nommé **'Semantic Memory'**. Contrairement aux serveurs de mémoire passifs (JSON/Vector), celui-ci agit comme un graphe de connaissances actif capable de raisonnement."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Memory Storage and Automatic Inference (Priority: P1)

An AI agent needs to store information about entities and relationships in natural language, and the system should automatically infer additional facts based on loaded ontologies without requiring explicit programming.

**Why this priority**: This is the core differentiator from passive memory systems. The automatic inference capability is the foundation that makes this system "active" rather than passive.

**Independent Test**: Can be fully tested by storing a simple statement like "John is a Person" and verifying that the system automatically infers parent class relationships (e.g., "John is an Agent" if Person subClassOf Agent in FOAF ontology). Delivers immediate value by reducing the amount of explicit data the AI needs to store.

**Acceptance Scenarios**:

1. **Given** an empty knowledge graph, **When** an AI agent adds the memory "Alice works at TechCorp" in natural language, **Then** the system converts it to RDF triples and stores them in the graph
2. **Given** FOAF ontology is loaded stating "Person subClassOf Agent", **When** the system stores "Bob rdf:type Person", **Then** the system automatically infers and materializes "Bob rdf:type Agent" through deductive closure
3. **Given** stored memories about an entity, **When** an AI agent queries for information about that entity, **Then** the system returns both explicitly stored facts and automatically inferred facts

---

### User Story 2 - Custom Business Logic Rules (Priority: P2)

A user needs to define domain-specific reasoning rules that go beyond standard ontology inference, such as "if person X lives in city Y, and city Y is in country Z, then person X resides in country Z".

**Why this priority**: Extends the inference capabilities beyond standard ontologies to support domain-specific logic. Essential for real-world applications but can be implemented after basic inference works.

**Independent Test**: Can be tested by creating a SPARQL CONSTRUCT rule file for spatial transitivity, loading it into the system, storing location data, and verifying that transitive relationships are correctly inferred. Delivers value by enabling custom business logic without code changes.

**Acceptance Scenarios**:

1. **Given** a SPARQL CONSTRUCT rule defining spatial transitivity, **When** the system starts up, **Then** it loads and validates all rules from both default and custom rule directories
2. **Given** stored facts "Alice lives in Paris" and "Paris is in France", **When** the spatial transitivity rule executes, **Then** the system infers "Alice resides in France"
3. **Given** a user-defined rule file in the custom rules directory, **When** the system starts, **Then** the custom rules are loaded and executed alongside default rules
4. **Given** multiple rules that could apply to the same data, **When** inference runs, **Then** all applicable rules execute and their results are merged without conflicts

---

### User Story 3 - Uncertainty Handling and User Verification (Priority: P2)

The system encounters an inference that has uncertain confidence (e.g., "person X might know person Y based on shared affiliations") and needs to request verification from the user before treating it as fact.

**Why this priority**: Critical for maintaining knowledge graph integrity and avoiding false inferences. Prevents the system from polluting the knowledge base with uncertain information.

**Independent Test**: Can be tested by creating a rule that produces uncertain inferences (with a confidence flag), triggering it with test data, and verifying that the system returns a verification request structure rather than directly asserting the fact. Delivers value by maintaining high data quality.

**Acceptance Scenarios**:

1. **Given** a rule that generates inferences with uncertainty flags, **When** the rule produces an uncertain inference, **Then** the system does NOT directly insert it into the knowledge graph
2. **Given** an uncertain inference has been generated, **When** the system processes it, **Then** it returns a structured verification request to the AI agent for user confirmation
3. **Given** a user confirms an uncertain inference, **When** the confirmation is received, **Then** the system inserts the fact into the knowledge graph with appropriate provenance metadata
4. **Given** a user rejects an uncertain inference, **When** the rejection is received, **Then** the system discards the inference and optionally records the rejection to improve future reasoning

---

### User Story 4 - Offline Operation with Smart Ontology Caching (Priority: P3)

A user operates in an environment with unreliable network connectivity, and the system needs to continue functioning using cached ontologies without requiring downloads.

**Why this priority**: Improves system reliability and reduces network dependency, but the core functionality works without this feature. Important for production deployments but not essential for initial MVP.

**Independent Test**: Can be tested by pre-loading ontologies, disconnecting from network, starting the system, and verifying it successfully loads cached ontologies and performs inference. Delivers value by ensuring uninterrupted operation in network-constrained environments.

**Acceptance Scenarios**:

1. **Given** an ontology has been downloaded previously, **When** the system starts and the network is unavailable, **Then** the system loads the cached version without error
2. **Given** a cached ontology exists with HTTP metadata (ETag/Last-Modified), **When** the system starts with network available, **Then** it checks if the remote ontology has been updated before re-downloading
3. **Given** a remote ontology has not changed (same ETag), **When** the system checks for updates, **Then** it uses the cached version without downloading
4. **Given** network is available and remote ontology has been updated, **When** the system detects the change, **Then** it downloads the new version and updates the cache

---

### User Story 5 - Knowledge Graph Persistence Across Sessions (Priority: P3)

A user shuts down the MCP server and later restarts it, expecting all stored memories and inferred facts to be preserved.

**Why this priority**: Essential for production use but not needed for initial testing. Can be implemented after core inference logic is validated.

**Independent Test**: Can be tested by storing memories, shutting down the server, restarting it, and verifying that all data is correctly restored. Delivers value by making the system suitable for long-term use.

**Acceptance Scenarios**:

1. **Given** a knowledge graph with stored memories, **When** the server shuts down gracefully, **Then** the graph is serialized to persistent storage (Turtle file or database)
2. **Given** a persisted knowledge graph exists, **When** the server starts up, **Then** it loads the graph and re-applies all inference rules to ensure consistency
3. **Given** the server crashes unexpectedly, **When** it restarts, **Then** it recovers from the last successful save point with minimal data loss
4. **Given** a user configures persistence format preference, **When** saving the graph, **Then** the system uses the configured format (Turtle, SQLite, or Oxigraph)

---

### Edge Cases

- What happens when an inference rule produces conflicting facts (e.g., "Alice age 25" vs "Alice age 30")?
- How does the system handle circular dependencies in ontologies or rules?
- What happens when a custom SPARQL rule file contains syntax errors?
- How does the system behave when the cache directory is corrupted or deleted?
- What happens when ontologies define contradictory relationships?
- How does the system handle extremely large knowledge graphs that exceed available memory?
- What happens when inference produces an infinite recursion scenario?
- How does the system manage concurrent access from multiple AI agents?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST load standard ontologies (FOAF, SKOS, RDFS, Schema.org Lite) at startup and apply deductive closure using OWL-RL semantics
- **FR-002**: System MUST provide an MCP tool named `add_memory` that accepts natural language input and converts it to RDF triples for storage
- **FR-003**: System MUST automatically infer implicit facts from explicit assertions using loaded ontology axioms without requiring explicit code for each inference pattern
- **FR-004**: System MUST load SPARQL CONSTRUCT rules from both a default rules directory and a user-defined custom rules directory at startup
- **FR-005**: System MUST execute all loaded SPARQL CONSTRUCT rules against the knowledge graph after ontological inference is complete
- **FR-006**: System MUST support uncertainty flags in rule-generated inferences and return verification requests instead of directly asserting uncertain facts
- **FR-007**: System MUST cache downloaded ontologies locally with HTTP metadata (ETag, Last-Modified) to avoid redundant downloads
- **FR-008**: System MUST check cached ontologies for freshness by comparing HTTP headers before re-downloading
- **FR-009**: System MUST fall back to cached ontologies when network is unavailable or remote sources are unreachable
- **FR-010**: System MUST serialize the knowledge graph to persistent storage on shutdown (Turtle format by default)
- **FR-011**: System MUST support configurable persistence backends (Turtle file, SQLite, Oxigraph)
- **FR-012**: System MUST restore the knowledge graph from persistent storage on startup and re-apply inference rules
- **FR-013**: System MUST provide MCP tools for querying the knowledge graph with support for retrieving both explicit and inferred facts
- **FR-014**: System MUST validate SPARQL rule files for syntax errors during loading and report errors without crashing
- **FR-015**: System MUST support provenance metadata for tracking the source of inferred facts (which rule produced them)
- **FR-016**: System MUST detect and prevent infinite recursion in inference rules by implementing cycle detection with a configurable depth limit (default: 10 levels)
- **FR-017**: System MUST handle conflicting facts by maintaining multiple assertions with provenance tracking, allowing users to query for conflicts
- **FR-018**: System MUST log all inference activities (rules applied, facts generated, verification requests) for debugging and auditability

### Key Entities *(include if feature involves data)*

- **Memory**: A piece of information provided in natural language that gets converted to RDF triples. Represents atomic facts or relationships.
- **Triple**: The fundamental RDF data structure (subject-predicate-object) that stores both explicit assertions and inferred facts.
- **Ontology**: A formal vocabulary definition (e.g., FOAF, SKOS) that provides class hierarchies and property semantics for automatic inference.
- **Inference Rule**: A SPARQL CONSTRUCT query that derives new facts from existing patterns in the knowledge graph.
- **Verification Request**: A structured response containing an uncertain inference that requires user confirmation before being asserted as fact.
- **Provenance Record**: Metadata tracking the origin of a fact (user-provided, ontology-inferred, or rule-generated) and timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: AI agents can store natural language statements and retrieve both explicit and automatically inferred facts in a single query within 500ms for knowledge graphs up to 10,000 triples
- **SC-002**: System correctly infers at least 95% of logically derivable facts from standard FOAF and RDFS ontology axioms in benchmark test scenarios
- **SC-003**: Custom SPARQL rules can be added by users without server restart, with validation feedback provided within 1 second
- **SC-004**: System operates without network access for standard inference tasks using cached ontologies, with zero degradation in inference quality
- **SC-005**: Knowledge graph persists across server restarts with 100% data integrity and completes startup inference within 5 seconds for graphs up to 10,000 triples
- **SC-006**: System prevents infinite inference loops in 100% of test cases through cycle detection and depth limiting
- **SC-007**: Verification requests for uncertain inferences are generated and delivered to AI agents within 200ms of rule execution
- **SC-008**: System reduces the amount of explicit data storage required by AI agents by at least 30% through automatic inference (compared to storing all facts explicitly)
