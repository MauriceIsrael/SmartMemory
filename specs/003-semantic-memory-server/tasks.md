# Tasks: Semantic Memory MCP Server

**Input**: Design documents from `/specs/003-semantic-memory-server/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL for this feature - not explicitly requested in specification

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- All paths relative to project root `/home/momo/Antigravity/SmartMemory/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic Python structure

- [ ] T001 Create project directory structure per plan.md (src/semantic_memory/, src/rules/defaults/, src/user_rules/, tests/)
- [ ] T002 Initialize Python project with pyproject.toml (Poetry or setuptools, Python 3.11+)
- [ ] T003 [P] Add core dependencies to pyproject.toml (rdflib, owlrl, mcp, requests, pydantic)
- [ ] T004 [P] Add dev dependencies (pytest, pytest-asyncio, mypy, black, ruff)
- [ ] T005 [P] Create .gitignore with Python/RDF patterns (.cache/, *.ttl, __pycache__, etc.)
- [ ] T006 [P] Configure mypy for strict type checking in pyproject.toml
- [ ] T007 [P] Create README.md with installation and quickstart instructions
- [ ] T008 Create src/semantic_memory/__init__.py package initializer
- [ ] T009 Create src/semantic_memory/config.py for settings (cache_dir, persistence_backend, etc.)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T010 Create custom vocabulary namespace in src/semantic_memory/vocabulary.py (sem: namespace for provenance)
- [ ] T011 Create base RDF graph wrapper in src/semantic_memory/knowledge/graph.py (ProvenanceGraph class)
- [ ] T012 [P] Create logging configuration in src/semantic_memory/logging_config.py
- [ ] T013 [P] Create cache directory structure (.cache/ontologies/) with .gitkeep
- [ ] T014 [P] Create user_rules/ directory with README explaining custom rule format
- [ ] T015 Create MCP server entry point skeleton in src/semantic_memory/server.py
- [ ] T016 Create tests/fixtures/ directory with subdirs (ontologies/, test_rules/)
- [ ] T017 [P] Download and cache test ontologies in tests/fixtures/ontologies/ (FOAF, RDFS, SKOS, Schema.org)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Memory Storage and Automatic Inference (Priority: P1) 🎯 MVP

**Goal**: Store natural language as RDF triples and automatically infer facts using OWL-RL reasoning

**Independent Test**: Add "Alice is a Person" via add_memory, verify it returns both explicit triple (Alice rdf:type Person) and inferred triple (Alice rdf:type Agent) from OWL-RL closure

### Implementation for User Story 1

- [ ] T018 [P] [US1] Create ontology cache metadata model in src/semantic_memory/inference/ontology_loader.py (OntologyCacheMetadata dataclass)
- [ ] T019 [P] [US1] Implement HTTP caching logic with ETag/Last-Modified support in src/semantic_memory/inference/ontology_loader.py (fetch_with_cache function)
- [ ] T020 [US1] Implement ontology loader in src/semantic_memory/inference/ontology_loader.py (OntologyLoader class with load_standard_ontologies method)
- [ ] T021 [US1] Implement OWL-RL reasoner wrapper in src/semantic_memory/inference/reasoner.py (Reasoner class with apply_closure method)
- [ ] T022 [P] [US1] Create NL to RDF triple extractor in src/semantic_memory/nlp/triple_extractor.py (TripleExtractor class with pattern matching)
- [ ] T023 [US1] Implement add_memory MCP tool in src/semantic_memory/tools/add_memory.py (add_memory async function)
- [ ] T024 [US1] Implement query_memory MCP tool in src/semantic_memory/tools/query_memory.py (query_memory async function with SPARQL support)
- [ ] T025 [US1] Implement search_entity MCP tool in src/semantic_memory/tools/search_entity.py (search_entity async function)
- [ ] T026 [US1] Register MCP tools in src/semantic_memory/server.py and wire up startup sequence (load ontologies → apply OWL-RL)
- [ ] T027 [US1] Add provenance tracking to graph operations in src/semantic_memory/knowledge/graph.py (add_triple_with_provenance method)
- [ ] T028 [P] [US1] Create unit test for ontology loader in tests/unit/test_ontology_loader.py
- [ ] T029 [P] [US1] Create unit test for OWL-RL reasoner in tests/unit/test_reasoner.py
- [ ] T030 [P] [US1] Create unit test for triple extractor in tests/unit/test_triple_extractor.py
- [ ] T031 [US1] Create integration test for US1 in tests/integration/test_user_story_1.py (end-to-end: add_memory → query_memory)

**Checkpoint**: At this point, User Story 1 should be fully functional - can add memories and see automatic OWL-RL inferences

---

## Phase 4: User Story 2 - Custom Business Logic Rules (Priority: P2)

**Goal**: Load and execute SPARQL CONSTRUCT rules from .rq files to generate domain-specific inferences

**Independent Test**: Create spatial_transitivity.rq rule, add "Alice in Paris" and "Paris in France", verify system infers "Alice in France"

### Default SPARQL Rules Creation

- [ ] T032 [P] [US2] Create spatial_transitivity.rq in src/rules/defaults/ (transitive containment: if A in B and B in C then A in C)
- [ ] T033 [P] [US2] Create social_symmetry.rq in src/rules/defaults/ (make foaf:knows symmetric)
- [ ] T034 [P] [US2] Create coworkers_inference.rq in src/rules/defaults/ (infer schema:colleague from shared schema:worksFor)
- [ ] T035 [P] [US2] Create interest_discovery.rq in src/rules/defaults/ (infer schema:interestOf from schema:creator/attendee patterns)
- [ ] T036 [P] [US2] Create event_location_inheritance.rq in src/rules/defaults/ (inherit location from parent event via schema:superEvent)

### Rule Engine Implementation

- [ ] T037 [US2] Create rule metadata model in src/semantic_memory/inference/rule_engine.py (InferenceRule dataclass with file_path, sparql_query, stats)
- [ ] T038 [US2] Implement rule loader in src/semantic_memory/inference/rule_engine.py (load_rules function to scan .rq files from defaults/ and user_rules/)
- [ ] T039 [US2] Implement SPARQL rule validator in src/semantic_memory/inference/rule_engine.py (validate_rule function checking CONSTRUCT syntax)
- [ ] T040 [US2] Implement rule execution engine in src/semantic_memory/inference/rule_engine.py (RuleEngine class with execute_rules method)
- [ ] T041 [US2] Add cycle detection to rule engine in src/semantic_memory/inference/rule_engine.py (fixed-point iteration with max_depth=10)
- [ ] T042 [US2] Implement list_rules MCP tool in src/semantic_memory/tools/list_rules.py (list_rules async function)
- [ ] T043 [US2] Implement load_custom_rule MCP tool in src/semantic_memory/tools/load_custom_rule.py (load_custom_rule async function)
- [ ] T044 [US2] Integrate rule engine into server startup in src/semantic_memory/server.py (after OWL-RL, execute SPARQL rules)
- [ ] T045 [US2] Update add_memory tool to trigger rule re-execution in src/semantic_memory/tools/add_memory.py
- [ ] T046 [P] [US2] Create unit test for rule loader in tests/unit/test_rule_engine.py
- [ ] T047 [P] [US2] Create unit test for cycle detection in tests/unit/test_rule_engine.py
- [ ] T048 [US2] Create integration test for US2 in tests/integration/test_user_story_2.py (load custom rule, verify inference)

**Checkpoint**: At this point, both User Story 1 AND 2 work - can use both OWL-RL and custom SPARQL rules

---

## Phase 5: User Story 3 - Uncertainty Handling and User Verification (Priority: P2)

**Goal**: Detect uncertain inferences from rules and request user verification before inserting into graph

**Independent Test**: Create rule with sem:uncertain annotation, add trigger data, verify verification request returned instead of direct insertion

### Implementation for User Story 3

- [ ] T049 [P] [US3] Create verification request model in src/semantic_memory/knowledge/verification.py (VerificationRequest dataclass)
- [ ] T050 [P] [US3] Create pending verifications graph in src/semantic_memory/knowledge/graph.py (separate graph for uncertain inferences)
- [ ] T051 [US3] Implement uncertainty detection in src/semantic_memory/inference/rule_engine.py (check for sem:uncertain annotation in CONSTRUCT results)
- [ ] T052 [US3] Update add_memory tool to return verification_requests in src/semantic_memory/tools/add_memory.py
- [ ] T053 [US3] Implement verify_inference MCP tool in src/semantic_memory/tools/verify_inference.py (accept/reject logic)
- [ ] T054 [US3] Add verification status tracking to graph in src/semantic_memory/knowledge/graph.py (pending/confirmed/rejected)
- [ ] T055 [US3] Update get_graph_stats tool to include pending_verifications count in src/semantic_memory/tools/get_graph_stats.py
- [ ] T056 [P] [US3] Create unit test for verification request handling in tests/unit/test_verification.py
- [ ] T057 [US3] Create integration test for US3 in tests/integration/test_user_story_3.py (uncertain inference → verify → confirm/reject)

**Checkpoint**: All P2 user stories (US1, US2, US3) now functional independently

---

## Phase 6: User Story 4 - Offline Operation with Smart Ontology Caching (Priority: P3)

**Goal**: Support network-unavailable scenarios by falling back to cached ontologies with freshness checks

**Independent Test**: Pre-load ontologies, disconnect network, start server, verify it loads from cache and inference works

### Implementation for User Story 4

- [ ] T058 [P] [US4] Add network error handling to ontology loader in src/semantic_memory/inference/ontology_loader.py (catch ConnectionError, use cache)
- [ ] T059 [US4] Implement conditional GET with If-None-Match/If-Modified-Since in src/semantic_memory/inference/ontology_loader.py
- [ ] T060 [US4] Add cache metadata persistence in src/semantic_memory/inference/ontology_loader.py (save/load .meta.json files)
- [ ] T061 [US4] Update server startup to check ontology freshness in src/semantic_memory/server.py (call check_freshness before loading)
- [ ] T062 [US4] Add offline mode flag to config in src/semantic_memory/config.py (FORCE_OFFLINE for testing)
- [ ] T063 [P] [US4] Create unit test for cache freshness check in tests/unit/test_ontology_loader.py
- [ ] T064 [P] [US4] Create unit test for offline fallback in tests/unit/test_ontology_loader.py
- [ ] T065 [US4] Create integration test for US4 in tests/integration/test_user_story_4.py (offline startup scenario)

**Checkpoint**: User Story 4 complete - system works offline using cached ontologies

---

## Phase 7: User Story 5 - Knowledge Graph Persistence Across Sessions (Priority: P3)

**Goal**: Serialize graph to disk on shutdown, restore on startup with re-applied inference

**Independent Test**: Add data, shutdown server, restart, verify all triples (explicit + inferred) restored

### Implementation for User Story 5

- [ ] T066 [P] [US5] Implement Turtle serialization in src/semantic_memory/knowledge/persistence.py (TurtlePersistence class with save/load methods)
- [ ] T067 [P] [US5] Implement SQLite backend in src/semantic_memory/knowledge/persistence.py (SQLitePersistence class using rdflib.Graph with SQLAlchemy store)
- [ ] T068 [P] [US5] Implement Oxigraph backend in src/semantic_memory/knowledge/persistence.py (OxigraphPersistence class - optional)
- [ ] T069 [US5] Add persistence backend factory in src/semantic_memory/knowledge/persistence.py (get_persistence_backend function based on config)
- [ ] T070 [US5] Integrate save on shutdown in src/semantic_memory/server.py (graceful shutdown handler)
- [ ] T071 [US5] Integrate load on startup in src/semantic_memory/server.py (before ontology loading)
- [ ] T072 [US5] Add re-inference after load in src/semantic_memory/server.py (call reasoner + rule engine after restoring graph)
- [ ] T073 [US5] Add persistence format config option in src/semantic_memory/config.py (PERSISTENCE_BACKEND, PERSISTENCE_PATH)
- [ ] T074 [P] [US5] Create unit test for Turtle persistence in tests/unit/test_persistence.py
- [ ] T075 [P] [US5] Create unit test for SQLite persistence in tests/unit/test_persistence.py
- [ ] T076 [US5] Create integration test for US5 in tests/integration/test_persistence_recovery.py (save → restart → load → verify)

**Checkpoint**: All user stories (P1, P2, P3) complete and independently functional

---

## Phase 8: Conflict Detection & System Stats

**Goal**: Implement conflict detection and get_graph_stats MCP tool

### Implementation

- [ ] T077 [P] Create conflict detection module in src/semantic_memory/knowledge/conflicts.py (ConflictDetector class)
- [ ] T078 [P] Implement contradictory literal detection in src/semantic_memory/knowledge/conflicts.py (same subject+predicate, different values)
- [ ] T079 [P] Implement disjoint class detection in src/semantic_memory/knowledge/conflicts.py (check owl:disjointWith in ontologies)
- [ ] T080 [P] Implement functional property violation detection in src/semantic_memory/knowledge/conflicts.py (check owl:FunctionalProperty)
- [ ] T081 Integrate conflict detection into add_memory tool in src/semantic_memory/tools/add_memory.py (run after inference)
- [ ] T082 Implement get_graph_stats MCP tool in src/semantic_memory/tools/get_graph_stats.py (triple counts, ontology status, rules, conflicts)
- [ ] T083 [P] Create unit test for conflict detection in tests/unit/test_conflicts.py
- [ ] T084 Create integration test for conflict detection in tests/integration/test_conflicts.py

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, documentation, and validation

- [ ] T085 [P] Add comprehensive docstrings to all public APIs in src/semantic_memory/
- [ ] T086 [P] Run mypy type checking across entire codebase and fix any errors
- [ ] T087 [P] Run black formatter on all Python files
- [ ] T088 [P] Run ruff linter and address warnings
- [ ] T089 [P] Update README.md with complete usage examples from quickstart.md
- [ ] T090 [P] Create CONTRIBUTING.md with development setup instructions
- [ ] T091 Add performance logging for query execution times in src/semantic_memory/tools/query_memory.py
- [ ] T092 Add CLI entry point in src/semantic_memory/__main__.py for direct execution
- [ ] T093 Validate all scenarios from quickstart.md manually
- [ ] T094 [P] Create example custom rule in user_rules/README.md
- [ ] T095 Add error recovery documentation in docs/error-handling.md
- [ ] T096 Review and update all type hints for Python 3.11+ syntax

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - MVP delivery target
- **User Story 2 (Phase 4)**: Depends on Foundational - Can run parallel to US1 with sufficient team
- **User Story 3 (Phase 5)**: Depends on Foundational + US2 (needs rule engine)
- **User Story 4 (Phase 6)**: Depends on Foundational + US1 (needs ontology loader)
- **User Story 5 (Phase 7)**: Depends on Foundational + US1 (needs graph operations)
- **Conflict Detection (Phase 8)**: Depends on US1 (needs graph and inference)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories - pure foundation
- **User Story 2 (P2)**: No dependencies on other stories - can run parallel to US1
- **User Story 3 (P2)**: Depends on US2 (needs rule engine for uncertain inferences)
- **User Story 4 (P3)**: Depends on US1 (extends ontology loading)
- **User Story 5 (P3)**: Depends on US1 (extends graph operations)

### Within Each User Story

- SPARQL rule files (T032-T036) can all be created in parallel
- Unit tests can run in parallel (all marked [P])
- Models and utilities can be created in parallel
- Services depend on models completing
- Integration tests depend on all implementation tasks

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003, T004, T005, T006, T007 can all run in parallel

**Phase 2 (Foundational)**:
- T012, T013, T014, T017 can all run in parallel

**User Story 2 (SPARQL Rules)**:
- T032, T033, T034, T035, T036 can all create .rq files in parallel
- T046, T047 tests can run in parallel

**User Story 3**:
- T049, T050 can run in parallel

**User Story 4**:
- T058, T063, T064 can run in parallel

**User Story 5**:
- T066, T067, T068 persistence backends can be implemented in parallel
- T074, T075 tests can run in parallel

**Phase 8 (Conflicts)**:
- T077, T078, T079, T080 can all run in parallel

---

## Parallel Example: User Story 2 (SPARQL Rules)

```bash
# Create all 5 default SPARQL rules in parallel:
Task T032: "Create spatial_transitivity.rq in src/rules/defaults/"
Task T033: "Create social_symmetry.rq in src/rules/defaults/"
Task T034: "Create coworkers_inference.rq in src/rules/defaults/"
Task T035: "Create interest_discovery.rq in src/rules/defaults/"
Task T036: "Create event_location_inheritance.rq in src/rules/defaults/"

# Then implement rule engine (sequential):
Task T037: "Create rule metadata model"
Task T038: "Implement rule loader"
Task T039: "Implement SPARQL rule validator"
Task T040: "Implement rule execution engine"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T009) → ~1-2 hours
2. Complete Phase 2: Foundational (T010-T017) → ~2-3 hours
3. Complete Phase 3: User Story 1 (T018-T031) → ~4-6 hours
4. **STOP and VALIDATE**: Test add_memory and query_memory with OWL-RL inference
5. **MVP DELIVERED**: Can now store memories and see automatic inferences

**Total MVP time estimate**: 8-12 hours of focused development

### Incremental Delivery

1. **Foundation** (Phases 1-2) → Basic structure ready
2. **MVP** (+ Phase 3 US1) → Can store and infer facts
3. **Custom Rules** (+ Phase 4 US2) → Can add domain logic
4. **Quality Control** (+ Phase 5 US3) → Uncertainty handling
5. **Robustness** (+ Phases 6-7 US4-US5) → Offline + persistence
6. **Production Ready** (+ Phases 8-9) → Conflicts + polish

### Parallel Team Strategy

With 2-3 developers after Foundational phase:

1. **Developer A**: User Story 1 (T018-T031) - Core inference
2. **Developer B**: User Story 2 SPARQL rules creation (T032-T036 parallel) + rule engine (T037-T048)
3. **Developer C**: User Story 4 caching (T058-T065) + User Story 5 persistence (T066-T076)

Stories integrate at MCP tool level with minimal conflicts.

---

## Notes

- [P] tasks can run in parallel (different files)
- [Story] label (US1, US2, etc.) maps task to user story for traceability
- All 5 SPARQL rules (T032-T036) must include proper PREFIX declarations
- Tests are included but optional - can be skipped for faster MVP
- Each user story checkpoint = independently deployable increment
- Stop at any checkpoint to validate before proceeding
- Provenance tracking is automatic throughout all phases
- Constitution compliance verified in Phase 2 (foundational)

---

## Task Count Summary

- **Phase 1 (Setup)**: 9 tasks
- **Phase 2 (Foundational)**: 8 tasks
- **Phase 3 (US1 - MVP)**: 14 tasks
- **Phase 4 (US2 - Custom Rules)**: 17 tasks (includes 5 SPARQL files)
- **Phase 5 (US3 - Verification)**: 9 tasks
- **Phase 6 (US4 - Offline)**: 8 tasks
- **Phase 7 (US5 - Persistence)**: 11 tasks
- **Phase 8 (Conflicts)**: 8 tasks
- **Phase 9 (Polish)**: 12 tasks

**Total**: 96 tasks

**MVP (Phases 1-3)**: 31 tasks
**Full Feature (All phases)**: 96 tasks

**Parallel opportunities**: 40+ tasks marked [P] can run concurrently
