# Getting Started with SmartMemory

## What is SmartMemory?

SmartMemory is a **neuro-symbolic AI system** that combines:
- 🧠 **LLM flexibility** (natural language understanding)
- ⚡ **Formal reasoning** (SPARQL rules, provenance, guarantees)
- 🤝 **Human-in-the-loop** (approve/reject inferences)

**Use cases**: Compliance systems, knowledge bases, access control, business rules

---

## Quick Installation

```bash
# 1. Clone and setup
git clone <your-repo-url>
cd SmartMemory
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install
pip install -e .

# 3. Test it works
python examples/quick_demo.py
```

**Expected output**:
```
🧠 SmartMemory v0.1 - Quick Demo
✓ Loaded 5 inference rules
...
✓ Alice and Bob are colleagues
✨ Demo complete!
```

---

## Using with MCP Clients

### Option 1: Claude Desktop (Recommended)

**Edit config** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

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

**Restart Claude Desktop**, then try:
```
You: "Remember that Alice works at Google"
Claude: [uses add_memory tool]
  ✓ Added 1 triple. Inferred 0 additional facts.

You: "Bob also works at Google"
Claude: [uses add_memory tool]
  ✓ Added 1 triple. Inferred 1 fact:
    • Alice might be colleagues with Bob (confidence: 0.75)
    → Needs verification

You: "Yes, they work together"
Claude: [uses verify_inference tool]
  ✓ Inference accepted.
```

### Option 2: Gemini Desktop

Similar config in `~/.gemini/mcp_server_config.json`.

---

## Core Concepts

### 1. **Facts with Provenance**

Every fact has metadata:
```turtle
:Alice schema:colleague :Bob .

# Attached metadata (invisible to queries)
_:stmt rdf:subject :Alice ;
       sem:source "user-verified" ;
       sem:confidence 1.0 ;
       sem:timestamp "2025-12-02T20:00:00Z" .
```

### 2. **SPARQL Inference Rules**

Example: `src/rules/defaults/coworkers_inference.rq`
```sparql
CONSTRUCT {
    ?person1 schema:colleague ?person2 .
}
WHERE {
    ?person1 schema:worksFor ?org .
    ?person2 schema:worksFor ?org .
    FILTER(?person1 != ?person2)
}
```

### 3. **Confidence Threshold**

- **≥ 0.9**: Auto-accepted
- **< 0.9**: Requires user verification

---

## What Can You Build?

### Example: Access Control System

```python
# Rule: Admins can delete
CONSTRUCT { ?user :canDelete ?resource }
WHERE { ?user rdf:type :Admin }

# Rule: Owners can modify
CONSTRUCT { ?user :canModify ?resource }
WHERE { ?resource :ownedBy ?user }

# Query: Can Alice delete document X?
ASK { :Alice :canDelete :DocumentX }
```

**Result**: Formal proof with audit trail (who, when, which rule)

---

## Next Steps

1. **Read**: [Neuro-Symbolic Concept](neuro-symbolic.md)
2. **Create**: Custom rules in `user_rules/`
3. **Explore**: MCP tools reference

---

## Troubleshooting

**Server won't start**:
```bash
# Test manually
/path/to/venv/bin/python -m semantic_memory.server
```

**No tools showing**:
1. Restart MCP client completely
2. Check config file syntax
3. Verify absolute paths

**Need help?**: Open an issue on GitHub
