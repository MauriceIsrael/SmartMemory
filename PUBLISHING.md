# Publishing SmartMemory to the MCP Registry

The **Model Context Protocol (MCP) Registry** allows users to discover tools and servers easily. Publishing SmartMemory there will make it visible to the community.

> [!NOTE]
> Ensure your project is publicly accessible (e.g., on GitHub) before publishing.

## Prerequisites

*   **GitHub Account**: Required for authentication.
*   **mcp-publisher**: The CLI tool for the registry.

## Step-by-Step Guide

### 1. Install the Publisher Tool

**macOS / Linux (Homebrew)**
```bash
brew install modelcontextprotocol/tap/mcp-publisher
```

**From Source**
If you don't use Homebrew, query the [official repository](https://github.com/modelcontextprotocol/registry) for instructions.

### 2. Initialize Configuration

Navigate to the project root and run:

```bash
mcp-publisher init
```

This will create a `server.json` file. You will be prompted to enter:
*   **Name**: `smart-memory` (or similar unique name)
*   **Description**: "Neuro-symbolic memory for LLMs (POC)"
*   **Vendor**: Your GitHub username or organization (e.g., `@yourusername`)

### 3. Update `server.json`

Edit the generated `server.json` to point to your Docker image or PyPI package. Since we have a Dockerfile, using the Docker image is often easiest.

Example configuration:

```json
{
  "$schema": "https://registry.modelcontextprotocol.io/schema/server.json",
  "name": "smart-memory",
  "description": "A neuro-symbolic memory server that learns from conversation.",
  "vendor": "@yourusername",
  "version": "0.1.0",
  "distribution": {
    "docker": {
      "image": "ghcr.io/yourusername/smart-memory:latest"
    }
  }
}
```

> [!IMPORTANT]
> Make sure `ghcr.io/yourusername/smart-memory:latest` exists and is public! You can push it using the steps in [DEPLOY.md](DEPLOY.md).

### 4. Authenticate

Log in with your GitHub account:

```bash
mcp-publisher login github
```

### 5. Publish

Validate and push your manifest to the registry:

```bash
mcp-publisher publish
```

## Verification

Once published, anyone can install your server using:

```bash
npx -y @modelcontextprotocol/server-sse-client \
  https://registry.modelcontextprotocol.io/servers/smart-memory
# (Command depends on final registry implementation)
```

Or simply find it in the MCP Index alongside other tools.
