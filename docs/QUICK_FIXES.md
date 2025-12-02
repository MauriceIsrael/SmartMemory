# Quick Fixes for Slow Startup

## Applied

1. ✅ Fixed file:// URL loading in ontology_loader.py
2. 🔄 Adding config option to disable OWL-RL temporarily

## To Disable OWL-RL Temporarily

Add this to your ~/.gemini/settings.json or set as env var:

```json
{
  "mcpServers": {
    "semantic-memory": {
      ...
      "env": {
        "SEMMEM_ENABLE_OWL_REASONING": "false",  // ← ADD THIS
        "SEMMEM_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

Or just for one test:
```bash
export SEMMEM_ENABLE_OWL_REASONING=false
python -m semantic_memory.server
```

## Why OWL-RL is Slow

The reasoning engine is processing 245k triples and computing the deductive closure,
which can take minutes on a large ontology graph.

For development/testing, you can disable it. For production, we need to:
- Optimize the reasoning
- Or only load lightweight ontologies
- Or reason only on user data, not the full ontology
