# Quickstart: Inference Supervision Dashboard

This guide provides instructions for setting up and running the Inference Supervision Dashboard and its backend API.

## Prerequisites

*   Python 3.11+
*   Node.js and npm (or equivalent package manager)
*   An existing `SmartMemory` instance or the ability to run one.

## Backend Setup (FastAPI)

1.  **Navigate to the backend directory**:
    ```bash
    cd src/supervision_backend 
    ```
    *(Note: This directory will be created in a later phase)*

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the server**:
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

## Frontend Setup (SvelteKit)

1.  **Navigate to the frontend directory**:
    ```bash
    cd src/supervision_frontend
    ```
    *(Note: This directory will be created in a later phase)*

2.  **Install dependencies**:
    ```bash
    npm install
    ```

3.  **Run the development server**:
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:5173`.

## Running the Application

Once both the backend and frontend servers are running, you can access the dashboard by opening your browser to `http://localhost:5173`.
