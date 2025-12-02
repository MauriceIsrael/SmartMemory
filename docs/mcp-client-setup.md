# MCP Client Setup Guide

Complete guide for configuring SmartMemory with various MCP-compatible LLM clients.

## Table of Contents

- [Claude Desktop](#claude-desktop)
- [Continue.dev (VS Code)](#continuedev-vs-code)
- [Cline (VS Code)](#cline-vs-code)
- [Zed Editor](#zed-editor)
- [Custom MCP Clients](#custom-mcp-clients)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

1. **SmartMemory installed** and accessible on your system
2. **Python 3.11+** with virtual environment activated
3. **Absolute path** to your SmartMemory installation (e.g., `/home/user/SmartMemory`)

---

## Claude Desktop

### macOS

**Config file location**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "semantic-memory": {
      "command": "/Users/yourname/SmartMemory/venv/bin/python",
      "args": ["-m", "semantic_memory.server"],
      "env": {
        "SEMMEM_LOG_LEVEL": "INFO",
        "SEMMEM_PERSISTENCE_PATH": "/Users/yourname/.smartmemory/knowledge_graph.ttl"
      }
    }
  }
}
```

### Linux

**Config file location**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "semantic-memory": {
      "command": "/home/yourname/SmartMemory/venv/bin/python",
      "args": ["-m", "semantic_memory.server"],
      "env": {
        "SEMMEM_LOG_LEVEL": "INFO",
        "SEMMEM_PERSISTENCE_PATH": "/home/yourname/.smartmemory/knowledge_graph.ttl"
      }
    }
  }
}
```

### Windows

**Config file location**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "semantic-memory": {
      "command": "C:\\Users\\YourName\\SmartMemory\\venv\\Scripts\\python.exe",
      "args": ["-m", "semantic_memory.server"],
      "env": {
        "SEMMEM_LOG_LEVEL": "INFO",
        "SEMMEM_PERSISTENCE_PATH": "C:\\Users\\YourName\\.smartmemory\\knowledge_graph.ttl"
      }
    }
  }
}
```

### Quick Setup (Command Line)

```bash
# macOS/Linux
claude mcp add-json semantic-memory '{
  "command": "/home/yourname/SmartMemory/venv/bin/python",
  "args": ["-m", "semantic_memory.server"]
}'

# Verify it's working
claude mcp list
```

---

## Continue.dev (VS Code)

**Config file location**: `~/.continue/config.json`

```json
{
  "models": [...],
  "mcpServers": [
    {
      "name": "semantic-memory",
      "command": "/home/yourname/SmartMemory/venv/bin/python",
      "args": ["-m", "semantic_memory.server"],
      "env": {
        "SEMMEM_LOG_LEVEL": "INFO"
      }
    }
  ]
}
```

### Testing in Continue.dev

1. Open VS Code with Continue.dev extension
2. Open the Continue sidebar (Cmd+L or Ctrl+L)
3. Type: "Use semantic memory to remember that Alice works at Google"
4. Continue should automatically call the `add_memory` tool

---

## Cline (VS Code)

**Config file location**: `~/.cline/mcp_settings.json`

```json
{
  "mcpServers": {
    "semantic-memory": {
      "command": "/home/yourname/SmartMemory/venv/bin/python",
      "args": ["-m", "semantic_memory.server"],
      "cwd": "/home/yourname/SmartMemory",
      "env": {
        "SEMMEM_LOG_LEVEL": "INFO",
        "SEMMEM_CACHE_DIR": "/home/yourname/.smartmemory/cache"
      }
    }
  }
}
```

### VS Code Settings (Alternative)

Add to `.vscode/settings.json` in your project:

```json
{
  "cline.mcpServers": {
    "semantic-memory": {
      "command": "/home/yourname/SmartMemory/venv/bin/python",
      "args": ["-m", "semantic_memory.server"]
    }
  }
}
```

---

## Zed Editor

**Config file location**: `~/.config/zed/settings.json`

```json
{
  "language_models": {
    "mcp_servers": {
      "semantic-memory": {
        "command": {
          "path": "/home/yourname/SmartMemory/venv/bin/python",
          "args": ["-m", "semantic_memory.server"]
        },
        "env": {
          "SEMMEM_LOG_LEVEL": "INFO"
        }
      }
    }
  }
}
```

---

## Custom MCP Clients

For Python-based MCP clients using the MCP SDK:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure server parameters
server_params = StdioServerParameters(
    command="/home/yourname/SmartMemory/venv/bin/python",
    args=["-m", "semantic_memory.server"],
    env={
        "SEMMEM_LOG_LEVEL": "DEBUG",
        "SEMMEM_PERSISTENCE_PATH": "./my_knowledge_graph.ttl"
    }
)

# Connect to the server
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize
        await session.initialize()
        
        # List available tools
        tools = await session.list_tools()
        print(f"Available tools: {[t.name for t in tools.tools]}")
        
        # Call add_memory tool
        result = await session.call_tool(
            "add_memory",
            arguments={"input": "Alice works at Google"}
        )
        print(result.content[0].text)
```

---

## Environment Variables

Configure SmartMemory behavior via environment variables:

### Core Settings

```bash
# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
export SEMMEM_LOG_LEVEL=INFO

# Persistence file location
export SEMMEM_PERSISTENCE_PATH=/path/to/knowledge_graph.ttl

# Persistence backend (turtle, sqlite, oxigraph)
export SEMMEM_PERSISTENCE_BACKEND=turtle
```

### Cache Settings

```bash
# Cache directory for ontologies
export SEMMEM_CACHE_DIR=~/.smartmemory/cache

# Cache TTL in hours
export SEMMEM_CACHE_TTL_HOURS=24

# Force offline mode (use cached ontologies only)
export SEMMEM_FORCE_OFFLINE=false
```

### Inference Settings

```bash
# Maximum inference depth (prevent loops)
export SEMMEM_MAX_INFERENCE_DEPTH=10

# Auto-accept threshold for inferences (0.0-1.0)
export SEMMEM_AUTO_ACCEPT_THRESHOLD=0.85

# Default confidence for custom rules
export SEMMEM_DEFAULT_RULE_CONFIDENCE=0.75
```

### Rule Directories

```bash
# Default rules directory
export SEMMEM_DEFAULT_RULES_DIR=/path/to/SmartMemory/src/rules/defaults

# User custom rules directory
export SEMMEM_USER_RULES_DIR=/path/to/my_custom_rules
```

### Full Example Configuration

```json
{
  "mcpServers": {
    "semantic-memory": {
      "command": "/home/yourname/SmartMemory/venv/bin/python",
      "args": ["-m", "semantic_memory.server"],
      "env": {
        "SEMMEM_LOG_LEVEL": "INFO",
        "SEMMEM_PERSISTENCE_PATH": "/home/yourname/.smartmemory/knowledge.ttl",
        "SEMMEM_PERSISTENCE_BACKEND": "turtle",
        "SEMMEM_CACHE_DIR": "/home/yourname/.smartmemory/cache",
        "SEMMEM_CACHE_TTL_HOURS": "48",
        "SEMMEM_FORCE_OFFLINE": "false",
        "SEMMEM_MAX_INFERENCE_DEPTH": "10",
        "SEMMEM_AUTO_ACCEPT_THRESHOLD": "0.85",
        "SEMMEM_USER_RULES_DIR": "/home/yourname/.smartmemory/rules"
      }
    }
  }
}
```

---

## Troubleshooting

### Server Won't Start

**Problem**: MCP client reports "Server failed to start"

**Solutions**:
1. Check Python path is correct:
   ```bash
   /path/to/venv/bin/python --version
   # Should show Python 3.11+
   ```

2. Test server manually:
   ```bash
   /path/to/venv/bin/python -m semantic_memory.server
   # Should start without errors
   ```

3. Check logs (if configured):
   ```bash
   tail -f /path/to/logs/mcp_server.log
   ```

### Tools Not Showing Up

**Problem**: LLM says "No tools available"

**Solutions**:
1. Restart the MCP client completely
2. Check config file syntax (JSON must be valid)
3. Verify server initialization:
   ```bash
   # Add debug logging
   "env": {"SEMMEM_LOG_LEVEL": "DEBUG"}
   ```

### Persistence Errors

**Problem**: "Failed to save/load graph"

**Solutions**:
1. Check directory exists and is writable:
   ```bash
   mkdir -p ~/.smartmemory
   chmod 755 ~/.smartmemory
   ```

2. Use absolute paths in config
3. Check disk space

### Network Issues (Ontology Loading)

**Problem**: "Failed to load ontologies"

**Solutions**:
1. Enable offline mode:
   ```bash
   "env": {"SEMMEM_FORCE_OFFLINE": "true"}
   ```

2. Pre-cache ontologies:
   ```bash
   python -c "
   from semantic_memory.inference.ontology_loader import OntologyLoader
   loader = OntologyLoader()
   # Downloads and caches
   "
   ```

### Permission Denied

**Problem**: "PermissionError: [Errno 13]"

**Solutions**:
1. Make Python executable:
   ```bash
   chmod +x /path/to/venv/bin/python
   ```

2. Check file ownership:
   ```bash
   ls -la /path/to/knowledge_graph.ttl
   ```

---

## Testing Your Setup

### 1. Verify Server Starts

```bash
cd /path/to/SmartMemory
source venv/bin/activate
python -m semantic_memory.server
```

You should see: `INFO - Semantic Memory server startup complete`

Press Ctrl+C to stop.

### 2. Test via MCP Client

In Claude Desktop, Continue.dev, or your MCP client:

```
User: "Remember that Alice works at Google"
```

Expected: LLM should use the `add_memory` tool and confirm the information was saved.

### 3. Query the Memory

```
User: "What do you know about Alice?"
```

Expected: LLM should use `query_memory` or `search_entity` to retrieve the information.

### 4. Check Persistence

```bash
# After adding some memories, check the file
cat ~/.smartmemory/knowledge_graph.ttl
```

You should see RDF triples in Turtle format.

---

## Next Steps

- See [README.md](../README.md) for feature overview
- See [docs/realistic-dialog-scenario.md](realistic-dialog-scenario.md) for example usage
- See [user_rules/README.md](../user_rules/README.md) for custom rule examples
