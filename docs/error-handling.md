# Error Handling and Recovery

This document describes how the SmartMemory system handles errors and recovers from failures.

## Common Error Scenarios

### 1. Network Failures (Ontology Loading)

**Scenario**: The server cannot connect to the internet to download ontologies (FOAF, Schema.org, etc.).

**Handling**:
- The `OntologyLoader` catches `requests.ConnectionError` and `requests.Timeout`.
- It attempts to load the ontology from the local cache (`.cache/semantic-memory/`).
- If the cache is available, the system proceeds in "Offline Mode" for that ontology.
- If no cache is available, the error is logged, and the system continues without that specific ontology (graceful degradation).

**Recovery**:
- Restore network connectivity.
- Restart the server to attempt downloading ontologies again.

### 2. Persistence Failures

**Scenario**: The server fails to save the knowledge graph to disk (e.g., disk full, permission denied).

**Handling**:
- The `save()` method in `Persistence` backends catches `IOError` and `OSError`.
- The error is logged with a high severity level.
- The in-memory graph remains valid, so the server continues to function.

**Recovery**:
- Free up disk space or fix permissions.
- Call `add_memory` (even with a dummy fact) to trigger a save attempt.
- Or restart the server (graceful shutdown attempts to save).

### 3. SPARQL Query Errors

**Scenario**: A user submits a malformed SPARQL query.

**Handling**:
- The `query_memory` tool catches `pyparsing.ParseException` (from rdflib) and other exceptions.
- It returns a friendly error message to the user: "Query failed: ... Please check your SPARQL syntax."
- The server process does NOT crash.

### 4. Rule Execution Loops

**Scenario**: A set of rules creates an infinite inference loop (A -> B -> A).

**Handling**:
- The `RuleEngine` implements a `max_depth` limit (default: 10).
- It stops executing rules after reaching this limit.
- It logs a warning if the limit is reached.

### 5. Corrupted Persistence File

**Scenario**: The `knowledge_graph.ttl` file is corrupted.

**Handling**:
- On startup, `Persistence.load()` catches parsing errors.
- It logs a warning: "Failed to load persisted graph".
- The server starts with an empty graph.

**Recovery**:
- Restore the persistence file from a backup.
- Or manually fix the syntax errors in the Turtle file.

## Logging

All errors are logged to the console (stderr) and optionally to a file if configured.
Log levels:
- `ERROR`: Critical failures (persistence, startup).
- `WARNING`: Recoverable failures (network, malformed input).
- `INFO`: Normal operation events.
- `DEBUG`: Detailed execution traces.
