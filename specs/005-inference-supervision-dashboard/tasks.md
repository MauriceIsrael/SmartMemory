# Tasks: Inference Supervision Dashboard

This document breaks down the implementation of the Inference Supervision Dashboard into actionable tasks, organized by user story.

## Implementation Strategy

The implementation will follow an incremental, user-story-based approach. Each phase, corresponding to a user story, will deliver a testable, vertical slice of functionality. The MVP will consist of the foundational setup and the first user story (Dashboard View).

## Dependencies

The user stories are largely independent and can be developed in parallel after the Foundational phase is complete. However, a logical implementation order is: US1 → US2 → US3 → US4.

*   **US1 (Dashboard)**: No dependencies on other stories.
*   **US2 (Fact Explorer)**: No dependencies on other stories.
*   **US3 (Rule Management)**: No dependencies on other stories.
*   **US4 (Admin Console)**: No dependencies on other stories.

## Parallel Execution

Within each user story, backend and frontend tasks can be developed in parallel. For example, in US1, while one developer works on the `/stats` endpoint, another can build the Svelte components for the dashboard.

*   **Example (US1)**:
    *   Parallel 1: `T010` (Backend endpoint)
    *   Parallel 2: `T011`, `T012`, `T013` (Frontend components and integration)

---

## Phase 1: Setup

*Goal: Initialize the project structure and install dependencies.*

- [ ] T001 Create project directories: `backend/` and `frontend/`
- [ ] T002 [P] Initialize FastAPI project in `backend/` with a `main.py` and `requirements.txt`
- [ ] T003 [P] Initialize SvelteKit project in `frontend/`
- [ ] T004 [P] Add FastAPI and uvicorn to `backend/requirements.txt`
- [ ] T005 [P] Add TailwindCSS to the SvelteKit project in `frontend/`

## Phase 2: Foundational

*Goal: Establish the core application structure and connectivity.*

- [ ] T006 Create `backend/src/api/` and `backend/src/services/` directories
- [ ] T007 [P] Create `frontend/src/lib/`, `frontend/src/routes/`, and `frontend/src/components/` directories
- [ ] T008 Implement a `MemoryService` in `backend/src/services/memory_service.py` to connect to the main `SmartMemory` instance.
- [ ] T009 Implement the main navigation sidebar component in `frontend/src/components/Sidebar.svelte`

## Phase 3: User Story 1 - Daily System Health Check

*Goal: Implement the main dashboard view with KPI cards.*
*Independent Test: A user can load the main page and see the correct, up-to-date statistics for Total Facts, Inferred Facts, and Active Rules.*

- [ ] T010 [US1] Implement the `GET /stats` endpoint in `backend/src/api/endpoints/stats.py`
- [ ] T011 [P] [US1] Create an API client function in `frontend/src/lib/api.ts` to fetch data from the `/stats` endpoint.
- [ ] T012 [P] [US1] Create a `StatCard.svelte` component in `frontend/src/components/StatCard.svelte` to display a single KPI.
- [ ] T013 [US1] Implement the main dashboard page in `frontend/src/routes/+page.svelte`, using `StatCard` to display the stats.
- [ ] T014 [US1] Implement the "facts created over time" graph on the dashboard page `frontend/src/routes/+page.svelte`.

## Phase 4: User Story 2 - Investigating an Inferred Fact

*Goal: Implement the Fact Explorer page.*
*Independent Test: A user can navigate to the Fact Explorer, see a paginated list of all facts, and use the search bar to filter for a specific fact.*

- [ ] T015 [US2] Implement the `GET /facts` endpoint in `backend/src/api/endpoints/facts.py`, including pagination and search functionality.
- [ ] T016 [P] [US2] Create an API client function in `frontend/src/lib/api.ts` for the `/facts` endpoint.
- [ ] T017 [P] [US2] Create a `FactTable.svelte` component in `frontend/src/components/FactTable.svelte`.
- [ ] T018 [US2] Implement the Fact Explorer page in `frontend/src/routes/facts/+page.svelte`, using the `FactTable` component.
- [ ] T019 [US2] Add visual badges to `FactTable.svelte` to distinguish between asserted and inferred facts.

## Phase 5: User Story 3 - Disabling a Noisy Inference Rule

*Goal: Implement the Rule Management page.*
*Independent Test: A user can view all inference rules, see their stats, and successfully toggle a rule's active state.*

- [ ] T020 [US3] Implement the `GET /rules` endpoint in `backend/src/api/endpoints/rules.py`.
- [ ] T021 [US3] Implement the `POST /rules/{id}/toggle` endpoint in `backend/src/api/endpoints/rules.py`.
- [ ] T022 [P] [US3] Create API client functions in `frontend/src/lib/api.ts` for the `/rules` and `/rules/{id}/toggle` endpoints.
- [ ] T023 [P] [US3] Create a `RuleList.svelte` component in `frontend/src/components/RuleList.svelte`.
- [ ] T024 [P] [US3] Create a `RuleToggle.svelte` component in `frontend/src/components/RuleToggle.svelte`.
- [ ] T025 [US3] Implement the Rule Management page in `frontend/src/routes/rules/+page.svelte`, using the `RuleList` component.
- [ ] T026 [US3] Integrate toast notifications to provide feedback when a rule is toggled.

## Phase 6: User Story 4 - Manually Running Inference

*Goal: Implement the Administration Console.*
*Independent Test: A user can click the "Run Inference" button and receive feedback that the process has started.*

- [ ] T027 [US4] Implement the `POST /inference/run` endpoint in `backend/src/api/endpoints/inference.py`.
- [ ] T028 [P] [US4] Create an API client function in `frontend/src/lib/api.ts` for the `/inference/run` endpoint.
- [ ] T029 [US4] Implement the Administration Console page in `frontend/src/routes/admin/+page.svelte`.
- [ ] T030 [US4] Add a "Run Inference" button and loading indicator to the Admin page.

## Phase 7: Polish & Cross-Cutting Concerns

*Goal: Implement final UI polish and handle application-wide concerns.*

- [ ] T031 [P] Implement the dark mode theme across all pages.
- [ ] T032 [P] Implement graceful error handling for API connection issues.
- [ ] T033 Review and add fluid animations and transitions for a "Wow" effect.
- [ ] T034 [P] Add empty state messages to the Fact Explorer and Rule Management pages.
- [ ] T035 [P] Add tooltips to display rule validation errors.
