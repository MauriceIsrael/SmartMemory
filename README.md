# Semantic Memory MCP Server

A Model Context Protocol (MCP) server that provides semantic memory capabilities using a Knowledge Graph. It allows AI agents to store, infer, and verify facts using a persistent RDF store.

## Features

- **Semantic Ingestion**: Convert natural language statements into RDF triples.
- **Inference Engine**: Automatically deduce new facts based on defined rules.
- **Verification Loop**: Request user verification for uncertain inferences.
- **Persistence**: Save and load the knowledge graph to/from a Turtle (`.ttl`) file.

## Installation

1.  **Prerequisites**: Python 3.11 or higher.
2.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd SmartMemory
    ```
3.  **Set up a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    # OR if using pyproject.toml
    pip install .
    ```

## Usage

### Running the Server

To start the server (currently runs as a background service):

```bash
python src/server.py
```

> **Important**: Ensure you are running this from the project root and using the virtual environment where dependencies are installed.
>
> If you encounter `ModuleNotFoundError: No module named 'src'`, use the virtual environment python directly:
> ```bash
> venv/bin/python src/server.py
> ```
> Or ensure your `PYTHONPATH` includes the project root:
> ```bash
> PYTHONPATH=. python src/server.py
> ```

### CLI Tools

You can interact with the knowledge graph using the provided CLI tools.

**Add a Fact**:
```bash
python src/cli/add_fact.py "Subject" "Predicate" "Object"
```
Example:
```bash
python src/cli/add_fact.py ":User" ":likes" ":Coding"
```

**Get Pending Verifications**:
```bash
python src/cli/get_pending_verifications.py
```

## Gemini Configuration

To use this MCP server with Gemini (or other MCP clients), you need to configure it in your MCP settings file (e.g., `~/.gemini/mcp_config.json` or project-specific config).

Add the following entry to the `mcpServers` object:

```json
{
  "mcpServers": {
    "semantic-memory": {
      "command": "/absolute/path/to/SmartMemory/venv/bin/python",
      "args": ["/absolute/path/to/SmartMemory/src/server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/SmartMemory"
      }
    }
  }
}
```

*Note: Replace `/absolute/path/to/SmartMemory` with the actual path to your project directory.*

## How It Works: Inference & Verification Workflow

SmartMemory uses an intelligent workflow to automatically deduce new facts from user input while maintaining accuracy through verification.

### The Complete Flow

```
User Input → add_fact → Storage → Inference Engine → Confidence Check → User Verification (if needed)
```

#### Step-by-Step Example

**1. User adds a fact in conversation**

When you interact with an AI agent using SmartMemory, you might say:
> "Alice knows Bob"

**2. The `add_fact` tool is called**

The MCP server receives the fact and stores it as an RDF triple:
```turtle
:Alice :knows :Bob .
```

**3. Inference engine runs in the background**

SmartMemory has pre-loaded ontologies (FOAF, SKOS, Schema.org) and inference rules. For example, FOAF defines that `:knows` is a symmetric property.

The inference engine executes SPARQL CONSTRUCT queries:
```sparql
CONSTRUCT { ?y :knows ?x }
WHERE { ?x :knows ?y }
```

**4. New facts are deduced**

The system infers:
```turtle
:Bob :knows :Alice .  # Symmetric relationship
```

**5. Confidence-based verification**

Each inferred fact has a confidence score:

- **High confidence (>0.8)**: Automatically added to the knowledge graph
  - Example: Symmetric properties from well-known ontologies
  
- **Medium/Low confidence (<0.8)**: **User verification requested**
  - The system asks in the conversation: 
    > "I noticed that Alice knows Bob. Should I also record that Bob knows Alice?"
  
- **User confirms or rejects**: 
  - ✅ Confirmed → Fact added to knowledge graph
  - ❌ Rejected → Fact discarded, system learns from feedback

**6. Knowledge graph grows intelligently**

Over time, the graph accumulates both:
- **Stated facts** (directly from user)
- **Inferred facts** (deduced by rules, verified by user)

### Real-World Example

```
User: "Alice works at Google"
  ↓
System stores: :Alice :worksAt :Google
  ↓
Inference rule: "If X works at Y, and Y is a Company, then X is an Employee"
  ↓
System infers: :Alice :isA :Employee (confidence: 0.6)
  ↓
System asks: "Based on Alice working at Google, should I record that Alice is an Employee?"
  ↓
User confirms: "Yes"
  ↓
System stores: :Alice :isA :Employee
```

### Benefits of This Approach

✅ **Trust but Verify**: System is proactive but not presumptuous  
✅ **Learning**: User feedback improves future confidence scores  
✅ **Transparency**: User always knows what's being inferred  
✅ **Accuracy**: Prevents false assumptions from polluting the knowledge graph

## Examples

### 1. Storing a User Preference

You can tell the system about a user's preference, and it will store it in the knowledge graph.

**Input**: "I like Python."  
**Action**: Call `add_fact` (or use the CLI).  
**Result**: Triple `(:User, :likes, :Python)` is added.

### 2. Checking Pending Verifications

If the system has inferred facts that need verification, you can check them:

```bash
python src/cli/get_pending_verifications.py
```

And the system might ask: "Is it true that User is a Developer?"

## Advanced Configuration

### Adding Inference Rules

Advanced users can define custom inference rules to extend the system's reasoning capabilities. Rules are currently defined programmatically in `src/server.py`.

1.  **Open `src/server.py`**.
2.  **Import `InferenceRule` and `Triple`**:
    ```python
    from src.models.inference_rule import InferenceRule
    from src.models.triple import Triple
    ```
3.  **Define your rules** before initializing the `InferenceEngine`.
    A rule consists of a name, a list of conditions (Triples with variables), and a conclusion (Triple with variables). Variables are strings starting with `?`.

    Example: "If X likes Science Fiction, then X is a SciFi Fan."

    ```python
    rule_scifi_fan = InferenceRule(
        name="scifi_fan_rule",
        conditions=[
            Triple(subject="?x", predicate=":likes", object=":ScienceFiction")
        ],
        conclusion=Triple(subject="?x", predicate=":isA", object=":SciFiFan")
    )
    ```

4.  **Pass the rules to the `InferenceEngine`**:
    ```python
    self.inference_engine = InferenceEngine(
        rules=[rule_scifi_fan], 
        verification_service=self.verification_service
    )
    ```

5.  **Restart the server** for changes to take effect.
