# Realistic Dialog Scenario: Dual-Level Inference with User Verification

## Overview

This document describes a realistic interaction scenario between a user, an LLM, and the SmartMemory MCP server, demonstrating both levels of inference and the verification workflow.

## The Scenario

### Participants
- **User**: Alice (providing information)
- **LLM**: AI assistant using SmartMemory 
- **SmartMemory**: Semantic memory MCP server with dual-level inference

### Dialog Flow

#### 1. Initial Information

**User**: "Alice works at TechCorp and knows Bob."

**LLM**: *Calls `add_memory` tool*

**SmartMemory Response**:
```
✓ Added 6 explicit triple(s) from your input.
  - Alice works at TechCorp (schema:worksFor)
  - Alice knows Bob (foaf:knows)
  - Alice is a Person (rdf:type)
  - Bob is a Person (rdf:type)
  - TechCorp is an Organization (rdf:type)

✓ Inferred 2 additional triple(s) via OWL-RL reasoning.
  - Bob knows Alice (symmetric foaf:knows property)
  - Alice is a foaf:Agent (rdfs:subClassOf inference)

Total triples in knowledge graph: 8 (+ provenance metadata)
```

**Level 1 Inference (OWL-RL)**: Automatic
- `foaf:knows` is a symmetric property in the FOAF ontology
- System automatically infers: `Bob foaf:knows Alice`
- Confidence: 1.0 (ontological truth) → Auto-accepted

---

#### 2. Additional Context

**User**: "Bob also works at TechCorp."

**LLM**: *Calls `add_memory` again*

**SmartMemory Response**:
```
✓ Added 1 explicit triple(s) from your input.
  - Bob works at TechCorp (schema:worksFor)

✓ Inferred 0 additional triple(s) via OWL-RL reasoning.

⚠ 1 inference(s) need verification.
   Use the verify_inference tool to confirm or reject them.

Total triples in knowledge graph: 9
```

**Level 2 Inference (SPARQL)**: Requires Verification
- Custom rule detects: Both Alice and Bob work at same organization
- Rule infers: `Alice schema:colleague Bob` (confidence: 0.75)
- Confidence < 0.85 (auto-accept threshold) → Verification requested

---

#### 3. Verification Request

**SmartMemory Presents**:
```json
{
  "verification_id": "ver_abc123",
  "triple": "Alice schema:colleague Bob",
  "confidence": 0.75,
  "reasoning": "Both work at TechCorp (custom rule: potential_collaboration)",
  "status": "pending"
}
```

**LLM to User**: "I've inferred that Alice and Bob might be colleagues since they both work at TechCorp. Should I add this to your knowledge graph?"

---

#### 4. User Confirmation

**User**: "Yes, they do work together on projects. Please confirm."

**LLM**: *Calls `verify_inference` tool*

```json
{
  "triple": ":Alice schema:colleague :Bob",
  "action": "accept"
}
```

**SmartMemory Response**:
```
✓ Inference accepted and added to the knowledge graph.
  - Alice schema:colleague Bob [source: user-verified, confidence: 1.0]
```

---

#### 5. Final Query

**User**: "What do you know about Alice?"

**LLM**: *Calls `query_memory` tool*

**SmartMemory Response**:
```sparql
SELECT ?predicate ?object
WHERE {
  :Alice ?predicate ?object .
}
```

**Results**:
```
Found 4 results:

--- Result 1 ---
  predicate: schema:worksFor
  object: :TechCorp
  source: user
  
--- Result 2 ---
  predicate: foaf:knows
  object: :Bob
  source: user

--- Result 3 ---
  predicate: schema:colleague
  object: :Bob
  source: user-verified

--- Result 4 ---
  predicate: rdf:type
  object: schema:Person
  source: user
```

---

## Inference Summary

### Level 1: OWL-RL (Ontological Inference)
- **Source**: Standard ontologies (FOAF, Schema.org, RDFS)
- **Confidence**: 1.0 (ontological truth)
- **Example**: Symmetric `foaf:knows` relationship
- **Auto-accepted**: Yes

### Level 2: SPARQL Rules (Business Logic)
- **Source**: Custom SPARQL CONSTRUCT rules  
- **Confidence**: 0.5-0.95 (depends on rule)
- **Example**: Colleague inference from shared workplace
- **Auto-accepted**: Only if confidence ≥ 0.85

### Verification Workflow
1. **Trigger**: Inference with confidence < 0.85
2. **Action**: Add to `pending_verifications_graph`
3. **User Choice**: Accept or Reject via `verify_inference` tool
4. **Accepted**: Move to main graph with source="user-verified"
5. **Rejected**: Move to `rejected_verifications_graph` (learn from it)

---

## Provenance Tracking

Every triple has metadata:

```turtle
:Alice schema:colleague :Bob .

# Provenance metadata (RDF reification)
_:stmt1 a rdf:Statement ;
        rdf:subject :Alice ;
        rdf:predicate schema:colleague ;
        rdf:object :Bob ;
        sem:source "user-verified" ;
        sem:sourceRule <file:///rules/defaults/potential_collaboration.rq> ;
        sem:confidence 1.0 ;
        sem:timestamp "2025-11-25T13:45:00Z" ;
        sem:uncertain false .
```

---

## Why This Matters

### For Users
- **Transparency**: See what was inferred vs. stated
- **Control**: Approve uncertain inferences
- **Learning**: System remembers what you confirmed/rejected

### For LLMs
- **Rich Context**: Access both explicit and inferred knowledge
- **Confidence Aware**: Know which facts are certain
- **Explanations**: Trace back inference provenance

### For Developers
- **Extensible**: Add custom SPARQL rules for domain logic
- **Compliant**: W3C standards (RDF, RDFS, OWL, SPARQL)
- **Auditable**: Full provenance trail

---

## Test Implementation

See [`tests/integration/test_realistic_dialog.py`](file:///home/momo/Antigravity/SmartMemory/tests/integration/test_realistic_dialog.py) for the full automated test that simulates this scenario.

Key assertions:
- ✅ OWL-RL symmetric inference occurs
- ✅ SPARQL rule generates pending verification
- ✅ User acceptance moves triple to main graph
- ✅ Provenance metadata is correct
- ✅ Graph statistics reflect all changes
