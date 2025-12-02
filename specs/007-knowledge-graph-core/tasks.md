# Tasks for Feature: Knowledge Graph Core Components

This document breaks down the implementation of feature `007-knowledge-graph-core` into actionable tasks, organized by user story. All file paths are relative to the `src/` directory.

## Phase 1: Setup
- [ ] T001 [P] Create the directory structure `src/models/`, `src/queue/`, `src/dispatcher/`, `src/handlers/`, and `src/memory/` if they do not exist.

## Phase 2: Foundational (Core Data Models & Interfaces)
- [ ] T002 Implement the `Fact` Pydantic model as defined in the data model in `models/fact.py`.
- [ ] T003 Define the `IFactQueue` Abstract Base Class in `queue/fact_queue.py`.
- [ ] T004 Define the `IFactHandler` Abstract Base Class in `dispatcher/fact_dispatcher.py`.

## Phase 3: User Story 1 - Fact Ingestion and Structuring
- [ ] T005 [US1] Implement the `MemoryFactQueue` class in `queue/fact_queue.py`, including the `asyncio.Queue`, `set` for duplicate prevention, and `asyncio.Lock`.
- [ ] T006 [US1] Implement the `enqueue` method in `queue/fact_queue.py`.
- [ ] T007 [US1] Implement the `dequeue_batch` method in `queue/fact_queue.py`.

## Phase 4: User Story 2 - Asynchronous Fact Processing
- [ ] T008 [US2] Implement the `FactDispatcher` class structure in `dispatcher/fact_dispatcher.py`.
- [ ] T009 [US2] Implement the `register_handler` method in `dispatcher/fact_dispatcher.py`.
- [ ] T010 [US2] Implement the `start_dispatching` async loop in `dispatcher/fact_dispatcher.py`, using `asyncio.gather` to call handlers.
- [ ] T011 [P] [US2] Create a stub implementation for `FastInferenceHandler` in `handlers/fast_inference.py`.
- [ ] T012 [P] [US2] Create a stub implementation for `DeepReasoningHandler` in `handlers/deep_reasoning.py`.

## Phase 5: User Story 3 - Working Memory and Attention Mechanism
- [ ] T013 [US3] Implement the `MemoryNode` class (as a Pydantic model or dataclass) in `memory/node.py`.
- [ ] T014 [US3] Implement the `AttentionGraph` class structure in `memory/attention_graph.py`.
- [ ] T015 [P] [US3] Implement the `add_node` and `stimulate` methods in `memory/attention_graph.py`.
- [ ] T016 [P] [US3] Implement the `decay` and `prune` methods in `memory/attention_graph.py`.
- [ ] T017 [US3] Implement the `get_active_subgraph` method in `memory/attention_graph.py`.

## Phase 6: Polish & Cross-Cutting Concerns
- [ ] T018 [P] Add unit tests for the `Fact` model, including ID generation, in `tests/unit/test_models.py`.
- [ ] T019 [P] Add unit tests for `MemoryFactQueue` to verify queuing logic and duplicate prevention in `tests/unit/test_queue.py`.
- [ ] T020 [P] Add unit tests for `FactDispatcher` with mock handlers to verify correct dispatching in `tests/unit/test_dispatcher.py`.
- [ ] T021 [P] Add unit tests for `AttentionGraph` to verify `stimulate`, `decay`, and `prune` logic in `tests/unit/test_memory.py`.
- [ ] T022 Add logging to the `FactDispatcher` and `MemoryFactQueue` for better traceability.

## Dependency Graph & Implementation Strategy

The implementation is designed to be incremental, with each user story building upon the previous one.

1.  **MVP Scope (User Story 1)**: Complete `T001-T007`.
    -   This provides the foundational capability to ingest facts into a structured, de-duplicated, in-memory queue.
    -   **Independent Test**: Write a script that creates `Fact` instances and enqueues them into a `MemoryFactQueue`. Verify that duplicates are ignored and that facts can be dequeued in batches. This aligns with the `quickstart.md`.

2.  **Increment 2 (User Story 2)**: Complete `T008-T012`.
    -   This adds the processing layer, enabling facts from the queue to be dispatched to various handlers.
    -   **Dependencies**: Requires the `IFactQueue` and `Fact` model from the MVP.
    -   **Independent Test**: Extend the MVP test script. Create mock `IFactHandler`s, register them with the `FactDispatcher`, and start the dispatcher. Verify that the mock handlers receive the fact batches as expected.

3.  **Increment 3 (User Story 3)**: Complete `T013-T017`.
    -   This adds the advanced working memory model.
    -   **Dependencies**: Requires the `Fact` model from the MVP. It can be developed and tested in parallel with User Story 2, but its full integration benefits from the existence of a fact processing pipeline.
    -   **Independent Test**: Write a script that instantiates an `AttentionGraph`, adds `MemoryNode`s, and calls the `stimulate`, `decay`, and `prune` methods. Assert that the internal state of the graph changes as expected.

### Parallel Execution Examples:

-   **During Foundational Phase**: `T002`, `T003`, and `T004` can be done in parallel as they define interfaces and models in separate files.
-   **During US2**: The stub handlers (`T011`, `T012`) can be created in parallel with the dispatcher (`T008-T010`).
-   **Overall**: The `AttentionGraph` (US3) can be developed largely in parallel with the `FactDispatcher` (US2), as they only share the `Fact` model. Unit tests (`T018-T021`) can also be developed in parallel with their respective implementation tasks.
