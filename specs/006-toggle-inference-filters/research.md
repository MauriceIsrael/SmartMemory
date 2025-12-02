# Research & Decisions: Manage Inference Engines and Filters

## 1. Technology Stack Selection

### Decision
- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: SvelteKit with TypeScript

### Rationale
- The existing project structure contains `supervision_backend/` with Python files (`main.py`, `requirements.txt`) and `supervision_frontend/` with Svelte files (`svelte.config.js`, `package.json`).
- FastAPI is chosen for the backend as it is a modern, high-performance web framework for Python that aligns with the constitution's "Type Safety" principle.
- SvelteKit is the incumbent framework in the frontend, so we will continue to use it.

### Alternatives Considered
- **Flask for backend**: Flask is a viable alternative, but FastAPI's first-class support for async operations and automatic OpenAPI documentation generation makes it a better fit for this project's API-driven nature.
- **React/Vue for frontend**: While viable, adhering to the existing SvelteKit framework reduces complexity and maintains consistency.

## 2. State Management

### Decision
- The enabled/disabled state of the inference engines will be managed on the backend and stored in a persistent configuration file (e.g., a simple JSON or YAML file).

### Rationale
- Persisting state on the backend is required by `FR-002` ("state...MUST be persisted across application restarts").
- A simple file-based configuration is sufficient for the scale of this feature (only two engines) and avoids introducing a heavy database dependency. The backend service will be responsible for reading and writing this file.

### Alternatives Considered
- **Database Storage**: Using a database like SQLite would be more robust but adds unnecessary complexity for managing two boolean flags. It can be considered in the future if configuration needs become more complex.
