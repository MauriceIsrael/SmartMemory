# SmartMemory Quick Start Guide

Step-by-step walkthrough for getting started with SmartMemory semantic memory.

## 1. Installation (5 minutes)

```bash
# Navigate to where you want to install
cd ~/projects

# Clone the repository
git clone https://github.com/yourusername/SmartMemory.git
cd SmartMemory

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install
pip install -e .

# Verify installation
python -m semantic_memory.server
# Should show: "Semantic Memory server startup complete"
# Press Ctrl+C to stop
```

## 2. Configure Your LLM Client (2 minutes)

### Claude Desktop

```bash
# Open the config file
# macOS:
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
# Linux:
nano ~/.config/Claude/claude_desktop_config.json

# Add this (replace /path/to/SmartMemory with your actual path):
{
  "mcpServers": {
    "semantic-memory": {
      "command": "/path/to/SmartMemory/venv/bin/python",
      "args": ["-m", "semantic_memory.server"]
    }
  }
}

# Restart Claude Desktop
```

## 3. Test It Works

### In Claude Desktop

**You**: "Use semantic memory to remember that I live in San Francisco and work at Acme Corp."

**Claude should**:
- Use the `add_memory` tool
- Confirm the information was stored
- Show how many triples were added

**Expected Response**:
```
I've stored that information in your semantic memory:
- You live in San Francisco
- You work at Acme Corp

Total: 4 triples added (including inferred type information)
```

## 4. Basic Operations Tutorial

### A. Storing Information

**Natural Language (Easiest)**:
```
You: "I know Alice, and she works at Google."
```

SmartMemory will:
- Extract entities: `You`, `Alice`, `Google`
- Extract relationships: `knows`, `worksFor`
- Add type inference: `Alice` is a `Person`, `Google` is an `Organization`

**Explicit Triples (For Precision)**:
```
You: "Remember this triple: :Alice foaf:knows :Bob"
```

### B. Querying Information

**Simple Search**:
```
You: "Who do I know?"
```

Claude will use `query_memory` with:
```sparql
SELECT ?person WHERE { :You foaf:knows ?person }
```

**Complex Queries**:
```
You: "Find all people who work at the same company as Alice"
```

Claude will construct a SPARQL query:
```sparql
SELECT ?person ?company WHERE {
  :Alice schema:worksFor ?company .
  ?person schema:worksFor ?company .
  FILTER(?person != :Alice)
}
```

### C. Viewing Statistics

```
You: "How much do you know about me?"
```

Claude will use `get_graph_stats` and show:
- Total triples in graph
- Breakdown by source (user, inference, verified)
- Number of inference rules active
- Any conflicts detected

## 5. Advanced: Inference in Action

### Automatic Inference (Level 1: OWL-RL)

```
You: "I know Bob."
```

SmartMemory automatically infers:
- `Bob knows You` (because `foaf:knows` is symmetric)

No user action needed!

### Rule-Based Inference (Level 2: SPARQL)

```
You: "Alice works at Google. Bob works at Google."
```

SmartMemory MAY infer (depending on confidence):
- `Alice colleague Bob` (coworker rule)

If confidence < 0.85, you'll be asked:
```
"I've inferred that Alice and Bob might be colleagues since they 
work at the same company. Should I remember this?"
```

**You can**:
- Accept: "Yes, they work together"
- Reject: "No, they're in different departments"

## 6. Creating Custom Rules

### Scenario: Track Reading Habits

```
You: "Create a rule that if I read a book about a topic, 
I'm interested in that topic."
```

Claude will use `load_custom_rule`:

```sparql
PREFIX schema: <https://schema.org/>

CONSTRUCT {
    ?person schema:interest ?topic .
}
WHERE {
    ?book schema:reader ?person .
    ?book schema:about ?topic .
}
```

Now when you add:
```
You: "I read 'Clean Code' which is about software engineering."
```

SmartMemory automatically infers:
```
You are interested in software engineering.
```

## 7. Practical Use Cases

### Use Case 1: Personal CRM

```
# Add contacts
"I met Sarah at the AI conference in NYC. She's a researcher at MIT."

# Later query
"Who did I meet in NYC?"
"Find all researchers I know"
"What conferences have I attended?"
```

### Use Case 2: Project Knowledge Base

```
# Add project info
"Project Phoenix uses React and is deployed on AWS.
 Alice is the tech lead, Bob is working on the frontend."

# Later query
"What projects use React?"
"Who's working on which projects?"
"What's Alice working on?"
```

### Use Case 3: Learning Tracker

```
# Add learning activities
"I completed the Python course on Coursera.
 I'm reading 'Designing Data-Intensive Applications'."

# Later query
"What have I learned about Python?"
"What books am I reading?"
"What courses have I completed?"
```

## 8. Data Persistence

### Automatic Saving

SmartMemory **automatically saves** your knowledge graph when:
- The server shuts down gracefully
- Every time you add new information (configurable)

Default location: `~/.smartmemory/knowledge_graph.ttl`

### Manual Backup

```bash
# Copy your knowledge graph
cp ~/.smartmemory/knowledge_graph.ttl ~/backups/knowledge_$(date +%Y%m%d).ttl

# View it (it's human-readable!)
cat ~/.smartmemory/knowledge_graph.ttl
```

### Restoring Data

The knowledge graph automatically loads on server startup. Just ensure your config points to the right file:

```json
{
  "env": {
    "SEMMEM_PERSISTENCE_PATH": "/path/to/your/knowledge_graph.ttl"
  }
}
```

## 9. Viewing Your Knowledge Graph

### Option 1: Query Everything

```
You: "Show me everything you know."
```

### Option 2: Visualize (Coming Soon)

Export to formats for visualization tools:

```bash
# Export to GraphML for Gephi/Cytoscape
python -c "
from semantic_memory.knowledge.graph import ProvenanceGraph
g = ProvenanceGraph()
g.load_from_file('~/.smartmemory/knowledge_graph.ttl')
# Export logic here
"
```

### Option 3: SPARQL Debugging

```sparql
# Find all triples about you
SELECT ?p ?o WHERE { :You ?p ?o }

# Find all inferred triples
SELECT ?s ?p ?o ?rule WHERE {
  ?s ?p ?o .
  ?stmt rdf:subject ?s ; rdf:predicate ?p ; rdf:object ?o ;
        sem:source "sparql-rule" ;
        sem:sourceRule ?rule .
}

# Find pending verifications
SELECT ?s ?p ?o WHERE {
  GRAPH <urn:x-smartmem:pending> {
    ?s ?p ?o .
  }
}
```

## 10. Troubleshooting

### Server Not Showing Up in Claude

1. **Check the config file**:
   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Verify paths are absolute**:
   ```bash
   # Test the python path
   /absolute/path/to/SmartMemory/venv/bin/python --version
   ```

3. **Check server starts**:
   ```bash
   cd SmartMemory
   source venv/bin/activate
   python -m semantic_memory.server
   ```

4. **Restart Claude** (important!)

### Knowledge Not Persisting

Check the persistence file exists:
```bash
ls -lh ~/.smartmemory/knowledge_graph.ttl
```

If not, set it explicitly:
```json
{
  "env": {
    "SEMMEM_PERSISTENCE_PATH": "/Users/yourname/.smartmemory/knowledge_graph.ttl"
  }
}
```

### Ontology Loading Errors

Enable offline mode to use cached ontologies:
```json
{
  "env": {
    "SEMMEM_FORCE_OFFLINE": "true"
  }
}
```

## 11. Next Steps

- Read [`docs/realistic-dialog-scenario.md`](realistic-dialog-scenario.md) for an in-depth example
- Explore [`user_rules/README md`](../user_rules/README.md) to create custom inference rules
- Check [`docs/mcp-client-setup.md`](mcp-client-setup.md) for advanced configuration

## 12. Tips & Tricks

### Tip 1: Be Specific

❌ "Remember this about Alice"
✅ "Remember that Alice works at Google as a software engineer"

### Tip 2: Use Verification Wisely

Check what's waiting for verification:
```
"Show me any pending inferences that need my confirmation"
```

### Tip 3: Export & Share

Your knowledge graph is portable! Share it:
```bash
# Export
cp ~/.smartmemory/knowledge_graph.ttl shared_knowledge.ttl

# Import on another machine
cp shared_knowledge.ttl ~/.smartmemory/knowledge_graph.ttl
```

### Tip 4: Namespace Awareness

When querying, know your namespaces:
- Your entities: `http://semanticmemory.org/user#YourName`
- Schema.org: `https://schema.org/`
- FOAF: `http://xmlns.com/foaf/0.1/`

### Tip 5: Confidence Tuning

Adjust auto-accept threshold:
```json
{
  "env": {
    "SEMMEM_AUTO_ACCEPT_THRESHOLD": "0.90"  // More strict
  }
}
```

## Happy Remembering! 🧠✨
