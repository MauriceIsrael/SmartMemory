# Quick Start: Live Graph Dashboard

This guide explains how to run the components and see the live-updating graph feature in action.

## Prerequisites

- Python 3.11+
- Node.js and npm
- All Python and Node dependencies for the project are installed.

## Running the Application

### 1. Start the Main Backend Server

This server handles the core logic of the knowledge graph.

```bash
# From the project root directory
cd src/
python -m semantic_memory.server
```

### 2. Start the Supervision Backend

This server provides the API for the supervision dashboard, including the new SSE endpoint.

```bash
# From a new terminal, in the project root directory
cd src/supervision_backend/
./start.sh
```

### 3. Start the Supervision Frontend

This starts the SvelteKit development server for the dashboard UI.

```bash
# From a new terminal, in the project root directory
cd src/supervision_frontend/
npm install
npm run dev
```
After running this command, your terminal will display a URL for the local development server (e.g., `http://localhost:5173`).

### 4. Observe the Feature

1.  Open your web browser and navigate to the URL from the previous step (e.g., `http://localhost:5173`). You should see the supervision dashboard with the graph visualization.
2.  In a new terminal, use the `add_fact` CLI tool to add a new fact to the knowledge graph.
    ```bash
    # From the project root directory
    cd src/
    python -m cli.add_fact "http://example.com/User/Alice" "http://xmlns.com/foaf/0.1/name" "Alice"
    ```
3.  **Observe the dashboard in your browser.** Within a few seconds, you should see a new node for "Alice" appear in the graph visualization automatically, without needing to refresh the page. The graph has updated in real-time.
