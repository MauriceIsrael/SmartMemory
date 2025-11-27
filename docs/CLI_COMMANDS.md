# CLI Commands Reference

This document lists all available CLI commands for interacting with the SmartMemory system.

## Available Commands

### 1. Add a Fact

Add a new fact to the knowledge graph.

```bash
PYTHONPATH=. venv/bin/python src/cli/add_fact.py "<subject>" "<predicate>" "<object>"
```

**Example:**
```bash
PYTHONPATH=. venv/bin/python src/cli/add_fact.py ":Alice" ":knows" ":Bob"
```

**Output:**
```
✓ Fact added successfully
Subject: :Alice
Predicate: :knows
Object: :Bob
```

---

### 2. List Recent Facts

Display the most recent facts from the knowledge graph.

```bash
PYTHONPATH=. venv/bin/python src/cli/list_facts.py [OPTIONS]
```

**Options:**
- `-n, --count N` : Number of facts to display (default: 5)
- `--graph-file PATH` : Path to knowledge graph file (default: knowledge_graph.ttl)

**Examples:**
```bash
# Show last 5 facts (default)
PYTHONPATH=. venv/bin/python src/cli/list_facts.py

# Show last 10 facts
PYTHONPATH=. venv/bin/python src/cli/list_facts.py --count 10

# Show all facts
PYTHONPATH=. venv/bin/python src/cli/list_facts.py --count 1000
```

**Output:**
```
📊 Knowledge Graph Statistics
   Total facts: 2
   Showing: 2 most recent

Recent Facts:

[1] :User :likes :ChocolatePancakes
[2] :User :likes :SvelteJS
```

---

### 3. List Inference Rules

Display all configured inference rules.

```bash
PYTHONPATH=. venv/bin/python src/cli/list_rules.py [OPTIONS]
```

**Options:**
- `-v, --verbose` : Show detailed rule information including SPARQL queries

**Examples:**
```bash
# List rules (summary)
PYTHONPATH=. venv/bin/python src/cli/list_rules.py

# List rules with details
PYTHONPATH=. venv/bin/python src/cli/list_rules.py --verbose
```

**Output (when rules exist):**
```
📋 Inference Rules (2 total)

[1] symmetric_knows_rule
    Description: If X knows Y, then Y knows X

[2] developer_rule
    Description: If X likes Programming, then X is a Developer

💡 Use --verbose to see detailed rule information
```

---

### 4. Get Pending Verifications

List all facts awaiting user verification.

```bash
PYTHONPATH=. venv/bin/python src/cli/get_pending_verifications.py
```

**Output (no pending verifications):**
```
✓ No pending verifications.
The knowledge graph has no inferred facts awaiting user confirmation.
```

**Output (with pending verifications):**
```
Found 2 pending verification(s):

[1] {"id": "abc-123", "triple": {...}, "certainty_score": 0.7}

[2] {"id": "def-456", "triple": {...}, "certainty_score": 0.6}
```

---

### 5. Show Statistics

Display detailed statistics about the knowledge graph.

```bash
PYTHONPATH=. venv/bin/python src/cli/show_stat.py [OPTIONS]
```

**Options:**
- `--graph-file PATH` : Path to knowledge graph file (default: knowledge_graph.ttl)
- `-v, --verbose` : Show detailed statistics including predicate breakdown

**Examples:**
```bash
# Show basic statistics
PYTHONPATH=. venv/bin/python src/cli/show_stat.py

# Show detailed statistics with predicate breakdown
PYTHONPATH=. venv/bin/python src/cli/show_stat.py --verbose
```

**Output (basic):**
```
📊 Knowledge Graph Statistics

==================================================
  Total Facts (Triples):     42
==================================================
  Unique Subjects:           12
  Unique Predicates:         8
  Unique Objects:            18
  Unique Entities (S∪O):     25
==================================================
  URI References:            95
  Literals:                  15
  Blank Nodes:               0
==================================================

💡 Use --verbose to see detailed predicate breakdown
```

**Output (verbose):**
Shows the same statistics plus a breakdown of each predicate with counts, percentages, and visual bars.

---

## Quick Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `add_fact.py` | Add a fact | `add_fact.py ":Alice" ":knows" ":Bob"` |
| `list_facts.py` | Show recent facts | `list_facts.py --count 10` |
| `list_rules.py` | Show inference rules | `list_rules.py --verbose` |
| `get_pending_verifications.py` | Show pending verifications | `get_pending_verifications.py` |
| `show_stat.py` | Show graph statistics | `show_stat.py --verbose` |

## Logging

When facts trigger inference rules, you'll see detailed logs in the server output:

```
INFO - 🔍 Rule 'symmetric_knows_rule' triggered by 1 fact(s)
INFO -    ⚠️  Inferred (low confidence 0.70): :Bob :knows :Alice
INFO -    → Requesting user verification
INFO - 📊 Inference summary: 0 fact(s) added automatically, 1 pending verification(s)
```

**Log Levels:**
- `🔍` : Rule triggered
- `✓` : High confidence inference (auto-added)
- `⚠️` : Low confidence inference (needs verification)
- `→` : Action taken
- `📊` : Summary

## Tips

1. **Use aliases** for convenience:
   ```bash
   alias sm-add='PYTHONPATH=. venv/bin/python src/cli/add_fact.py'
   alias sm-list='PYTHONPATH=. venv/bin/python src/cli/list_facts.py'
   alias sm-rules='PYTHONPATH=. venv/bin/python src/cli/list_rules.py'
   alias sm-verify='PYTHONPATH=. venv/bin/python src/cli/get_pending_verifications.py'
   alias sm-stat='PYTHONPATH=. venv/bin/python src/cli/show_stat.py'
   ```

2. **Monitor server logs** to see inference in action:
   ```bash
   tail -f server.log
   ```

3. **Check graph statistics** regularly:
   ```bash
   PYTHONPATH=. venv/bin/python src/cli/list_facts.py --count 0
   ```
