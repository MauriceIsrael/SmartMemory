# Bug Fix: get_pending_verifications Returns Empty Results

## Problem

**Symptom**: `add_memory` reports "4 inference(s) need verification" but `get_pending_verifications` returns "No pending verifications".

## Root Cause

In `src/semantic_memory/tools/add_memory.py` (line 220), the code was:

```python
uncertain_results = graph.query(uncertain_query)
if uncertain_results:
    response_text += f"\n\n⚠ {len(uncertain_results)} inference(s) need verification."
```

**Problem**: `graph.query()` returns a **generator** that can only be iterated once. Calling `len(uncertain_results)` **consumes** the generator, leaving no results for `get_pending_verifications` to retrieve.

## Solution

Convert the generator to a list before calling `len()`:

```python
uncertain_results = list(graph.query(uncertain_query))  # Convert to list
if uncertain_results:
    response_text += f"\n\n⚠ {len(uncertain_results)} inference(s) need verification."
```

## Fix Applied

✅ Modified `/home/momo/Antigravity/SmartMemory/src/semantic_memory/tools/add_memory.py` line 220

## Testing

After restarting the MCP server, `get_pending_verifications` should now correctly return the 4 pending verifications.

## About the "Bizarre" Inferences

The 4 inferences from "Pierre knows Denis" are likely:

1. **Symmetric inference**: Denis knows Pierre (from `social_symmetry.rq`)
2. **Additional inferences** from custom rules in `user_rules/`

The `user_rules/` directory contains:
- `uncertain_rule.rq` - Likely produces uncertain inferences
- `potential_collaboration.rq` - May infer collaboration relationships
- `test_rule.rq` - Test rule

To understand what was inferred, after the server restart, you can:

```bash
# View pending verifications
PYTHONPATH=. venv/bin/python src/cli/get_pending_verifications.py

# Or query the graph directly
PYTHONPATH=. venv/bin/python -c "
from rdflib import Graph
g = Graph()
g.parse('knowledge_graph.ttl', format='turtle')
results = g.query('''
    PREFIX sem: <http://semanticmemory.org/vocab#>
    SELECT ?s ?p ?o
    WHERE {
        ?stmt a rdf:Statement ;
              rdf:subject ?s ;
              rdf:predicate ?p ;
              rdf:object ?o ;
              sem:uncertain true .
    }
''')
for r in results:
    print(f'{r[0]} {r[1]} {r[2]}')
"
```

## Next Steps

1. **Restart the MCP server** to apply the fix
2. **Re-test** by adding a memory and checking `get_pending_verifications`
3. **Review custom rules** in `user_rules/` to understand what's being inferred
4. **Disable uncertain rules** if needed by moving them out of `user_rules/`
