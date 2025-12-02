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
✓ Knowledge graph initialized
✓ Alice knows Bob
✓ Alice works at Google
Query: Who works at Google?
  ✓ :Alice
  ✓ :Bob
✨ Demo complete!
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

**See [docs/getting-started.md](docs/getting-started.md) for Gemini setup and more examples.**

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

Real conversation example from development: [See full scenario](docs/example-scenario.md)

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

**Tech Stack**: Python 3.11+, RDFLib, OWL-RL, MCP SDK

---

## 📚 Documentation

- **[Getting Started](docs/getting-started.md)**: Installation & first steps
- **[MCP Tools Reference](docs/mcp-tools.md)**: All 12 available tools
- **[Custom Rules Guide](docs/custom-rules.md)**: Write SPARQL inference rules
- **[Architecture Deep Dive](docs/architecture.md)**: Design decisions

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
