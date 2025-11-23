<!--
Sync Impact Report:
- Version change: 0.0.0 -> 1.0.0
- List of modified principles: Complete overhaul of principles.
- Added sections: Core Philosophy, Technical Constraints, Coding Standards, Interaction Model
- Removed sections: All previous sections replaced.
- Templates requiring updates:
    - .specify/templates/plan-template.md (⚠ pending)
    - .specify/templates/spec-template.md (⚠ pending)
    - .specify/templates/tasks-template.md (⚠ pending)
- Follow-up TODOs: None
-->
# Project Constitution: Smart Semantic Memory MCP

## 1. Core Philosophy
- **No "Flat" Data:** We do not store data as simple JSON blobs. All knowledge must be structured as triples (Subject-Predicate-Object) or quads.
- **Active, Not Passive:** The memory server is not just a database. It is an agent that infers new knowledge upon insertion.
- **Trust but Verify:** Inferences are probabilistic or logical. The system must inherently support an "Elicitation Loop" to ask the user for confirmation on ambiguous deductions.

## 2. Technical Constraints
- **Language:** Python 3.11+ (Preferred for RDFLib ecosystem) OR TypeScript (only if using N3.js/Graphy). *Decision: Python is default for this spec.*
- **Standards:** STRICT adherence to W3C standards (RDF, RDFS, OWL, SHACL).
- **Protocol:** Must implement the Model Context Protocol (MCP) strictly.

## 3. Coding Standards
- **Type Safety:** All code must be fully typed (mypy strict or TypeScript strict).
- **Ontology First:** No ad-hoc predicates. Use standard ontologies (FOAF, Schema.org, SKOS) where possible, or define a strict local ontology.
- **Immutability:** Inferred facts are distinct from stated facts.

## 4. Interaction Model
- The system acts as a "Gardener" of knowledge, constantly pruning and checking consistency, not just a "Warehouse".

## Governance
This constitution supersedes all other practices. Amendments require documentation, approval, and a migration plan. All PRs and reviews must verify compliance with this constitution.

**Version**: 1.0.0 | **Ratified**: 2025-11-22 | **Last Amended**: 2025-11-22