# Tasks: Semantic Memory MCP Server

**Input**: Design documents from `specs/001-semantic-memory-mcp/`

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 Create project structure (`src`, `tests`)
- [X] T002 Initialize `pyproject.toml` with dependencies (`mcp-sdk`, `rdflib`, `pytest`) in `src/`

## Phase 2: Foundational (Blocking Prerequisites)

- [X] T003 [P] Implement the `Triple` data model in `src/models/triple.py`
- [X] T004 [P] Implement the `InferenceRule` data model in `src/models/inference_rule.py`
- [X] T005 [P] Implement the `VerificationRequest` data model in `src/models/verification_request.py`
- [X] T006 Implement the core `KnowledgeGraph` class in `src/models/knowledge_graph.py`, including `explicit_graph` and `inferred_graph`
- [X] T007 Implement the persistence service in `src/services/persistence_service.py` for saving and loading the graph to/from a `.ttl` file.

## Phase 3: User Story 1 - Semantic Ingestion (Priority: P1) 🎯 MVP

**Goal**: The system can take a user's statement and convert it into an RDF triple.

**Independent Test**: The system can be given a set of statements and we can verify that the correct triples are created in the knowledge graph.

- [X] T008 [P] [US1] Implement the `add_fact` MCP tool in `src/cli/add_fact.py`
- [X] T009 [US1] Implement a mock service in `src/services/conversion_service.py` that takes a natural language string and returns a hardcoded `Triple` object.

## Phase 4: User Story 2 - Light Inference Engine (Priority: P2)

**Goal**: The system can apply inference rules on new data to deduce new facts.

**Independent Test**: Given a knowledge graph and a new fact, we can verify that the expected inferred facts are generated.

- [X] T010 [US2] Implement a simple forward-chaining inference engine in `src/services/inference_engine.py`
- [X] T011 [US2] Integrate the inference engine with the `KnowledgeGraph` to run on new fact additions.

## Phase 5: User Story 3 - Elicitation Loop (Priority: P1)

**Goal**: The system can ask for user verification when an inference is not certain.

**Independent Test**: Given an inference with a medium certainty score, we can verify that the system issues a `request_verification` tool call.

- [X] T012 [P] [US3] Implement the `get_pending_verifications` MCP tool in `src/cli/get_pending_verifications.py`
- [X] T013 [US3] Implement the logic in the `InferenceEngine` to create `VerificationRequest` objects when the certainty score of an inference is below a threshold.

## Phase 6: User Story 4 - Persistence (Priority: P2)

**Goal**: The system can save the knowledge graph to a file.

**Independent Test**: We can save the knowledge graph, shut down the server, restart it, and verify that the knowledge is still present.

- [X] T014 [US4] Integrate the `PersistenceService` with the `KnowledgeGraph` to save the graph when the server shuts down and load it on startup.

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T015 [P] Add logging to all services and tools.
- [X] T016 [P] Add comprehensive error handling for all services and tools.
- [X] T017 [P] Write unit tests for all models in `tests/unit/`
- [X] T018 [P] Write unit tests for all services in `tests/unit/`
- [X] T019 Write integration tests for the MCP tools in `tests/integration/`
