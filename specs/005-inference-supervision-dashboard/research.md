# Research & Decisions: Inference Supervision Dashboard

## Technology Stack Selection

### Decision

*   **Frontend**: SvelteKit with Svelte 5
*   **Backend API**: FastAPI (Python)
*   **Styling**: TailwindCSS

### Rationale

This stack was explicitly requested in the initial feature description.

*   **SvelteKit** was chosen for its modern, reactive framework, providing a fast and component-based architecture suitable for a dashboard application. Svelte 5 is preferred for its use of runes, which simplifies reactivity.
*   **FastAPI** was chosen as a lightweight Python backend to serve as a bridge to the existing `SmartMemory` Python components. Its asynchronous nature is well-suited for I/O-bound operations like querying the knowledge graph.
*   **TailwindCSS** was selected for its utility-first approach, enabling rapid development of a modern and customizable user interface, including the requested "dark mode".

### Alternatives Considered

*   No alternatives were considered as the technology stack was a primary requirement of the feature request.
