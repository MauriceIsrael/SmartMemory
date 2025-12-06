# SmartMemory Deployment Guide

This guide explains how to deploy the SmartMemory MCP Server and Dashboard as a single Docker container.

## Prerequisites

*   **Docker Installed**: You need Docker Desktop or Docker Engine.
*   **GCP Account** (for Cloud Run): If deploying to Google Cloud.

## Local Deployment (Docker)

1.  **Build the Image**:
    ```bash
    docker build -t smart-memory .
    ```

2.  **Run the Container**:
    ```bash
    docker run -p 8080:8080 smart-memory
    ```

3.  **Access**:
    *   Dashboard: `http://localhost:8080`
    *   API: `http://localhost:8080/api/health`

## Deploy to Google Cloud Run

1.  **Install Google Cloud SDK**: ensure `gcloud` is installed and authenticated (`gcloud auth login`).

2.  **Configure Project**:
    ```bash
    gcloud config set project YOUR_PROJECT_ID
    ```

3.  **Build and Push the Image** (using Cloud Build):
    ```bash
    gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/smart-memory
    ```

4.  **Deploy to Cloud Run**:
    ```bash
    gcloud run deploy smart-memory \
      --image gcr.io/YOUR_PROJECT_ID/smart-memory \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated
    ```

    *Replace `YOUR_PROJECT_ID` with your actual GCP Project ID.*

## GitHub Actions (CI/CD)

To automate deployment, you can add a `.github/workflows/deploy.yml` file.

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches:
      - main

env:
  PROJECT_ID: your-project-id
  SERVICE_NAME: smart-memory
  REGION: us-central1

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: 'read'
      id-token: 'write'

    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Google Auth
        id: auth
        uses: 'google-github-actions/auth@v1'
        with:
          credentials_json: '${{ secrets.GCP_CREDENTIALS }}'

      - name: Deploy to Cloud Run
        uses: 'google-github-actions/deploy-cloudrun@v1'
        with:
          source: '.'
          service: ${{ env.SERVICE_NAME }}
          region: ${{ env.REGION }}
      - name: Deploy to Cloud Run
        uses: 'google-github-actions/deploy-cloudrun@v1'
        with:
          source: '.'
          service: ${{ env.SERVICE_NAME }}
          region: ${{ env.REGION }}

## Connecting via MCP (Hosted Mode)

Once deployed, your server will support **Server-Sent Events (SSE)** for remote MCP connections.

### Desktop Configuration (Claude)

If you have deployed to `https://smart-memory.example.com`, configure Claude Desktop as follows:

```json
{
  "mcpServers": {
    "smartmemory-hosted": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sse-client",
        "https://smart-memory.example.com/sse"
      ]
    }
  }
}
```

*Note: This requires `npx` (Node.js) on your local machine to run the SSE client proxy.*
