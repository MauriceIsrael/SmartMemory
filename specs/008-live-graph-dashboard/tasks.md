# Tasks for Feature: Live-Updating Dashboard Graph

This document breaks down the implementation of feature `008-live-graph-dashboard` into actionable tasks.

## Phase 1: Setup
- [ ] T001 [P] In the `supervision_backend`, create a new file `src/supervision_backend/handlers/realtime_handler.py`.
- [ ] T002 [P] In the `supervision_frontend`, create a new file `src/supervision_frontend/src/lib/services/RealtimeService.ts`.
- [ ] T003 [P] In the `supervision_frontend`, create a new file `src/supervision_frontend/src/lib/stores/graphStore.ts` for managing graph state.

## Phase 2: Foundational (Backend SSE)

- [ ] T004 Implement a new `RealtimeUpdateHandler` class in `src/supervision_backend/handlers/realtime_handler.py`. It should inherit from the `IFactHandler` interface defined in feature `007-knowledge-graph-core`.
- [ ] T005 Implement a mechanism within `RealtimeUpdateHandler` to pass received facts to the SSE endpoint. An `asyncio.Queue` is a suitable choice for this.
- [ ] T006 Implement the Server-Sent Events (SSE) endpoint at `GET /api/v1/graph/updates` in `src/supervision_backend/api/routes/admin.py`. This endpoint should read from the queue populated by `RealtimeUpdateHandler` and stream events.
- [ ] T007 In the main application startup logic (where `FactDispatcher` is configured), register an instance of the new `RealtimeUpdateHandler`.

## Phase 3: User Story 1 - Live Graph Monitoring

- [ ] T008 [US1] In `src/supervision_frontend/src/lib/stores/graphStore.ts`, create a Svelte writable store to hold the graph's nodes and edges.
- [ ] T009 [US1] In `src/supervision_frontend/src/lib/services/RealtimeService.ts`, implement the logic to connect to the backend's `/api/v1/graph/updates` SSE endpoint using the browser's `EventSource` API.
- [ ] T010 [US1] In `src/supervision_frontend/src/lib/services/RealtimeService.ts`, add a listener for the `graph_update` event. When an event is received, parse its JSON data.
- [ ] T011 [US1] Update the `graphStore` with the new node and edge data received from the SSE event. The `RealtimeService` will call a method on the store to add the new data.
- [ ] T012 [US1] Modify the main graph visualization component (e.g., in `src/supervision_frontend/src/routes/+page.svelte`) to subscribe to the `graphStore` and reactively re-render when its data changes.

## Phase 4: Polish & Cross-Cutting Concerns

- [ ] T013 [P] In `src/supervision_frontend/src/lib/services/RealtimeService.ts`, implement robust error handling for the `EventSource` connection, including automatic reconnection attempts with backoff.
- [ ] T014 [P] Add unit tests for the `RealtimeUpdateHandler` in the backend to ensure it correctly processes facts and passes them to its internal queue.
- [ ] T015 [P] Add an integration test for the `/api/v1/graph/updates` endpoint to verify that it streams data correctly when a fact is processed.

## Dependency Graph & Implementation Strategy

This feature can be implemented as a single unit, but the backend and frontend work can be parallelized.

1.  **MVP Scope (User Story 1)**: Complete all tasks `T001-T012`.
    -   This delivers the full end-to-end functionality for live graph updates.
    -   **Dependencies**: This feature depends on the completion of `007-knowledge-graph-core`, specifically the `FactDispatcher` and `IFactHandler` interface. The backend handler (`T004-T007`) must be implemented before the frontend (`T008-T012`) can be fully tested.
    -   **Independent Test**: As described in the `quickstart.md` for this feature: start all servers, open the dashboard, add a fact via the CLI, and watch the graph update automatically on the web page.

### Parallel Execution Examples:

-   **Backend vs. Frontend**: The entire backend implementation (`T004-T007` and `T014-T015`) can be done in parallel with the entire frontend implementation (`T008-T013`). The teams can work from the agreed-upon `openapi.yml` contract.
-   **Within Frontend**: The `graphStore` (`T008`) and the `RealtimeService` (`T009`, `T010`) can be developed in parallel with updating the visualization component (`T012`), as long as the store's interface is defined early.
