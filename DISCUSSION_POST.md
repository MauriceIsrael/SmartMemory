# 🧠 Seeking Feedback from Neuro-Symbolic AI Researchers

## Overview

**SmartMemory** is an experimental implementation of a neuro-symbolic architecture that bridges Large Language Models (LLMs) with symbolic reasoning through knowledge graphs and SPARQL-based inference rules.

The core idea: **Give LLMs structured memory** by combining:
- **Neural** (LLM): Natural language understanding, entity extraction, rule discovery
- **Symbolic** (RDF/SPARQL): Verified knowledge graph, logical inference, rule-based deduction

## What Makes This Interesting?

1. **Bidirectional Learning Loop**:
   - LLM extracts facts and proposes inference rules from conversations/documents
   - Human expert validates rules before they become "laws" in the knowledge graph
   - Symbolic reasoner applies validated rules to deduce new facts
   - LLM queries results via SPARQL to answer questions with logical certainty

2. **MCP Integration**: 
   - Designed as a Model Context Protocol (MCP) server
   - Works with Claude Desktop, Gemini, and other MCP clients
   - Persistent memory across conversations

3. **Real-World Rule Extraction**:
   - Upload PDFs (policies, regulations, game rules)
   - LLM extracts SPARQL `CONSTRUCT` rules
   - Dashboard for bulk rule validation
   - Knowledge graph grows organically from documents

## Current Architecture

```
User Input → LLM (extract entities/rules) → Pending Validation
                                                    ↓
                                            Human Approval
                                                    ↓
RDF Knowledge Graph ← SPARQL Inference Engine ← Validated Rules
         ↓
   Query Results → LLM (natural language answers)
```

**Tech Stack**: Python, RDFLib, SPARQL, FastAPI, SvelteKit, litellm

## Research Questions & Open Problems

We'd love input from the neuro-symbolic AI community on:

### 1. **Rule Quality & Generalization**
- How can we improve LLM-generated SPARQL rule quality?
- Best practices for preventing overfitting to specific examples?
- Metrics for rule "goodness" beyond unit tests?

### 2. **Scalability**
- Currently ~5K triples, 50 rules perform well
- What bottlenecks should we expect at 100K+ triples?
- Incremental reasoning vs. full materialization trade-offs?

### 3. **Hybrid Reasoning Strategies**
- When to use symbolic reasoning vs. LLM prompting?
- How to handle uncertainty and contradictions?
- Combining OWL-RL reasoning with custom SPARQL rules?

### 4. **Rule Learning**
- Active learning strategies for rule proposal?
- Can we automatically learn rule confidence scores?
- Techniques for rule refinement based on feedback?

### 5. **Evaluation**
- How to benchmark neuro-symbolic systems like this?
- Existing datasets for knowledge graph + rule learning?
- Metrics beyond accuracy (explainability, trust, auditability)?

## What We're NOT (Yet)

- ❌ Production-ready (proof of concept only)
- ❌ Handling contradictions robustly
- ❌ Advanced provenance tracking
- ❌ Automated rule conflict resolution

## Call for Collaboration

**We're particularly interested in**:
- 📚 **Pointers to relevant papers** (rule learning, neuro-symbolic architectures, KG reasoning)
- 🔬 **Experimental ideas** to validate or improve the approach
- 🐛 **Fundamental flaws** we might have overlooked
- 🤝 **Collaboration opportunities** for research projects

**Use Cases to Explore**:
- Legal/regulatory compliance checking
- Medical protocol verification
- Game rule enforcement
- Business logic extraction from documents

## Try It Out

**From MCP Registry** (Easiest):
```json
// Add to your Claude Desktop config
{
  "mcpServers": {
    "smart-memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-smart-memory"]
    }
  }
}
```

**From Source** (For Development):
```bash
git clone https://github.com/yourusername/SmartMemory
cd SmartMemory
./scripts/start_dashboard.sh
# Or use Docker for one-liner deployment
```

See [QUICKSTART.md](../QUICKSTART.md) for details.

## Questions for Discussion

1. **Architecture**: Is the validation-in-the-loop approach the right trade-off between automation and correctness?

2. **Symbolic Representation**: Should we support more expressive logics (e.g., Datalog, ASP) or stick with SPARQL for simplicity?

3. **LLM Integration**: How can we better leverage modern LLMs (function calling, structured outputs) for rule extraction?

4. **Evaluation**: What benchmarks or test suites would be most valuable for systems like this?

5. **Real-World Deployment**: What are the biggest barriers to deploying neuro-symbolic systems in practice?

## Your Input Matters!

Whether you're a veteran in knowledge representation or new to neuro-symbolic AI, we'd love to hear your thoughts. This is a learning project, and we're eager to understand what works, what doesn't, and where the field is heading.

**Comment below or open an issue!** 🚀

---

**Relevant Links**:
- 📖 [Full Documentation](../README.md)
- 🏗️ [Architecture Details](../docs/)
- 💬 [Discussions](../../discussions)
- 🐛 [Issues](../../issues)
