# Research & Technical Decisions: Semantic Memory MCP Server

**Feature**: 003-semantic-memory-server
**Date**: 2025-11-22
**Status**: Complete

## Overview

This document captures technical research, architectural decisions, and rationale for the Semantic Memory MCP Server implementation.

## 1. RDF Library Selection

**Decision**: Use `rdflib` as the primary RDF manipulation library

**Rationale**:
- **Mature ecosystem**: RDFLib is the de facto standard for RDF in Python with 15+ years of development
- **W3C compliance**: Full support for RDF 1.1, Turtle, N-Triples, RDF/XML, JSON-LD serialization formats
- **SPARQL support**: Built-in SPARQL 1.1 query engine for both SELECT and CONSTRUCT queries
- **owlrl integration**: Seamless integration with owlrl library for OWL-RL reasoning
- **Active maintenance**: Regular updates and strong community support

**Alternatives Considered**:
- **Oxigraph (Rust-based)**: Excellent performance but requires Python bindings and adds complexity for pure Python deployment
- **Apache Jena via Py4J**: Java interop overhead and deployment complexity
- **Custom implementation**: Massive scope increase, reinventing well-tested standards

**Trade-offs**:
- Performance: RDFLib is slower than Oxigraph for very large graphs (>100k triples), but acceptable for our 10k triple target
- Memory: In-memory graphs can be large, but persistence options (SQLite backend) mitigate this

## 2. Inference Strategy: OWL-RL Reasoner

**Decision**: Use `owlrl` library for Level 1 (ontological) inference

**Rationale**:
- **OWL-RL profile**: Subset of OWL 2 designed for rule-based reasoning - perfect balance of expressivity and computational tractability
- **Deductive closure**: Automatically materializes all inferred triples without manual rule coding
- **Standard ontologies**: Works seamlessly with FOAF, RDFS, SKOS, Schema.org
- **Deterministic**: Same input always produces same inferences (no heuristics)

**Implementation Notes**:
- Apply `owlrl.DeductiveClosure` after loading ontologies and before custom SPARQL rules
- Configuration: Use `OWLRL_Semantics` for OWL-RL or `RDFS_Semantics` for simpler reasoning
- Performance: Cache inferred triples to avoid re-computation on every query

**Alternatives Considered**:
- **Full OWL 2 reasoner (HermiT, Pellet)**: Undecidable complexity, overkill for our use case
- **Custom rule engine**: Would duplicate owlrl functionality, maintenance burden
- **SHACL validation**: Complementary but not a replacement for inference

## 3. SPARQL Rule Engine (Level 2)

**Decision**: Execute SPARQL CONSTRUCT queries from `.rq` files as custom inference rules

**Rationale**:
- **Declarative**: Rules are pure SPARQL, no imperative code needed
- **Standard**: SPARQL 1.1 is a W3C standard - rules are portable across systems
- **User-friendly**: Users can write rules without Python knowledge
- **Extensible**: New rules added by dropping files in `user_rules/` directory

**Implementation Strategy**:
1. Load all `.rq` files from `src/rules/defaults/` and `user_rules/` on startup
2. Parse and validate each query using rdflib's `prepareQuery()`
3. Execute rules in sequence after OWL-RL closure completes
4. Repeat rule execution until no new triples are generated (fixed-point iteration)
5. Implement cycle detection: track rule execution count, error if exceeds threshold (default: 10 iterations)

**Rule Execution Order**:
- Execute default rules before custom rules (predictable behavior)
- Within each set, execute alphabetically by filename (deterministic)
- Future enhancement: Support rule priority metadata in comments

**Alternatives Considered**:
- **SWRL (Semantic Web Rule Language)**: More expressive but less tool support, steeper learning curve
- **Python-embedded rules**: Flexible but breaks declarative model, harder for users
- **Forward-chaining with Rete algorithm**: Complex implementation, optimized for different use case

## 4. Natural Language to RDF Conversion

**Decision**: Hybrid approach using pattern matching + LLM-assisted extraction

**Rationale**:
- **Pattern matching**: Fast, deterministic for common patterns ("X is a Y", "X works at Y")
- **LLM fallback**: Handle complex or ambiguous statements
- **Provenance**: Always mark source as "user-provided" to distinguish from inferred

**Implementation Approach**:
```python
# Priority order:
1. Check for simple patterns (regex-based)
   - "X is a Y" → (X, rdf:type, Y)
   - "X works at Y" → (X, schema:worksFor, Y)

2. If no match, use LLM to extract (subject, predicate, object)
   - Provide ontology context (FOAF, Schema.org vocabularies)
   - Request structured output with namespace prefixes

3. Validate extracted triples
   - Check predicates exist in loaded ontologies
   - Warn on custom predicates (constitution: "Ontology First")
```

**Alternatives Considered**:
- **Pure LLM**: High quality but slow, API costs, non-deterministic
- **Pure pattern matching**: Fast but brittle, many false negatives
- **Stanford CoreNLP**: Heavy dependency, overkill for our domain

## 5. Ontology Caching Strategy

**Decision**: HTTP caching with ETag/Last-Modified support

**Rationale**:
- **Offline operation**: Essential for FR-009 (fallback to cache when network unavailable)
- **Freshness**: Check remote version without re-downloading entire ontology
- **Standards compliance**: Use standard HTTP cache headers

**Implementation Details**:
```python
Cache structure:
.cache/ontologies/
├── foaf.rdf            # Ontology file
├── foaf.meta.json      # {"etag": "...", "last-modified": "...", "url": "..."}
├── skos.rdf
├── skos.meta.json
└── ...

Download logic:
1. Check if cached file exists
2. If exists, read metadata and send conditional GET with If-None-Match/If-Modified-Since
3. If 304 Not Modified → use cache
4. If 200 OK → download, update cache, save metadata
5. If network error → use cache (log warning)
```

**Cache Expiry**: Check for updates on server startup (not every query)

**Alternatives Considered**:
- **No caching**: Violates FR-009, requires network for every startup
- **Time-based expiry**: Less efficient than ETag/Last-Modified
- **Manual updates**: User friction, easy to forget

## 6. Persistence Backend Options

**Decision**: Support three backends with Turtle as default

### 6.1 Turtle (.ttl) Files (Default)

**Pros**:
- Human-readable
- Version control friendly (text-based diff)
- Standard RDF serialization
- Zero setup (no external database)

**Cons**:
- Slower for large graphs (full file rewrite on save)
- No transactions

**Use Case**: Development, small deployments (<10k triples)

### 6.2 SQLite Backend

**Pros**:
- ACID transactions
- Fast queries with indexes
- Single-file portability
- No server setup

**Cons**:
- Binary format (not human-readable)
- RDFLib's SQLite backend has performance quirks

**Use Case**: Production deployments with frequent writes

### 6.3 Oxigraph (Optional)

**Pros**:
- Highest performance (Rust-based)
- Optimized for RDF workloads
- SPARQL query performance

**Cons**:
- Additional dependency (requires Rust toolchain or wheels)
- Less mature Python bindings

**Use Case**: Large-scale deployments (>100k triples)

**Configuration**: `PERSISTENCE_BACKEND` environment variable or config.yaml

## 7. Uncertainty Handling Mechanism

**Decision**: Annotation-based uncertainty with verification workflow

**Rationale**:
- **Constitution compliance**: "Trust but Verify" principle
- **Data quality**: Prevents pollution of knowledge graph with speculative inferences

**Implementation**:
```python
# In SPARQL rules, mark uncertain inferences with custom property:
PREFIX sem: <http://example.org/semantic-memory/>

CONSTRUCT {
    ?person1 foaf:knows ?person2 .
    ?inference sem:uncertain "true" .
    ?inference sem:confidence "0.6" .
}
WHERE {
    # Heuristic: people working at same company might know each other
    ?person1 schema:worksFor ?org .
    ?person2 schema:worksFor ?org .
    FILTER(?person1 != ?person2)
}

# Detection logic in rule_engine.py:
1. After CONSTRUCT execution, check for sem:uncertain annotations
2. If found, do NOT insert into main graph
3. Store in temporary "pending_verifications" graph
4. Return verification request via MCP tool response
5. User confirms/rejects via verify_inference tool
6. If confirmed: remove uncertainty annotation, insert into main graph with provenance
```

**Alternatives Considered**:
- **Probabilistic database**: Complex, out of scope for MVP
- **Always infer**: Violates constitution, reduces quality
- **Never use uncertain rules**: Limits expressiveness

## 8. MCP Protocol Integration

**Decision**: Use official `mcp` Python SDK

**Rationale**:
- **Official implementation**: Maintained by Anthropic
- **Type safety**: Built with Pydantic for strict typing
- **Async support**: Non-blocking tool execution
- **Documentation**: Official examples and patterns

**Tool Design**:
```python
Tools to expose:
1. add_memory(text: str) -> dict
   - Input: Natural language statement
   - Output: {triples_added, inferred_count, conflicts}

2. query_memory(sparql: str) -> dict
   - Input: SPARQL SELECT query
   - Output: {results: [...], count: N}

3. search_entity(entity_uri: str) -> dict
   - Input: Entity URI or label
   - Output: {explicit_facts, inferred_facts, provenance}

4. verify_inference(inference_id: str, accept: bool) -> dict
   - Input: ID from verification request, user decision
   - Output: {status: "confirmed"|"rejected"}

5. load_custom_rule(rule_file: str) -> dict
   - Input: Path to .rq file (optional, auto-loads from user_rules/)
   - Output: {status, validation_errors}
```

**Alternatives Considered**:
- **REST API**: More complex deployment, not needed for MCP use case
- **gRPC**: Overkill for this scope
- **Custom protocol**: Defeats purpose of using MCP standard

## 9. Conflict Detection & Resolution

**Decision**: Detect conflicts but preserve both assertions with provenance

**Rationale**:
- **Open World Assumption**: RDF assumes incomplete information, conflicts may be contextual
- **Auditability**: Users should see competing claims
- **Non-destructive**: Don't auto-delete user data

**Implementation**:
```python
Conflict patterns:
1. Contradictory literals:
   - (:alice :age "25") vs (:alice :age "30")
   - Detection: same subject+predicate, different literal values

2. Disjoint classes:
   - (:bob rdf:type :Person) vs (:bob rdf:type :Organization)
   - Detection: check ontology for owl:disjointWith

3. Functional property violations:
   - (:alice foaf:name "Alice") vs (:alice foaf:name "Alicia")
   - Detection: check ontology for owl:FunctionalProperty

Response:
- Mark conflicting triples with sem:conflict property
- Link to provenance (which rule/user input generated each)
- Expose via query_conflicts() MCP tool
- Future: SHACL validation for stricter constraints
```

## 10. Testing Strategy

**Decision**: Three-tier testing approach

### Unit Tests
- **Scope**: Individual components in isolation
- **Tools**: pytest with mocking
- **Coverage target**: >80% for core logic
- **Examples**:
  - `test_ontology_loader`: Cache hit/miss, network failure fallback
  - `test_reasoner`: OWL-RL inference correctness
  - `test_triple_extractor`: NL parsing accuracy

### Integration Tests
- **Scope**: Component interactions
- **Examples**:
  - End-to-end inference pipeline (NL input → triples → OWL-RL → SPARQL rules → query)
  - MCP tool interactions (add_memory → query_memory)
  - Persistence roundtrip (save → load → verify integrity)

### Contract Tests
- **Scope**: MCP tool interfaces
- **Verify**: Input schemas, output formats, error handling
- **Critical**: Ensures backward compatibility for clients

**Test Data**: Use real ontologies (FOAF, RDFS) cached in `tests/fixtures/ontologies/`

## 11. Default SPARQL Rules

Five default rules to include in `src/rules/defaults/`:

### 11.1 spatial_transitivity.rq
**Purpose**: Infer location containment chains
```sparql
# If A is in B, and B is in C, then A is in C
PREFIX schema: <https://schema.org/>
CONSTRUCT {
    ?inner schema:containedInPlace ?outer .
}
WHERE {
    ?inner schema:containedInPlace ?middle .
    ?middle schema:containedInPlace ?outer .
}
```

### 11.2 social_symmetry.rq
**Purpose**: Make foaf:knows symmetric (if A knows B, then B knows A)
```sparql
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
CONSTRUCT {
    ?person2 foaf:knows ?person1 .
}
WHERE {
    ?person1 foaf:knows ?person2 .
    FILTER NOT EXISTS { ?person2 foaf:knows ?person1 }
}
```

### 11.3 coworkers_inference.rq
**Purpose**: Infer colleague relationships from shared workplace
```sparql
PREFIX schema: <https://schema.org/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
CONSTRUCT {
    ?person1 schema:colleague ?person2 .
}
WHERE {
    ?person1 schema:worksFor ?org .
    ?person2 schema:worksFor ?org .
    FILTER(?person1 != ?person2)
    FILTER NOT EXISTS { ?person1 schema:colleague ?person2 }
}
```

### 11.4 interest_discovery.rq
**Purpose**: Infer user interests from object interactions
```sparql
PREFIX schema: <https://schema.org/>
CONSTRUCT {
    ?person schema:interestOf ?topic .
}
WHERE {
    {
        ?person schema:creator ?thing .
        ?thing schema:about ?topic .
    } UNION {
        ?person schema:attendee ?event .
        ?event schema:about ?topic .
    }
    FILTER NOT EXISTS { ?person schema:interestOf ?topic }
}
```

### 11.5 event_location_inheritance.rq
**Purpose**: Inherit location from parent event
```sparql
PREFIX schema: <https://schema.org/>
CONSTRUCT {
    ?subEvent schema:location ?location .
}
WHERE {
    ?subEvent schema:superEvent ?parentEvent .
    ?parentEvent schema:location ?location .
    FILTER NOT EXISTS { ?subEvent schema:location ?existingLocation }
}
```

## 12. Performance Optimization Notes

### Inference Caching
- Cache OWL-RL closure results until graph changes
- Invalidate cache on new triples added
- Avoid re-running inference on every query

### SPARQL Optimization
- Use `FILTER NOT EXISTS` to prevent duplicate inferences
- Index frequently queried predicates (if using SQLite backend)
- Limit rule iterations (cycle detection doubles as performance safeguard)

### Memory Management
- For large graphs, consider Oxigraph backend
- Stream query results instead of materializing all at once
- Periodic garbage collection after batch operations

## Summary

All technical decisions prioritize:
1. **Standards compliance**: W3C RDF/OWL/SPARQL adherence
2. **Constitution alignment**: Active reasoning, data quality, type safety
3. **User ergonomics**: Declarative rules, minimal configuration
4. **Production readiness**: Offline operation, persistence, conflict handling

No unresolved technical questions remain. Ready to proceed to Phase 1 (Data Model & Contracts).
