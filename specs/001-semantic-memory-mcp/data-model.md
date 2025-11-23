# Data Model: Semantic Memory MCP Server

This document defines the key data entities for the Semantic Memory MCP Server.

## Core Entities

### Triple
Represents a single piece of knowledge in the graph.

- **Fields**:
    - `subject`: The subject of the statement (string, URI).
    - `predicate`: The relationship between the subject and object (string, URI).
    - `object`: The object of the statement (string, URI, or literal).
- **Validation**:
    - Subject, predicate, and object must not be null or empty.
    - URIs should be well-formed.

### KnowledgeGraph
A collection of triples that represents the system's memory. It is composed of two distinct graphs.

- **Graphs**:
    - `explicit_graph`: Contains only the facts directly provided by the user.
    - `inferred_graph`: Contains only the facts deduced by the inference engine.
- **Validation**:
    - The explicit and inferred graphs must be kept separate to maintain data integrity.

### InferenceRule
A logical rule that allows the system to deduce new triples from existing ones.

- **Fields**:
    - `name`: A unique name for the rule.
    - `conditions`: A set of patterns to match against the knowledge graph.
    - `conclusion`: A pattern for the new triple to be created if the conditions are met.
- **Example**:
    - `name`: `likes_author`
    - `conditions`: `(?x :likes ?y) AND (?y :hasAuthor ?z)`
    - `conclusion`: `(?x :mightLike ?z)`

### VerificationRequest
A request for the user to verify an uncertain inference.

- **Fields**:
    - `id`: A unique identifier for the request.
    - `triple`: The inferred triple to be verified.
    - `certainty_score`: The certainty score of the inference (float between 0.0 and 1.0).
- **State Transitions**:
    - `pending`: The request has been sent to the user but not yet answered.
    - `confirmed`: The user has confirmed the inference.
    - `rejected`: The user has rejected the inference.
