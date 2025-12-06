# French Language Support Added - 2025-11-26

## Problem Fixed

**Issue**: When users said "Bastien travaille chez Cap", the system stored it as:
```
<random-node> rdfs:comment "Bastien travaille chez Cap"
```

Instead of structured data:
```
<Bastien> schema:worksFor <Cap>
```

This is why queries looking for `schema:worksFor` returned 0 results.

## Solution

Added French language patterns to `TripleExtractor`:

### New Patterns:

1. **Work relationships** (French):
   - `travaille chez` / `travaille à`
   - `bosse chez` / `bosse à`  
   - `est employé par` / `est employée par`
   
   → Creates: `<Person> schema:worksFor <Company>`

2. **Social relationships** (French):
   - `connaît` / `connait`
   - `est ami avec` / `est amie avec`
   
   → Creates: `<Person1> foaf:knows <Person2>`

3. **Type/classification** (French):
   - `est un` / `est une`
   
   → Creates: `<Entity> rdf:type <Type>`

4. **Location** (French):
   - `est à` / `est en`
   - `se trouve à` / `se trouve en`
   
   → Creates: `<Entity> schema:location <Place>`

5. **Events** (French):
   - `a assisté à`
   - `est allé à` / `est allée à`
   - `a participé à`
   
   → Creates: `<Person> schema:attendee <Event>`

6. **Creation** (French):
   - `a créé` / `a écrit` / `a fait`
   
   → Creates: `<Creator> schema:creator <Work>`

7. **Topics** (French):
   - `parle de` / `traite de` / `concerne`
   
   → Creates: `<Work> schema:about <Topic>`

## Test Results

✅ All patterns working correctly:

```
"Bastien travaille chez Cap"
→ <Bastien> schema:worksFor <Cap> (confidence: 0.9)

"Dirk bosse à Cap"  
→ <Dirk> schema:worksFor <Cap> (confidence: 0.9)

"Alice connaît Bob"
→ <Alice> foaf:knows <Bob> (confidence: 0.9)

"Charlie est un ingénieur"
→ <Charlie> rdf:type <ingénieur> (confidence: 0.85)
```

## Next Steps

1. **Restart Gemini** to load the new code
2. **Clear old data** (optional - the old rdfs:comment triples are still in the graph)
3. **Re-add the facts**: 
   - "Bastien travaille chez Cap"
   - "Dirk travaille à Cap"
4. **Query**: "Qui travaille chez Cap?" should now work!

## Files Modified

- `src/semantic_memory/nlp/triple_extractor.py` - Added French patterns

Cache cleared, ready to test!
