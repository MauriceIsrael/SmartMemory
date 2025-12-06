# Quick Start Guide

Get SmartMemory running in 5 minutes! Choose your mode below.

## 🚀 Fastest: MCP Mode (Conversational)

**For**: Chat with Claude Desktop or similar MCP clients

### Install

```bash
# Clone and install
git clone https://github.com/yourusername/SmartMemory.git
cd SmartMemory
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Configure Your MCP Client

**For Claude Desktop**, edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "smart-memory": {
      "command": "/path/to/SmartMemory/venv/bin/python",
      "args": ["-m", "smart_memory.server"],
      "env": {}
    }
  }
}
```

**For Gemini**, see [GEMINI.md](GEMINI.md)

### Start Chatting!

1. Restart your MCP client
2. Start a conversation
3. Try: *"Remember: I work at Acme Corp"*
4. Then: *"What company do I work for?"*

✅ Done! Your LLM now has persistent memory.

---

## 🐳 Docker Mode (Dashboard + Supervision)

**For**: Teams, document processing, rule visualization

### Prerequisites

- Docker installed
- Ollama running (if using local LLM) OR an API key for OpenAI/Anthropic

### One-Command Start

```bash
# With Local Ollama
docker run -p 8080:8080 \
  -e LLM_PROVIDER=ollama \
  -e LLM_MODEL=llama3 \
  -e LLM_BASE_URL=http://172.17.0.1:11434 \
  -v $(pwd)/brain:/app/data \
  smart-memory

# With OpenAI
docker run -p 8080:8080 \
  -e LLM_PROVIDER=openai \
  -e LLM_MODEL=gpt-4 \
  -e LLM_API_KEY=your-api-key \
  -v $(pwd)/brain:/app/data \
  smart-memory
```

**Note**: On Linux, use `172.17.0.1` for Ollama. On Mac/Windows, use `host.docker.internal`.

### Access Dashboard

Open `http://localhost:8080` in your browser.

### Upload Your First Document

1. Go to **Documents** page
2. Click **Upload**
3. Select a PDF (rules, policies, etc.)
4. Wait for rule extraction
5. Go to **Validation** to approve/reject extracted rules

✅ Done! Your knowledge graph is being built.

---

## 🛠️ Local Development (Dashboard)

**For**: Developers who want to modify the source

```bash
# Backend + Frontend
./scripts/start_dashboard.sh

# Access
# Dashboard: http://localhost:5173
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## Next Steps

- **Configure LLM**: [CONFIGURATION.md](CONFIGURATION.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Full Documentation**: [README.md](README.md)

## Common Issues

**"LLM connection failed"**: See [TROUBLESHOOTING.md#llm-connection-issues](TROUBLESHOOTING.md#llm-connection-issues)

**"Dashboard not loading"**: Check that port 8080 is available: `lsof -i :8080`

**"MCP server not responding"**: Verify path in MCP config matches your installation
