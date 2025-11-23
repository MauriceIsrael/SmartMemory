# Feature Specification: Semantic Memory MCP Server

**Feature Branch**: `001-semantic-memory-mcp`
**Created**: 2025-11-22
**Status**: Draft
**Input**: User description: "I want to build an MCP (Model Context Protocol) server called 'Semantic Memory'. Unlike the default 'memory' server which is passive, this one uses a knowledge graph (RDF). Key features: Semantic Ingestion: When the user gives information (e.g. 'I like SciFi'), the server converts it into an RDF triple (e.g. :User :likes :SciFi). Light Inference Engine: On insertion, the system applies rules (e.g. transitivity, subclasses). If :User :likes :SciFi and :SciFi :hasAuthor :Asimov, the system can infer :User :mightLike :Asimov. Elicitation Loop (The Killer Feature): If an inference has a medium degree of certainty, the server does not add it silently. It returns a specific `request_verification` tool to the client LLM, forcing the latter to ask the user: 'Since you like Sci-Fi, do you also appreciate Asimov?'. Persistence: Save in Turtle (.ttl) or SQLite format with graph structure. The objective is to reduce the necessary context window by deducing implicit facts rather than repeating them."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Semantic Ingestion (Priority: P1)

As a user, I want the system to understand my statements and represent them as structured knowledge, so that the system can build a model of my preferences and knowledge.

**Why this priority**: This is the core functionality for capturing information.

**Independent Test**: The system can be given a set of statements and we can verify that the correct triples are created in the knowledge graph.

**Acceptance Scenarios**:

1. **Given** an empty knowledge graph, **When** the user states "I like Science Fiction", **Then** the system creates the triple `(:User, :likes, :ScienceFiction)`.
2. **Given** a knowledge graph, **When** the user states "Asimov wrote Foundation", **Then** the system creates the triple `(:Asimov, :wrote, :Foundation)`.

---

### User Story 2 - Light Inference Engine (Priority: P2)

As a user, I want the system to automatically connect pieces of information, so that it can uncover relationships I haven't explicitly stated.

**Why this priority**: This makes the memory "smart" and reduces the need for me to state everything explicitly.

**Independent Test**: Given a knowledge graph and a new fact, we can verify that the expected inferred facts are generated.

**Acceptance Scenarios**:

1. **Given** the triple `(:User, :likes, :ScienceFiction)` and the rule `{ ?x :likes ?y . ?y :hasAuthor ?z => ?x :mightLike ?z . }`, **When** the triple `(:ScienceFiction, :hasAuthor, :Asimov)` is added, **Then** the system infers `(:User, :mightLike, :Asimov)`.

---

### User Story 3 - Elicitation Loop (Priority: P1)

As a user, I want the system to ask for confirmation when it makes an uncertain inference, so that the knowledge graph remains accurate and reflects my actual preferences.

**Why this priority**: This is the "killer feature" that ensures the quality of the inferred knowledge and provides a natural interaction loop.

**Independent Test**: Given an inference with a medium certainty score, we can verify that the system issues a `request_verification` tool call.

**Acceptance Scenarios**:

1. **Given** an inference `(:User, :mightLike, :Asimov)` with a certainty score of 0.7, **When** the inference is generated, **Then** the system returns a `request_verification` tool call to the client with the content of the inference.
2. **Given** an inference with a certainty score of 0.95, **When** the inference is generated, **Then** the system adds it to the graph without asking for verification.

---

### User Story 4 - Persistence (Priority: P2)

As a user, I want the system to save its knowledge, so that my information is not lost between sessions.

**Why this priority**: This is essential for the system to have a long-term memory.

**Independent Test**: We can save the knowledge graph, shut down the server, restart it, and verify that the knowledge is still present.

**Acceptance Scenarios**:

1. **Given** a knowledge graph with 10 triples, **When** the system is shut down and restarted, **Then** the knowledge graph still contains 10 triples.

---

### Edge Cases

- What happens when the user input is ambiguous and cannot be converted into a single triple?
- How does the system handle contradictory information provided by the user?
- What is the behavior when the persistence mechanism fails (e.g., disk full)?

### Assumptions

- A default ontology (e.g., Schema.org, FOAF) will be used as a base for predicates.
- Inference certainty scores are represented as a float between 0.0 and 1.0.


## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide an MCP endpoint for the semantic memory.
- **FR-002**: The system MUST convert natural language user input into RDF triples.
- **FR-003**: The system MUST apply inference rules on data insertion to deduce new facts.
- **FR-004**: The system MUST return a `request_verification` tool call to the client LLM when an inference's certainty is below a configurable threshold.
- **FR-005**: The system MUST persist the knowledge graph to a file. The default persistence format is Turtle (.ttl).

### Key Entities

- **Triple**: A subject-predicate-object statement representing a piece of knowledge.
- **Knowledge Graph**: A collection of triples that represents the system's memory.
- **Inference Rule**: A logical rule that allows the system to deduce new triples from existing ones.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The system correctly converts 95% of test user statements into valid RDF triples.
- **SC-002**: The inference engine correctly deduces all expected new facts for a given set of test cases.
- **SC-003**: The system triggers the elicitation loop for 100% of inferences with a certainty score between 0.5 and 0.9.
- **SC-004**: The system can successfully save and reload a knowledge graph of at least 1 million triples in under 5 seconds.