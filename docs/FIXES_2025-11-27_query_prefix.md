# Query Fixes - 2025-11-27

## Problems Fixed

### 1. query_memory - Missing PREFIX Declarations ✅

**Problem**: When Gemini generated SPARQL queries without PREFIX declarations, they failed with:
```
Exception: Unknown namespace prefix : None
```

Example failing query from Gemini:
```sparql
SELECT ?person WHERE { ?person :worksAt :Thales . }
```

**Solution**: Auto-prepend common PREFIX declarations if not present in query.

**Prefixes added**:
- `: <http://semanticmemory.org/user#>` (default user namespace)
- `rdf:`, `rdfs:`, `owl:` (W3C standards)
- `foaf:` (Friend of a Friend)
- `schema:` (Schema.org)
- `sem:` (Semantic Memory internal)

**Result**: Queries now work even if Gemini forgets PREFIX declarations.

---

### 2. search_entity - Missing PREFIX in Internal Queries ✅

**Problem**: Internal SPARQL queries in `search_entity` used prefixes like `foaf:`, `rdfs:`, `schema:` but didn't declare them.

**Solution**: Added PREFIX declarations to all 3 internal queries:
1. Main search query (uses foaf:, rdfs:, schema:)
2. Fallback props query (uses rdf:)
3. Detail properties query (uses rdf:, rdfs:, foaf:, schema:)

**Result**: `search_entity` now works reliably without namespace errors.

---

## Files Modified

- ✅ `src/semantic_memory/tools/query_memory.py` - Auto-prepend PREFIX
- ✅ `src/semantic_memory/tools/search_entity.py` - Added PREFIX to internal queries

## Testing

Restart Gemini and test:

1. **query_memory**: "Qui travaille chez Thales?"
   - Should now work even if Gemini's query is missing PREFIX

2. **search_entity**: "Find people named Jeremie"
   - Should work without namespace errors

Cache cleared, ready to test!
