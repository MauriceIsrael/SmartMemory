# SmartMemory

**Neuro-Symbolic AI** | Blend LLM flexibility with formal reasoning guarantees

<p align="center">
  <em>Convert conversations into verified knowledge graphs with SPARQL inference rules</em>
</p>

---

## 🎯 What is SmartMemory?

A **Model Context Protocol (MCP) server** that lets AI assistants (Claude, Gemini) build **formal knowledge graphs** from natural language conversations, with:

- ✅ **Provenance tracking**: Every fact has source, confidence, timestamp
- ✅ **SPARQL inference rules**: Automatic deductions with formal guarantees  
- ✅ **Human-in-the-loop**: Approve/reject uncertain inferences
- ✅ **Collaborative rule creation**: LLM proposes, you validate, system enforces

**Perfect for**: Compliance systems, access control, business rules, knowledge bases

---

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/yourusername/SmartMemory
cd SmartMemory
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

### 2. Test Standalone

```bash
python examples/quick_demo.py
```

Expected output:
```
🧠 SmartMemory v0.1 - Quick Demo

✓ Knowledge graph initialized with 5 default rules

Step 1: Adding facts
--------------------------------------------------
  ✓ Alice knows Bob
  ✓ Alice works at Google
  ✓ Bob works at Google

Triples in graph: 27

Step 2: Querying the graph
--------------------------------------------------
Query: Who works at Google?
  ✓ :Alice
  ✓ :Bob

Query: Who does Alice know?
  ✓ :Bob

✨ Demo complete!

What SmartMemory adds:
  ✓ Provenance tracking (who added, when, confidence)
  ✓ SPARQL inference rules (automatic deductions)
  ✓ Human-in-the-loop (approve/reject uncertain facts)
  ✓ MCP integration (use with Claude, Gemini, etc.)

Step 3: Conversational Rule Learning (The 'Magic' Part)
--------------------------------------------------
Scenario: User teaches the system a new business rule.

1. User says: 'Driving a car requires a license'
   LLM analyzes this and proposes a SPARQL rule...
   → Proposed Rule 'driving_requires_license':
     IF ?person uses :Car THEN ?person requires :DrivingLicense

2. User approves the rule via approve_rule('driving_requires_license')
   ✓ Rule activated and added to engine

3. User says: 'Charlie drives to work'
   ✓ Added fact: Charlie uses Car

4. System automatically infers consequences...
   ✓ Inference engine finished (inferred 4 new triples)
   ✨ INFERENCE CONFIRMED: Charlie requires DrivingLicense

Next steps:
  • See docs/getting-started.md for MCP setup
  • Try with Claude Desktop or Gemini
  • Create custom rules in user_rules/
```

### 3. Use with MCP Clients

**Claude Desktop**: Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `~/.config/Claude/claude_desktop_config.json` (Linux):

```json
{
  "mcpServers": {
    "smartmemory": {
      "command": "/absolute/path/to/SmartMemory/venv/bin/python",
      "args": ["-m", "semantic_memory.server"]
    }
  }
}
```

**Restart Claude**, then:
```
You: "Remember that Alice works at Google"
Claude: [uses add_memory]
  ✓ Added 1 triple to knowledge graph

You: "Bob also works there"  
Claude: [uses add_memory + inference]
  ✓ Added 1 triple
  ⚠️  Inferred: Alice might be colleagues with Bob (confidence: 0.75)
  → Requires verification

You: "Yes, they work together"
Claude: [uses verify_inference]
  ✓ Inference accepted and formalized
```

**See [docs/getting-started.md](docs/getting-started.md) for setup and more examples.**

### 4. Visualization Dashboard

SmartMemory comes with a built-in dashboard to visualize the knowledge graph and manage the system.

**Quick Start** (one command):
```bash
# From the SmartMemory root directory
./scripts/start_dashboard.sh
```

This starts both the backend (FastAPI) and frontend (SvelteKit) in parallel. The dashboard will automatically open in your browser at `http://localhost:5173`.

**What you get**:
- 📊 Real-time knowledge graph statistics
- 📋 Browse and search facts
- ⚙️ Manage inference rules
- 🔄 **Auto-refresh**: Dashboard automatically reloads data to show changes made during LLM conversations

**Manual Setup** (if you prefer separate terminals):

<details>
<summary>Click to expand manual setup instructions</summary>

**Install supervision dependencies** (first time only):
```bash
# From the SmartMemory root directory
source venv/bin/activate
pip install fastapi "uvicorn[standard]"
# Or install via optional dependencies:
# pip install -e ".[supervision]"
```

**Backend (FastAPI)**:
```bash
cd src/supervision_backend
# Ensure PYTHONPATH includes project root
export PYTHONPATH=$PYTHONPATH:$(pwd)/../..
# Use the venv's uvicorn (not the system one)
../../venv/bin/uvicorn main:app --reload --port 8000
```

**Frontend (SvelteKit)**:
```bash
cd src/supervision_frontend
npm install
npm run dev -- --open
```

</details>

Access the dashboard at `http://localhost:5173`.

---

## 💡 Key Feature: Conversational Rule Learning

SmartMemory lets LLMs **extract business rules** from conversation and formalize them:

```
You: "Driving a car requires a license"
LLM: [proposes SPARQL rule with preview]
  Rule: driving_requires_license
  Preview: Would infer "Bob needs license" (he drives)
  
You: approve_rule('driving_requires_license')
LLM: ✓ Rule activated

You: "Charlie also drives to work"  
LLM: [automatic inference]
  ✓ Charlie now requires license (inferred by rule)
```

Real conversation example from development: [See full scenario](docs/realistic-dialog-scenario.md)

---

## 🧠 Architecture

```
┌─────────────────┐
│   LLM (Gemini)  │  ← Natural language
│    Claude, etc. │     understanding
└────────┬────────┘
         │ MCP Protocol
         ▼
┌─────────────────────────────────────┐
│   SmartMemory Server                │
│  ┌──────────────┐  ┌─────────────┐ │
│  │ 12 MCP Tools │  │ Rule Engine │ │
│  │ - add_memory │  │ - SPARQL    │ │
│  │ - verify     │  │ - Inference │ │
│  │ - suggest    │  │ - Provenance│ │
│  └──────────────┘  └─────────────┘ │
└────────┬───────────────────────────┘
         │
         ▼
  ┌──────────────┐
  │ RDF Knowledge│  ← Persistent, auditable
  │     Graph    │     formal reasoning
  └──────────────┘
```

**Tech Stack**: Python 3.11+, RDFLib, OWL-RL (optional), MCP SDK, SvelteKit, TypeScript, TailwindCSS

> **Note**: Full ontology loading (FOAF, Schema.org) is **disabled by default** to ensure fast startup times (<2s). You can enable it in `config.py` if you need deep reasoning capabilities, at the cost of slower startup (~5-10s).

---

## 📚 Documentation

- **[Getting Started](docs/getting-started.md)**: Installation & first steps
- **[MCP Tools Reference](docs/getting-started.md#tools-overview)**: Available tools
- **[Custom Rules Guide](docs/CUSTOM_RULES.md)**: Write SPARQL inference rules
- **[Architecture Deep Dive](docs/architecture-overview.md)**: Design decisions

---

## 🔬 Research Context

SmartMemory implements **neuro-symbolic AI** concepts:
- **Neural** (LLM): Flexibility, natural language, learning
- **Symbolic** (SPARQL/RDF): Formal guarantees, provenance, auditability

**Relevant research areas**:
- Knowledge distillation from neural networks
- Explainable AI (XAI) by design
- Human-in-the-loop machine learning

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines  
- How to submit PRs

---

## 📜 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

Built with ❤️ using:
- [RDFLib](https://rdflib.readthedocs.io/) - RDF processing
- [Model Context Protocol](https://modelcontextprotocol.io/) - LLM integration
- W3C Semantic Web standards (SPARQL, OWL, RDF)

---

**Questions?** Open an issue or discussion on GitHub

**Built by**: SmartMemory Contributors | **Version**: 0.1.0
