# Custom SPARQL Inference Rules

This directory contains user-defined SPARQL CONSTRUCT rules for custom inference logic.

## Rule Format

Rules must be valid SPARQL CONSTRUCT queries saved as `.rq` files. Each rule file should:

1. Include appropriate PREFIX declarations
2. Use CONSTRUCT to specify the triples to generate
3. Use WHERE to specify the pattern matching conditions
4. Include `FILTER NOT EXISTS` to prevent duplicate inferences

## Example Rule

**File: `mentor_relationship.rq`**

```sparql
# Infers mentorship from teaching relationship
PREFIX schema: <https://schema.org/>

CONSTRUCT {
    ?teacher schema:mentor ?student .
}
WHERE {
    ?course schema:instructor ?teacher .
    ?course schema:attendee ?student .
    FILTER NOT EXISTS { ?teacher schema:mentor ?student }
}
```

## Loading Rules

### Via MCP Tool

Use the `load_custom_rule` tool to load rules at runtime:

```json
{
  "tool": "load_custom_rule",
  "rule_name": "mentor_relationship",
  "sparql_construct": "...",
  "confidence": 0.75
}
```

### File-Based Loading

Place `.rq` files in this directory. The server will automatically load them on startup if configured to do so.

## Confidence Scores

Each rule has a confidence score (0.0 - 1.0):

- **≥ 0.80**: Inferences are automatically accepted
- **< 0.80**: System requests user verification before accepting

The default confidence for custom rules is 0.75 (requires verification).

## Best Practices

### 1. Always Use FILTER NOT EXISTS

Prevent duplicate inferences by checking if the triple already exists:

```sparql
FILTER NOT EXISTS { ?subject ?predicate ?object }
```

### 2. Be Specific with Patterns

Use specific property paths to avoid overly broad matches:

```sparql
# Good: Specific pattern
?person schema:worksFor ?org .
?org a schema:Organization .

# Avoid: Too broad
?person ?anyPredicate ?anything .
```

### 3. Test Rules Incrementally

Start with simple patterns and add complexity:

```sparql
# Step 1: Basic pattern
?person schema:creator ?article .

# Step 2: Add type constraint
?article a schema:Article .

# Step 3: Add inference
?article schema:about ?topic .
```

### 4. Document Your Rules

Use comments to explain the inference logic:

```sparql
# This rule infers that people who co-author articles together are collaborators
# Confidence: 0.80 (automatic acceptance)
# Example: Alice and Bob co-authored a paper → Alice collaborates with Bob
```

## Common Patterns

### Transitive Relationships

```sparql
PREFIX ex: <http://example.org/>

CONSTRUCT {
    ?a ex:connectedTo ?c .
}
WHERE {
    ?a ex:connectedTo ?b .
    ?b ex:connectedTo ?c .
    FILTER(?a != ?c)
    FILTER NOT EXISTS { ?a ex:connectedTo ?c }
}
```

### Symmetric Relationships

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

### Property Inheritance

```sparql
PREFIX schema: <https://schema.org/>

CONSTRUCT {
    ?child schema:location ?location .
}
WHERE {
    ?child schema:partOf ?parent .
    ?parent schema:location ?location .
    FILTER NOT EXISTS { ?child schema:location ?existingLocation }
}
```

### Aggregation-Based Inference

```sparql
PREFIX schema: <https://schema.org/>

CONSTRUCT {
    ?person schema:expertise ?topic .
}
WHERE {
    {
        SELECT ?person ?topic (COUNT(?article) AS ?count)
        WHERE {
            ?person schema:creator ?article .
            ?article schema:about ?topic .
        }
        GROUP BY ?person ?topic
        HAVING (COUNT(?article) >= 3)
    }
    FILTER NOT EXISTS { ?person schema:expertise ?topic }
}
```

## Debugging Rules

### Check Rule Syntax

Use the `query_memory` tool to test the WHERE clause:

```sparql
SELECT ?teacher ?student
WHERE {
    ?course schema:instructor ?teacher .
    ?course schema:attendee ?student .
}
```

### View Inferred Triples

Query for triples with specific provenance:

```sparql
SELECT ?s ?p ?o ?rule
WHERE {
    ?s ?p ?o .
    ?stmt a rdf:Statement ;
          rdf:subject ?s ;
          rdf:predicate ?p ;
          rdf:object ?o ;
          sem:source "sparql-rule" ;
          sem:sourceRule ?rule .
}
```

## Need Help?

- Check the default rules in `src/rules/defaults/` for examples
- See `specs/003-semantic-memory-server/research.md` for design decisions
- Refer to the SPARQL 1.1 specification: https://www.w3.org/TR/sparql11-query/
