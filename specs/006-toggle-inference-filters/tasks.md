# Tasks for Feature: Manage Inference Engines and Filters

This document breaks down the implementation of feature `006-toggle-inference-filters` into actionable tasks, organized by user story.

## Phase 1: Setup

- [ ] T001 [P] In the backend, create a configuration file `src/supervision_backend/engine_state.json` to persist the state of inference engines.
- [ ] T002 [P] In the frontend, create a new file for an API service module at `src/supervision_frontend/src/lib/services/AdminService.ts`.

## Phase 2: Foundational (Backend API)

- [ ] T003 Define the Pydantic model for `InferenceEngineState` in a new file `src/supervision_backend/models/admin.py`.
- [ ] T004 Implement a new `EngineService` in `src/supervision_backend/services/engine_service.py` to read and write engine states to `engine_state.json`.
- [ ] T005 Create the base API router for the admin console in a new file `src/supervision_backend/api/routes/admin.py`.
- [ ] T006 Integrate the new admin router into the main FastAPI application in `src/supervision_backend/main.py`.

## Phase 3: User Story 1 - Toggle Inference Engines

- [ ] T007 [US1] Implement the `GET /api/inference-engines` endpoint in `src/supervision_backend/api/routes/admin.py` to list engine states.
- [ ] T008 [US1] Implement the `POST /api/inference-engines/{engine_name}` endpoint in `src/supervision_backend/api/routes/admin.py` to update an engine's state.
- [ ] T009 [P] [US1] Create a reusable `ToggleSwitch.svelte` component in `src/supervision_frontend/src/lib/components/ToggleSwitch.svelte`.
- [ ] T010 [US1] In the frontend's `AdminService.ts`, implement functions to fetch and update the engine states by calling the new backend endpoints.
- [ ] T011 [US1] Develop the Admin Console UI in `src/supervision_frontend/src/routes/admin/+page.svelte` to display and manage the inference engine toggles.

## Phase 4: User Story 2 - Filter Dynamically Loaded Rules

- [ ] T012 [US2] Implement the `GET /api/rules` endpoint with the `source` query parameter for filtering in `src/supervision_backend/api/routes/admin.py`.
- [ ] T013 [US2] In the frontend's `AdminService.ts`, add a function to fetch rules with the `source` filter.
- [ ] T014 [US2] Add a "Filter" UI control to the "Rule Management" page (e.g., `src/supervision_frontend/src/routes/rules/+page.svelte`) and connect it to the `AdminService` function.

## Phase 5: User Story 3 - Filter for Inferred Facts

- [ ] T015 [US3] Implement the `GET /api/facts` endpoint with the `origin` query parameter for filtering in `src/supervision_backend/api/routes/admin.py`.
- [ ] T016 [US3] In the frontend's `AdminService.ts`, add a function to fetch facts with the `origin` filter.
- [ ] T017 [US3] Add a "Filter" UI control to the "Facts" page (e.g., `src/supervision_frontend/src/routes/facts/+page.svelte`) and connect it to the `AdminService` function.

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T018 [P] Add robust error handling (e.g., for failed API calls) and user feedback notifications (e.g., toasts) across all new UI components.
- [ ] T019 [P] Write `pytest` unit tests for the new backend services and API endpoints in the `src/supervision_backend/tests/` directory.
- [ ] T020 [P] Write Vitest/Playwright integration tests for the frontend components to ensure the toggles and filters work end-to-end.

## Dependency Graph & Implementation Strategy

The implementation can proceed user story by user story, as they are largely independent after the foundational backend work is complete.

1.  **MVP Scope (User Story 1)**: Complete all `[US1]` tasks. This will deliver the core value of being able to toggle the engines.
    -   Dependencies: T001-T006 must be completed first.
    -   Independent Test: The admin console can be opened, toggles can be flipped, and the backend state file `engine_state.json` updates accordingly.

2.  **Increment 2 (User Story 2)**: Complete all `[US2]` tasks.
    -   Dependencies: MVP must be complete.
    -   Independent Test: The "Rule Management" page can be filtered to show only dynamically loaded rules.

3.  **Increment 3 (User Story 3)**: Complete all `[US3]` tasks.
    -   Dependencies: MVP must be complete.
    -   Independent Test: The "Facts" page can be filtered to show only inferred facts.

### Parallel Execution Examples:

-   **During US1**:
    -   Task `T009` (Frontend component) can be done in parallel with `T007` and `T008` (Backend endpoints).
-   **Overall**:
    -   The backend API (`T003-T008`, `T012`, `T015`) can be developed in parallel with the frontend UI (`T009-T011`, `T014`, `T017`) once the OpenAPI contract is agreed upon.
    -   Testing tasks (`T019`, `T020`) can be worked on in parallel with their corresponding implementation tasks.