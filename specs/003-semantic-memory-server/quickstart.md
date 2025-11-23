# Quickstart Guide: Semantic Memory MCP Server

**Feature**: 003-semantic-memory-server
**Date**: 2025-11-22
**Audience**: Developers testing the implementation

## Overview

This guide provides concrete test scenarios to validate each user story in the Semantic Memory MCP Server specification. Each scenario can be tested independently and represents a complete, valuable increment of functionality.

## Prerequisites

- Python 3.11+ installed
- MCP client (Claude Desktop, or mcp CLI tool)
- Internet connection for initial ontology download (optional after first run)

## Installation

```bash
# Clone and navigate to project root
cd /path/to/SmartMemory

# Install dependencies
pip install -e .

# Start the MCP server
python -m semantic_memory.server
```

## Test Scenarios by User Story

### User Story 1: Basic Memory Storage and Automatic Inference (P1)

**Goal**: Verify that facts are stored as RDF triples and automatic inference works.

#### Scenario 1.1: Store Simple Fact

```python
# Using MCP client
tool: add_memory
input:
  text: "Alice is a Person"

expected_output:
  status: "success"
  explicit_triples:
    - subject: "http://example.org/Alice"
      predicate: "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
      object: "http://xmlns.com/foaf/0.1/Person"
  inferred_triples:
    - subject: "http://example.org/Alice"
      predicate: "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
      object: "http://xmlns.com/foaf/0.1/Agent"
      source: "owlrl"
      # OWL-RL inferred because foaf:Person subClassOf foaf:Agent

✓ Success criteria: inferred_triples contains at least one triple from OWL-RL
```

#### Scenario 1.2: Query Both Explicit and Inferred Facts

```python
# After adding Alice as Person
tool: search_entity
input:
  entity_label: "Alice"
  include_incoming: true
  max_depth: 0

expected_output:
  status: "success"
  entity_uri: "http://example.org/Alice"
  explicit_facts:
    - predicate: "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
      object: "http://xmlns.com/foaf/0.1/Person"
  inferred_facts:
    - predicate: "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
      object: "http://xmlns.com/foaf/0.1/Agent"
      source: "owlrl"
  types:
    - "http://xmlns.com/foaf/0.1/Person"
    - "http://xmlns.com/foaf/0.1/Agent"

✓ Success criteria: Both explicit and inferred types returned in single query
✓ Provenance distinguishes user-provided vs system-generated
```

#### Scenario 1.3: Natural Language Conversion

```python
tool: add_memory
input:
  text: "Bob works at TechCorp"

expected_output:
  status: "success"
  explicit_triples:
    - subject: "http://example.org/Bob"
      predicate: "https://schema.org/worksFor"
      object: "http://example.org/TechCorp"
  inferred_triples:
    # Depends on loaded ontologies

✓ Success criteria: Natural language converted to proper Schema.org predicate
✓ Subject and object URIs generated correctly
```

#### Scenario 1.4: Performance Check

```python
# Add 100 simple facts
for i in range(100):
    tool: add_memory
    input:
      text: f"Person{i} is a Person"

# Then query graph stats
tool: get_graph_stats

expected_output:
  triple_counts:
    total: >= 200  # At least 100 explicit + 100 inferred
    explicit: 100
    inferred: >= 100

# Measure end-to-end time
✓ Success criteria: Total time < 5 seconds for 100 facts
✓ Query response < 500ms
```

---

### User Story 2: Custom Business Logic Rules (P2)

**Goal**: Verify SPARQL CONSTRUCT rules execute correctly and generate expected inferences.

#### Scenario 2.1: Load and Validate Default Rules

```python
tool: list_rules
input:
  include_inactive: false

expected_output:
  status: "success"
  rules:
    - id: "spatial_transitivity"
      source: "default"
      is_active: true
    - id: "social_symmetry"
      source: "default"
      is_active: true
    - id: "coworkers_inference"
      source: "default"
      is_active: true
    - id: "interest_discovery"
      source: "default"
      is_active: true
    - id: "event_location_inheritance"
      source: "default"
      is_active: true
  total_count: 5
  active_count: 5

✓ Success criteria: All 5 default rules loaded successfully
✓ No validation errors
```

#### Scenario 2.2: Test Spatial Transitivity Rule

```python
# Add location facts
tool: add_memory
input:
  text: "Alice lives in Paris"

tool: add_memory
input:
  text: "Paris is in France"

# Query for inferred location
tool: search_entity
input:
  entity_label: "Alice"

expected_output:
  inferred_facts:
    - predicate: "https://schema.org/containedInPlace"
      object: "http://example.org/France"
      source: "sparql-rule"
      source_rule: "spatial_transitivity.rq"

✓ Success criteria: Transitive inference "Alice in France" generated
✓ Provenance points to spatial_transitivity.rq
```

#### Scenario 2.3: Test Social Symmetry Rule

```python
tool: add_memory
input:
  text: "Alice knows Bob"

# Symmetry should be inferred
tool: query_memory
input:
  sparql: |
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?s ?o WHERE {
      ?s foaf:knows ?o .
    }

expected_output:
  results:
    - s: "http://example.org/Alice"
      o: "http://example.org/Bob"
    - s: "http://example.org/Bob"
      o: "http://example.org/Alice"  # Inferred by social_symmetry.rq
  count: 2

✓ Success criteria: foaf:knows is symmetric (Bob knows Alice inferred)
```

#### Scenario 2.4: Test Coworkers Inference Rule

```python
tool: add_memory
input:
  text: "Alice works at TechCorp"

tool: add_memory
input:
  text: "Bob works at TechCorp"

# Colleague relationship should be inferred
tool: search_entity
input:
  entity_label: "Alice"

expected_output:
  inferred_facts:
    - predicate: "https://schema.org/colleague"
      object: "http://example.org/Bob"
      source: "sparql-rule"
      source_rule: "coworkers_inference.rq"

✓ Success criteria: Colleague relationship inferred from shared employer
```

#### Scenario 2.5: Load Custom Rule

```python
# Create custom rule file in user_rules/
# File: user_rules/team_membership.rq
"""
# Infers team membership from project participation
PREFIX schema: <https://schema.org/>
CONSTRUCT {
    ?person1 schema:colleague ?person2 .
}
WHERE {
    ?person1 schema:memberOf ?team .
    ?person2 schema:memberOf ?team .
    FILTER(?person1 != ?person2)
    FILTER NOT EXISTS { ?person1 schema:colleague ?person2 }
}
"""

tool: load_custom_rule
input:
  rule_filename: "team_membership.rq"

expected_output:
  status: "loaded"
  rule_id: "team_membership"
  description: "Infers team membership from project participation"
  validation_errors: []

# Verify it's listed
tool: list_rules

expected_output:
  rules:
    - id: "team_membership"
      source: "custom"
      is_active: true

✓ Success criteria: Custom rule loaded and active
✓ No validation errors
```

---

### User Story 3: Uncertainty Handling and User Verification (P2)

**Goal**: Verify uncertain inferences trigger verification requests instead of direct insertion.

#### Scenario 3.1: Generate Uncertain Inference

```python
# Create a rule that produces uncertain inference
# File: user_rules/possible_acquaintance.rq
"""
# UNCERTAIN: Infers possible acquaintance from shared interests
PREFIX schema: <https://schema.org/>
PREFIX sem: <http://example.org/semantic-memory/>
CONSTRUCT {
    ?person1 schema:knows ?person2 .
    _:inference sem:uncertain "true" .
    _:inference sem:confidence "0.6" .
}
WHERE {
    ?person1 schema:interestOf ?topic .
    ?person2 schema:interestOf ?topic .
    FILTER(?person1 != ?person2)
}
"""

tool: load_custom_rule
input:
  rule_filename: "possible_acquaintance.rq"

# Add test data
tool: add_memory
input:
  text: "Alice is interested in AI"

tool: add_memory
input:
  text: "Bob is interested in AI"

# Check for verification request
expected_output:
  verification_requests:
    - id: "ver_xxx"
      triple:
        subject: "http://example.org/Alice"
        predicate: "https://schema.org/knows"
        object: "http://example.org/Bob"
      confidence: 0.6
      explanation: "Inferred from shared interest in AI"

✓ Success criteria: Uncertain inference NOT inserted into graph
✓ Verification request returned with ID
```

#### Scenario 3.2: Confirm Uncertain Inference

```python
# Get verification ID from previous scenario
verification_id = "ver_xxx"

tool: verify_inference
input:
  verification_id: verification_id
  accept: true
  feedback: "Confirmed - they collaborate on AI projects"

expected_output:
  status: "confirmed"
  triple:
    subject: "http://example.org/Alice"
    predicate: "https://schema.org/knows"
    object: "http://example.org/Bob"
  added_to_graph: true

# Verify it's now in main graph
tool: search_entity
input:
  entity_label: "Alice"

expected_output:
  inferred_facts:
    - predicate: "https://schema.org/knows"
      object: "http://example.org/Bob"
      source: "sparql-rule"

✓ Success criteria: After confirmation, triple inserted with provenance
```

#### Scenario 3.3: Reject Uncertain Inference

```python
tool: verify_inference
input:
  verification_id: "ver_yyy"
  accept: false
  feedback: "Incorrect - they don't know each other"

expected_output:
  status: "rejected"
  added_to_graph: false

# Verify it's NOT in graph
tool: search_entity
input:
  entity_label: "Alice"

expected_output:
  inferred_facts: []  # Rejected inference not present

✓ Success criteria: Rejected inference not added to graph
✓ Rejection recorded (future enhancement: learn from rejections)
```

---

### User Story 4: Offline Operation with Smart Ontology Caching (P3)

**Goal**: Verify system works without network access using cached ontologies.

#### Scenario 4.1: Initial Ontology Download

```python
# First startup with network available
# Ontologies should be downloaded and cached

tool: get_graph_stats

expected_output:
  ontologies_loaded:
    - name: "FOAF"
      namespace: "http://xmlns.com/foaf/0.1/"
      source: "network"  # Downloaded from W3C
      triple_count: > 0
    - name: "Schema.org"
      source: "network"
    - name: "RDFS"
      source: "network"
    - name: "SKOS"
      source: "network"

# Check cache directory
$ ls .cache/ontologies/
foaf.rdf
foaf.meta.json
skos.rdf
skos.meta.json
rdfs.rdf
rdfs.meta.json
schema.rdf
schema.meta.json

✓ Success criteria: All ontologies downloaded and cached
✓ Metadata files contain ETag and Last-Modified
```

#### Scenario 4.2: Offline Startup (Network Unavailable)

```python
# Disconnect network or block ontology URLs
# Restart server

tool: get_graph_stats

expected_output:
  ontologies_loaded:
    - name: "FOAF"
      source: "cached"  # Loaded from cache, not network
    - name: "Schema.org"
      source: "cached"
    - name: "RDFS"
      source: "cached"
    - name: "SKOS"
      source: "cached"

# Inference should still work
tool: add_memory
input:
  text: "Charlie is a Person"

expected_output:
  inferred_triples:
    - source: "owlrl"  # OWL-RL inference still works with cached ontologies

✓ Success criteria: Server starts successfully offline
✓ All ontologies loaded from cache
✓ Inference works identically to online mode
```

#### Scenario 4.3: Cached Ontology Freshness Check

```python
# Reconnect network
# Cached ontology unchanged on remote server

# Restart server (triggers freshness check)

# Check server logs
expected_log:
  "Checking FOAF ontology freshness..."
  "Remote ETag matches cache - using cached version"

tool: get_graph_stats

expected_output:
  ontologies_loaded:
    - name: "FOAF"
      source: "cached"  # Used cache, no re-download

✓ Success criteria: HTTP conditional GET with If-None-Match
✓ 304 Not Modified response → use cache
✓ No unnecessary download
```

---

### User Story 5: Knowledge Graph Persistence Across Sessions (P3)

**Goal**: Verify data survives server restarts with full integrity.

#### Scenario 5.1: Save and Restore Graph (Turtle Format)

```python
# Add test data
tool: add_memory
input:
  text: "David works at DataCorp"

tool: add_memory
input:
  text: "Emma is David's colleague"

# Stop server gracefully
# File should be created: knowledge_graph.ttl

$ cat knowledge_graph.ttl
# Should contain explicit and inferred triples

# Restart server

tool: search_entity
input:
  entity_label: "David"

expected_output:
  explicit_facts:
    - predicate: "https://schema.org/worksFor"
      object: "http://example.org/DataCorp"
  inferred_facts:
    # All inferences restored

✓ Success criteria: All triples restored after restart
✓ Provenance preserved
✓ Re-inference applies to restored data
```

#### Scenario 5.2: Startup Inference Performance

```python
# Load graph with 1000 triples from persistence

# Measure startup time
import time
start = time.time()
# Start server
end = time.time()

startup_time = end - start

✓ Success criteria: Startup inference < 5 seconds for 10,000 triples
✓ All inferences re-applied correctly
```

#### Scenario 5.3: Persistence Format Configuration

```python
# Configure SQLite backend
# In config.yaml or env:
PERSISTENCE_BACKEND=sqlite
PERSISTENCE_PATH=knowledge_graph.db

# Add data and restart

# Verify SQLite file created
$ ls knowledge_graph.db
knowledge_graph.db

# Verify data persisted
tool: get_graph_stats

expected_output:
  triple_counts:
    total: > 0  # Data restored from SQLite

✓ Success criteria: SQLite backend works
✓ Data integrity maintained
✓ Query performance acceptable
```

---

## Edge Case Testing

### Edge Case 1: Conflicting Facts

```python
tool: add_memory
input:
  text: "Alice is 25 years old"

tool: add_memory
input:
  text: "Alice is 30 years old"

expected_output:
  status: "partial"
  conflicts_detected:
    - type: "contradictory_literal"
      existing_triple:
        subject: "http://example.org/Alice"
        predicate: "https://schema.org/age"
        object: "25"
      new_triple:
        subject: "http://example.org/Alice"
        predicate: "https://schema.org/age"
        object: "30"

# Query conflicts
tool: get_graph_stats

expected_output:
  conflicts:
    total_count: 1
    unresolved_count: 1

✓ Success criteria: Conflicts detected and flagged
✓ Both assertions preserved with provenance
```

### Edge Case 2: SPARQL Rule Syntax Error

```python
# Create invalid rule
# File: user_rules/broken_rule.rq
"""
CONSTRUCT {
    ?s ?p ?o
}
WHERE {
    ?s ?p ?o
    # Missing closing brace
"""

tool: load_custom_rule
input:
  rule_filename: "broken_rule.rq"

expected_output:
  status: "validation_error"
  validation_errors:
    - "SPARQL syntax error: Expected } at line 5"

# Verify rule not active
tool: list_rules
input:
  include_inactive: true

expected_output:
  rules:
    - id: "broken_rule"
      is_active: false
      # Not included in inference

✓ Success criteria: Syntax error caught during validation
✓ Server continues running (no crash)
✓ Rule marked inactive
```

### Edge Case 3: Infinite Recursion Detection

```python
# Create rule that could cause infinite loop
# File: user_rules/recursive_rule.rq
"""
CONSTRUCT {
    ?s :derivedFrom ?o .
}
WHERE {
    ?s :related ?o .
    # No FILTER NOT EXISTS - generates new triples each iteration
}
"""

tool: add_memory
input:
  text: "A is related to B"

# Inference should terminate with cycle detection
expected_output:
  status: "partial"
  warnings:
    - "Inference cycle detected after 10 iterations - stopping to prevent infinite loop"

✓ Success criteria: Cycle detection triggered
✓ System remains responsive
✓ No stack overflow or hang
```

---

## Performance Benchmarks

### Benchmark 1: Large Graph Query

```python
# Load 10,000 triples
for i in range(10000):
    add_memory(f"Entity{i} is a Thing")

# Complex SPARQL query
tool: query_memory
input:
  sparql: |
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?s WHERE {
      ?s rdf:type ?type .
    }
  limit: 100

expected_output:
  execution_time_ms: < 500

✓ Success criteria: Query < 500ms for 10k triples
```

### Benchmark 2: Inference Throughput

```python
# Measure inference on batch insert
import time
start = time.time()

for i in range(100):
    add_memory(f"Person{i} works at Company{i % 10}")

end = time.time()
throughput = 100 / (end - start)

✓ Success criteria: > 20 facts/second with inference
```

---

## Summary

This quickstart provides end-to-end test scenarios covering:
- ✅ All 5 user stories (P1, P2, P3)
- ✅ Edge cases (conflicts, errors, cycles)
- ✅ Performance benchmarks

Each scenario can be run independently to validate a specific capability. Together, they form a comprehensive test suite for the Semantic Memory MCP Server.

**Next Steps**: Use these scenarios to create automated integration tests in `tests/integration/`.
