# Implementation Plan: Manage Inference Engines and Filters

**Branch**: `006-toggle-inference-filters` | **Date**: 2025-11-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-toggle-inference-filters/spec.md`

## Summary

This feature introduces an administration console for managing the two inference engines ("OWL-RL Engine" and "SPARQL Engine"). The technical approach involves creating API endpoints in the Python backend to toggle the engines' state and filter rules/facts. The Svelte/TypeScript frontend will be updated to include UI controls (toggles and filter buttons) that interact with these new endpoints. State will be persisted on the backend.

## Technical Context

**Language/Version**: Backend: Python 3.11+; Frontend: TypeScript/Svelte
**Primary Dependencies**: Backend: FastAPI, rdflib; Frontend: SvelteKit
**Storage**: File-based RDF graph (persisted via `rdflib` store)
**Testing**: `pytest` for the backend; Vitest/Playwright for the frontend
**Target Platform**: Linux server (backend), Web Browser (frontend)
**Project Type**: Web application with a separate frontend and backend.
**Performance Goals**: UI updates < 3 seconds; Engine state changes < 15 seconds.
**Constraints**: Must integrate with the existing `supervision_backend` and `supervision_frontend` applications.
**Scale/Scope**: This feature applies to the two existing inference engines and is scoped to the administration console.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

*   **No "Flat" Data:** Pass. The feature manages RDF rules and facts.
*   **Active, Not Passive:** Pass. The feature is centered on activating/deactivating inference engines.
*   **Trust but Verify:** N/A. This feature does not introduce new uncertain inferences.
*   **Language:** Pass. The implementation uses Python and TypeScript.
*   **Standards:** Pass. Adheres to RDF standards.
*   **Protocol:** N/A. This feature concerns the admin interface, not the core MCP.
*   **Type Safety:** Pass. The plan requires strict typing for both backend and frontend code.
*   **Ontology First:** Pass. The feature will use the existing ontology for rules and facts.
*   **Immutability:** Pass. The feature correctly distinguishes between stated/inferred and default/dynamic data.
*   **Interaction Model:** Pass. The feature provides tools for the "Gardener" (admin).

## Project Structure

### Documentation (this feature)

```text
specs/006-toggle-inference-filters/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── openapi.yml
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/            # Add/update models for engine state
│   ├── services/          # Add/update services for engine management
│   └── api/               # Add new endpoints for engine control and filtering
│       └── routes/
│           └── admin.py
└── tests/

frontend/
├── src/
│   ├── components/        # Add new Svelte components (toggles, filter controls)
│   ├── routes/            # Add/update pages for the admin console
│   │   └── admin/
│   └── services/          # Add new API service to call backend endpoints
└── tests/
```

**Structure Decision**: The feature modifies the existing `supervision_backend` and `supervision_frontend` applications, which correspond to the `backend/` and `frontend/` directories in the project structure. New code will be added to the appropriate `api`, `services`, `components`, and `routes` subdirectories.

## Complexity Tracking

No violations to the constitution have been identified.