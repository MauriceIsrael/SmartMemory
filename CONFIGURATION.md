# Configuration Guide

Complete reference for configuring SmartMemory.

## LLM Configuration

SmartMemory uses an LLM to extract business rules from documents. You can configure this in two ways:

### Method 1: Dashboard (Local Development)

**Best for**: Interactive configuration with immediate testing

1. Start the dashboard:
   ```bash
   ./scripts/start_dashboard.sh
   ```

2. Navigate to `http://localhost:5173` → **Admin** page

3. Fill in the LLM Configuration form:
   - **Provider**: Select your provider
   - **Model**: Enter model name
   - **API Key** (if cloud provider): Your API key
   - **Base URL** (if Ollama): Your Ollama server URL
   - **Temperature**: 0.0-2.0 (default: 0.7)

4. Click **Test Connection** to verify

5. Click **Save Configuration**

Configuration is saved to `llm_config.json` in the project root.

---

### Method 2: Environment Variables (Docker)

**Best for**: Production deployment, containers

Set these when running Docker:

```bash
docker run -p 8080:8080 \
  -e LLM_PROVIDER=ollama \
  -e LLM_MODEL=llama3 \
  -e LLM_BASE_URL=http://172.17.0.1:11434 \
  -e LLM_TEMPERATURE=0.7 \
  smart-memory
```

**Available Variables**:

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_PROVIDER` | Provider name | `ollama`, `openai`, `anthropic`, `google` |
| `LLM_MODEL` | Model name | `llama3`, `gpt-4`, `claude-3-5-sonnet` |
| `LLM_API_KEY` | API key (cloud providers) | `sk-proj-...` |
| `LLM_BASE_URL` | Base URL (Ollama/custom) | `http://172.17.0.1:11434` |
| `LLM_TEMPERATURE` | Temperature (optional) | `0.7` (default) |

---

## Supported LLM Providers

### Ollama (Local)

**Setup**:
1. Install Ollama: https://ollama.ai
2. Pull a model:
   ```bash
   ollama pull llama3
   # or
   ollama pull qwen2.5-coder  # Better for code/rules
   ```

**Configuration**:

**Dashboard**:
- Provider: `ollama`
- Model: `llama3` (or your model name)
- Base URL: `http://localhost:11434`

**Docker** (Linux):
```bash
docker run -e LLM_PROVIDER=ollama \
           -e LLM_MODEL=llama3 \
           -e LLM_BASE_URL=http://172.17.0.1:11434 \
           ...
```

**Docker** (Mac/Windows):
```bash
docker run -e LLM_PROVIDER=ollama \
           -e LLM_MODEL=llama3 \
           -e LLM_BASE_URL=http://host.docker.internal:11434 \
           ...
```

**Recommended Models**:
- `qwen2.5-coder`: Best for rule extraction
- `llama3`: Good general purpose
- `mistral`: Fast, decent quality

---

### OpenAI

**Setup**:
1. Get API key from https://platform.openai.com/api-keys

**Configuration**:

**Dashboard**:
- Provider: `openai`
- Model: `gpt-4` (or `gpt-3.5-turbo`, `gpt-4-turbo`)
- API Key: `sk-proj-...`

**Docker**:
```bash
docker run -e LLM_PROVIDER=openai \
           -e LLM_MODEL=gpt-4 \
           -e LLM_API_KEY='sk-proj-...' \
           ...
```

**Recommended Models**:
- `gpt-4`: Best quality, slower
- `gpt-4-turbo`: Good balance
- `gpt-3.5-turbo`: Fastest, cheaper

---

### Anthropic (Claude)

**Setup**:
1. Get API key from https://console.anthropic.com/

**Configuration**:

**Dashboard**:
- Provider: `anthropic`
- Model: `claude-3-5-sonnet-20241022`
- API Key: `sk-ant-...`

**Docker**:
```bash
docker run -e LLM_PROVIDER=anthropic \
           -e LLM_MODEL=claude-3-5-sonnet-20241022 \
           -e LLM_API_KEY='sk-ant-...' \
           ...
```

**Recommended Models**:
- `claude-3-5-sonnet-20241022`: Best for reasoning
- `claude-3-haiku-20240307`: Fastest, cheaper

---

### Google (Gemini)

**Setup**:
1. Get API key from https://makersuite.google.com/app/apikey

**Configuration**:

**Dashboard**:
- Provider: `google`
- Model: `gemini-1.5-pro`
- API Key: Your Google API key

**Docker**:
```bash
docker run -e LLM_PROVIDER=google \
           -e LLM_MODEL=gemini-1.5-pro \
           -e LLM_API_KEY='your-google-key' \
           ...
```

**Recommended Models**:
- `gemini-1.5-pro`: Best quality
- `gemini-1.5-flash`: Faster, cheaper

---

## Server Configuration

### Environment Variables

**Project Root**:
```bash
export SMART_MEMORY_ROOT=/path/to/your/data
```

**Knowledge Graph File**:
```bash
export KNOWLEDGE_GRAPH_FILE=/path/to/graph.ttl
```

### Configuration File

Located at `src/smart_memory/config.py`:

```python
class Config:
    # Project root (where data is stored)
    project_root: Path = Path.cwd()
    
    # Knowledge graph file
    knowledge_graph_file: Path = project_root / "knowledge_graph.ttl"
    
    # Rules directories
    default_rules_dir: Path = project_root / "src/rules/defaults"
    user_rules_dir: Path = project_root / "user_rules"
    rejected_rules_dir: Path = project_root / "rejected_rules"
    
    # OWL Reasoning (disabled by default for performance)
    owl_reasoning: bool = False
    
    # Ontology loading (disabled by default)
    load_ontologies: bool = False
```

---

## MCP Client Configuration

### Claude Desktop

**Config file location**:
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Configuration**:
```json
{
  "mcpServers": {
    "smart-memory": {
      "command": "/absolute/path/to/SmartMemory/venv/bin/python",
      "args": ["-m", "smart_memory.server"],
      "env": {}
    }
  }
}
```

**Important**: Use absolute paths!

---

### Gemini Desktop (Cline)

See [GEMINI.md](GEMINI.md) for complete setup instructions.

---

## Advanced Configuration

### Temperature Settings

Controls randomness in LLM responses:

- **0.0-0.3**: Deterministic, precise (good for rules)
- **0.4-0.7**: Balanced (default: 0.7)
- **0.8-1.5**: Creative, varied
- **1.6-2.0**: Very random (not recommended)

**For rule extraction**: Use 0.3-0.7

---

### Docker Networking

**Accessing host services from Docker**:

**Linux**:
- Use bridge IP: `172.17.0.1`
- Or use `--network host` mode

**Mac/Windows**:
- Use `host.docker.internal`

**Custom network**:
```bash
# Create network
docker network create smartmemory-net

# Run containers on it
docker run --network smartmemory-net ...
```

---

### Volume Mounting

**Persist knowledge graph**:
```bash
docker run -v $(pwd)/brain:/app/data smart-memory
```

**Custom paths**:
```bash
docker run -v /my/data:/app/data \
           -v /my/rules:/app/user_rules \
           smart-memory
```

---

## Troubleshooting

- **LLM not working**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#llm-connection-issues)
- **Dashboard connection errors**: Check proxy configuration in `vite.config.ts`
- **MCP not responding**: Verify paths and restart client

---

## Next Steps

- [Quick Start Guide](QUICKSTART.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Full Documentation](README.md)
